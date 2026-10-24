// IndexedDB Storage Adapter for Ages of Dominion Reborn
// Conforms to A05 specification: atomic transaction commits, epoch advancement, CAS head comparison,
// multi-slot storage, backup preservation, and complete migration from localStorage.

import { checksum, decode, encode, SAVE_KEY, VIEW_KEY } from './save.js';

function campaignIdentity(state) {
  if (state?.id) return String(state.id);
  return `campaign-${state?.seed ?? 'unknown'}`;
}

function payloadRevision(encoded) {
  try { return JSON.parse(JSON.parse(encoded).payload).revision; }
  catch { return null; }
}

function headsMatch(current, expected) {
  return Boolean(current && expected)
    && current.epoch === expected.epoch
    && current.revision === expected.revision
    && current.campaignId === expected.campaignId
    && current.checksum === expected.checksum;
}

function casAllows(current, expected) {
  if (!expected) return !current;
  return headsMatch(current, expected);
}

function assertCandidate(current, candidate, replace = false) {
  if (!replace && current && (campaignIdentity(candidate) !== current.campaignId || candidate.revision < current.revision)) {
    throw new Error('Refuse stale save revision or changed campaign identity');
  }
}
function preservePrevious(store, raw, data, currentHead) {
  if (raw == null) return;
  try {
    const state = decode(raw, data);
    if (currentHead !== undefined && !headsMatch(currentHead, headFor(state, raw, currentHead?.epoch))) {
      throw new Error('Save head does not match campaign bytes');
    }
    store.put(raw, 'backup');
  } catch {
    // Never replace a valid backup with damaged bytes.
    store.put(raw, `damaged:${checksum(raw)}`);
  }
}

function headFor(state, encoded, epoch, extra = {}) {
  const payload = JSON.parse(encoded).payload;
  return {
    epoch,
    campaignId: campaignIdentity(state),
    revision: state.revision,
    checksum: checksum(payload),
    updatedAt: Date.now(),
    ...extra,
  };
}

export const DB_NAME = 'aod-reborn-db';
export const DB_VERSION = 1;
export const STORE_HEAD = 'heads';
export const STORE_CAMPAIGNS = 'campaigns';
export const STORE_SLOTS = 'slots';
export const STORE_META = 'metadata';

/**
 * Creates an in-memory or browser-backed IndexedDB storage adapter.
 * Supports environment abstraction for both Node.js tests and browser runtime.
 */
export class IndexedDBStorageAdapter {
  constructor(dbFactory = typeof indexedDB !== 'undefined' ? indexedDB : null, dbName = DB_NAME) {
    this.dbFactory = dbFactory;
    this.dbName = dbName;
    this.db = null;
    this.memoryDb = {
      heads: new Map(),
      campaigns: new Map(),
      slots: new Map(),
      metadata: new Map(),
    };
    this.epoch = 1;
    this.opening = null;
  }

  async open() {
    if (this.db) return this.db;
    if (!this.dbFactory) {
      // Use transactional in-memory simulation in environments without native IndexedDB
      return this;
    }

    if (this.opening) return this.opening;
    this.opening = new Promise((resolve, reject) => {
      let blocked = false;
      const request = this.dbFactory.open(this.dbName, DB_VERSION);
      request.onupgradeneeded = event => {
        const db = event.target.result;
        if (!db.objectStoreNames.contains(STORE_HEAD)) db.createObjectStore(STORE_HEAD);
        if (!db.objectStoreNames.contains(STORE_CAMPAIGNS)) db.createObjectStore(STORE_CAMPAIGNS);
        if (!db.objectStoreNames.contains(STORE_SLOTS)) db.createObjectStore(STORE_SLOTS);
        if (!db.objectStoreNames.contains(STORE_META)) db.createObjectStore(STORE_META);
      };
      request.onsuccess = event => {
        if (blocked) { event.target.result.close(); return; }
        this.db = event.target.result;
        this.db.onversionchange = () => { this.db?.close(); this.db = null; };
        this.db.onclose = () => { this.db = null; };
        resolve(this.db);
      };
      request.onerror = event => reject(new Error('IndexedDB open failed: ' + event.target.error));
      request.onblocked = () => { blocked = true; reject(new Error('IndexedDB open blocked by another game window')); };
    }).finally(() => { this.opening = null; });
    return this.opening;
  }

  writeTransaction(stores) {
    try { return this.db.transaction(stores, 'readwrite', { durability: 'strict' }); }
    catch (error) {
      if (!(error instanceof TypeError)) throw error;
      return this.db.transaction(stores, 'readwrite');
    }
  }

  /**
   * Loads current live campaign with head metadata and backup status.
   */
  async loadLive(data) {
    await this.open();
    if (!this.db) {
      const head = this.memoryDb.heads.get('live') ?? null;
      const live = this.memoryDb.campaigns.get('live') ?? null;
      const backupRaw = this.memoryDb.campaigns.get('backup') ?? null;
      let backup = null;
      if (backupRaw) {
        try { backup = decode(backupRaw, data); } catch { /* Ignore corrupted backup */ }
      }
      if (!live) return { status: 'EMPTY', head: null, state: null, backup };
      try {
        const state = decode(live, data);
        if (!headsMatch(head, headFor(state, live, head?.epoch))) throw new Error('Save head does not match campaign bytes');
        return { status: 'VALID', head, state, backup };
      } catch (err) {
        return { status: 'DAMAGED', error: err.message, head, state: null, backup, raw: live };
      }
    }

    return new Promise((resolve, reject) => {
      const tx = this.db.transaction([STORE_HEAD, STORE_CAMPAIGNS, STORE_META], 'readonly');
      const metaReq = tx.objectStore(STORE_META).get('live-view');
      const headReq = tx.objectStore(STORE_HEAD).get('live');
      const liveReq = tx.objectStore(STORE_CAMPAIGNS).get('live');
      const backupReq = tx.objectStore(STORE_CAMPAIGNS).get('backup');
      tx.oncomplete = () => {
        const head = headReq.result ?? null;
        const live = liveReq.result ?? null;
        const backupRaw = backupReq.result ?? null;
        let backup = null;
        if (backupRaw) {
          try { backup = decode(backupRaw, data); } catch { /* Ignore */ }
        }
        if (!live) return resolve({ status: 'EMPTY', head: null, state: null, backup });
        try {
          const state = decode(live, data);
          const expected = headFor(state, live, head?.epoch);
          if (!headsMatch(head, expected)) throw new Error('Save head does not match campaign bytes');
          resolve({ status: 'VALID', head, state, backup, view: metaReq.result });
        } catch (err) {
          resolve({ status: 'DAMAGED', error: err.message, head, state: null, backup, raw: live });
        }
      };
      tx.onabort = tx.onerror = () => reject(new Error('loadLive failed: ' + tx.error));
    });
  }

  /**
   * Commits an autosave or command mutation with atomic CAS (expectedHead).
   */
  async commit(expectedHead, encodedCandidate, data, view = 'kingdom') {
    const candidateState = decode(encodedCandidate, data);

    await this.open();
    if (!this.db) {
      const currentHead = this.memoryDb.heads.get('live');
      if (!casAllows(currentHead, expectedHead)) {
        throw new Error('CAS head mismatch: expected revision ' + expectedHead?.revision + ' but found ' + currentHead?.revision);
      }
      assertCandidate(currentHead, candidateState);
      const previousLive = this.memoryDb.campaigns.get('live');
      if (previousLive) preservePrevious({ put: (value, key) => this.memoryDb.campaigns.set(key, value) }, previousLive, data, currentHead);
      const newHead = headFor(candidateState, encodedCandidate, currentHead?.epoch || 1);
      this.memoryDb.campaigns.set('live', encodedCandidate);
      this.memoryDb.heads.set('live', newHead);
      this.epoch = newHead.epoch;
      return newHead;
    }

    return new Promise((resolve, reject) => {
      const tx = this.writeTransaction([STORE_HEAD, STORE_CAMPAIGNS, STORE_META]);
      const headStore = tx.objectStore(STORE_HEAD);
      const campStore = tx.objectStore(STORE_CAMPAIGNS);

      const headReq = headStore.get('live');
      let written = null;
      let candidateError = null;
      headReq.onsuccess = () => {
        const currentHead = headReq.result;
        if (!casAllows(currentHead, expectedHead)) {
          try { tx.abort(); } catch { /* The abort handler rejects. */ }
          return;
        }
        try { assertCandidate(currentHead, candidateState); }
        catch (error) { candidateError = error; tx.abort(); return; }
        const liveReq = campStore.get('live');
        liveReq.onsuccess = () => {
          preservePrevious(campStore, liveReq.result, data, currentHead);
          const newHead = headFor(candidateState, encodedCandidate, currentHead?.epoch || 1);
          written = newHead;
          campStore.put(encodedCandidate, 'live');
          headStore.put(newHead, 'live');
          tx.objectStore(STORE_META).put(view, 'live-view');
          this.epoch = newHead.epoch;
        };
      };
      tx.oncomplete = () => { this.verifyCommit(written, data).then(resolve, reject); };
      tx.onabort = tx.onerror = () => reject(new Error('commit transaction aborted: ' + tx.error));
      tx.onabort = () => reject(candidateError || new Error('CAS head mismatch: expected revision ' + expectedHead?.revision));
    });
  }

  /**
   * Replaces the campaign entirely (e.g. New Game, Slot Load, or Import)
   * Advances the adapter epoch so any delayed autosaves from the prior epoch are rejected.
   */
  async replace(expectedHead, encodedCandidate, data, view = 'kingdom') {
    const candidateState = decode(encodedCandidate, data);

    await this.open();
    if (!this.db) {
      const currentHead = this.memoryDb.heads.get('live');
      if (!casAllows(currentHead, expectedHead)) {
        throw new Error('CAS head mismatch: expected revision ' + expectedHead?.revision + ' but found ' + currentHead?.revision);
      }
      const previousLive = this.memoryDb.campaigns.get('live');
      if (previousLive) preservePrevious({ put: (value, key) => this.memoryDb.campaigns.set(key, value) }, previousLive, data, currentHead);
      const newHead = headFor(candidateState, encodedCandidate, (currentHead?.epoch || 0) + 1);
      this.memoryDb.campaigns.set('live', encodedCandidate);
      this.memoryDb.heads.set('live', newHead);
      this.epoch = newHead.epoch;
      return newHead;
    }

    return new Promise((resolve, reject) => {
      const tx = this.writeTransaction([STORE_HEAD, STORE_CAMPAIGNS, STORE_META]);
      const headStore = tx.objectStore(STORE_HEAD);
      const campStore = tx.objectStore(STORE_CAMPAIGNS);
      let written = null;
      const headReq = headStore.get('live');
      headReq.onsuccess = () => {
        const currentHead = headReq.result;
        if (!casAllows(currentHead, expectedHead)) {
          try { tx.abort(); } catch { /* The abort handler rejects. */ }
          return;
        }
        const liveReq = campStore.get('live');
        liveReq.onsuccess = () => {
          preservePrevious(campStore, liveReq.result, data, currentHead);
          written = headFor(candidateState, encodedCandidate, (currentHead?.epoch || 0) + 1);
          campStore.put(encodedCandidate, 'live');
          headStore.put(written, 'live');
          tx.objectStore(STORE_META).put(view, 'live-view');
          this.epoch = written.epoch;
        };
      };
      tx.oncomplete = () => { this.verifyCommit(written, data).then(resolve, reject); };
      tx.onabort = tx.onerror = () => reject(new Error('replace transaction aborted: ' + tx.error));
      tx.onabort = () => reject(new Error('CAS head mismatch: expected revision ' + expectedHead?.revision));
    });
  }

  async verifyCommit(written, data) {
    // A completed write may outlive its acknowledgement. Inspect the existing
    // head again; never replay the command, rollback, or adopt a foreign head.
    let failure;
    for (let attempt = 0; attempt < 2; attempt++) {
      try {
        const snapshot = await this.loadLive(data);
        if (snapshot.status !== 'VALID' || !headsMatch(snapshot.head, written)) throw new Error('Snapshot changed before save acknowledgement');
        return written;
      } catch (error) { failure = error; }
    }
    const error = new Error('Save acknowledgement uncertain. Export changes and reopen to reconcile.', { cause: failure });
    error.committedHead = written;
    throw error;
  }

  /**
   * Stores a campaign snapshot into slot 1, 2, or 3.
   */
  async storeSlot(index, encodedCandidate, data) {
    if (!Number.isInteger(index) || index < 1 || index > 3) throw new Error('Invalid slot index: ' + index);
    decode(encodedCandidate, data); // Validate before storage
    await this.open();
    if (!this.db) {
      this.memoryDb.slots.set(`slot-${index}`, encodedCandidate);
      return true;
    }
    return new Promise((resolve, reject) => {
      const tx = this.writeTransaction([STORE_SLOTS]);
      tx.objectStore(STORE_SLOTS).put(encodedCandidate, `slot-${index}`);
      tx.oncomplete = () => {
        try {
          const verify = this.db.transaction([STORE_SLOTS], 'readonly');
          const req = verify.objectStore(STORE_SLOTS).get(`slot-${index}`);
          verify.oncomplete = () => req.result === encodedCandidate ? resolve(true) : reject(new Error('Slot readback changed before acknowledgement'));
          verify.onabort = verify.onerror = () => reject(verify.error || new Error('Slot acknowledgement uncertain'));
        } catch (error) { reject(error); }
      };
      tx.onabort = tx.onerror = () => reject(new Error('storeSlot failed: ' + tx.error));
    });
  }

  /**
   * Loads a campaign snapshot from slot 1, 2, or 3.
   */
  async loadSlot(index, data) {
    if (!Number.isInteger(index) || index < 1 || index > 3) throw new Error('Invalid slot index: ' + index);
    await this.open();
    if (!this.db) {
      const raw = this.memoryDb.slots.get(`slot-${index}`);
      return raw ? decode(raw, data) : null;
    }
    return new Promise((resolve, reject) => {
      const tx = this.db.transaction([STORE_SLOTS], 'readonly');
      const req = tx.objectStore(STORE_SLOTS).get(`slot-${index}`);
      tx.oncomplete = () => {
        try { resolve(req.result ? decode(req.result, data) : null); }
        catch (error) { reject(error); }
      };
      tx.onabort = tx.onerror = () => reject(new Error('loadSlot failed: ' + tx.error));
    });
  }

  /**
   * Restores last-good backup to live campaign.
   */
  async restoreBackup(data) {
    const current = await this.loadLive(data);
    if (current.status === 'VALID') throw new Error('Live save is valid');
    const raw = (await this.export()).campaigns.backup;
    if (!raw) throw new Error('No valid backup');
    const state = decode(raw, data);
    await this.replace(current.head, raw, data);
    return state;
  }

  /**
   * Complete migration of all localStorage keys into IndexedDB as specified by A05.
   * Inventories live, backup, staged, damaged, all 3 slots, view, and metadata.
   */
  async migrateFromLocalStorage(storage, data) {
    if (!storage) return { migrated: false, reason: 'No localStorage provided' };

    const live = storage.getItem(SAVE_KEY);
    const backup = storage.getItem(SAVE_KEY + '-backup');
    const staged = storage.getItem(SAVE_KEY + '-staged');
    const damaged = storage.getItem(SAVE_KEY + '-damaged');
    const slot1 = storage.getItem(SAVE_KEY + '-slot-1');
    const slot2 = storage.getItem(SAVE_KEY + '-slot-2');
    const slot3 = storage.getItem(SAVE_KEY + '-slot-3');
    const view = storage.getItem(VIEW_KEY);

    const inventory = {
      hasLive: live !== null,
      hasBackup: backup !== null,
      hasStaged: staged !== null,
      hasDamaged: damaged !== null,
      hasSlots: [slot1 !== null, slot2 !== null, slot3 !== null],
      view: view ?? 'kingdom',
    };

    if (!inventory.hasLive && !inventory.hasBackup && !inventory.hasStaged && !inventory.hasDamaged && !inventory.hasSlots.some(Boolean) && !view) {
      return { migrated: false, reason: 'Empty source localStorage', inventory };
    }

    const sourceHash = checksum(JSON.stringify([live, backup, staged, damaged, slot1, slot2, slot3, view]));
    const marker = { sourceHash, complete: true };

    await this.open();
    if (!this.db) {
      const currentHead = this.memoryDb.heads.get('live');
      const keepLive = this.memoryDb.campaigns.has('live');
      if (live && !keepLive) {
        try {
          const state = decode(live, data);
          this.memoryDb.campaigns.set('live', live);
          this.memoryDb.heads.set('live', headFor(state, live, Math.max(1, (currentHead?.epoch || 0) + 1), { migratedFromLocalStorage: true }));
        } catch {
          this.memoryDb.campaigns.set('damaged', live);
        }
      }
      for (const [key, raw] of Object.entries({ live, backup, staged, damaged, slot1, slot2, slot3 })) {
        if (raw != null) this.memoryDb.campaigns.set(`legacy:${sourceHash}:${key}`, raw);
      }
      if (backup && !this.memoryDb.campaigns.has('backup')) this.memoryDb.campaigns.set('backup', backup);
      if (staged && !this.memoryDb.campaigns.has('staged')) this.memoryDb.campaigns.set('staged', staged);
      if (damaged && !this.memoryDb.campaigns.has('damaged')) this.memoryDb.campaigns.set('damaged', damaged);
      if (slot1 && !this.memoryDb.slots.has('slot-1')) this.memoryDb.slots.set('slot-1', slot1);
      if (slot2 && !this.memoryDb.slots.has('slot-2')) this.memoryDb.slots.set('slot-2', slot2);
      if (slot3 && !this.memoryDb.slots.has('slot-3')) this.memoryDb.slots.set('slot-3', slot3);
      if (view) this.memoryDb.metadata.set('view', view);
      this.memoryDb.metadata.set('migration-marker', marker);
      return { migrated: true, inventory };
    }

    return new Promise((resolve, reject) => {
      const tx = this.writeTransaction([STORE_HEAD, STORE_CAMPAIGNS, STORE_SLOTS, STORE_META]);
      const campStore = tx.objectStore(STORE_CAMPAIGNS);
      const slotStore = tx.objectStore(STORE_SLOTS);
      const metaStore = tx.objectStore(STORE_META);
      const headStore = tx.objectStore(STORE_HEAD);
      const headReq = headStore.get('live');
      headReq.onsuccess = () => {
        const currentHead = headReq.result;
        // Any existing authoritative head wins, including a lower-revision
        // replacement from another campaign. Revision is not a global clock.
        const keepLive = Boolean(currentHead);
        if (live && !keepLive) {
          try {
            const state = decode(live, data);
            campStore.put(live, 'live');
            headStore.put(headFor(state, live, Math.max(1, (currentHead?.epoch || 0) + 1), { migratedFromLocalStorage: true }), 'live');
          } catch {
            campStore.put(live, 'damaged');
          }
        }
        for (const [key, raw] of Object.entries({ live, backup, staged, damaged, slot1, slot2, slot3 })) {
          if (raw != null) campStore.put(raw, `legacy:${sourceHash}:${key}`);
        }
        const putAbsent = (store, key, raw) => {
          if (raw == null) return;
          const request = store.get(key);
          request.onsuccess = () => { if (request.result == null) store.put(raw, key); };
        };
        putAbsent(campStore, 'backup', backup);
        putAbsent(campStore, 'staged', staged);
        putAbsent(campStore, 'damaged', damaged);
        putAbsent(slotStore, 'slot-1', slot1);
        putAbsent(slotStore, 'slot-2', slot2);
        putAbsent(slotStore, 'slot-3', slot3);
        if (view && !keepLive) { metaStore.put(view, 'view'); metaStore.put(view, 'live-view'); }
        metaStore.put(marker, 'migration-marker');
      };
      tx.oncomplete = () => resolve({ migrated: true, inventory });
      tx.onabort = tx.onerror = () => reject(new Error('Migration transaction failed: ' + tx.error));
    });
  }

  /**
   * Export all storage state to a JSON-serializable object.
   */
  async export() {
    await this.open();
    if (!this.db) {
      return {
        heads: Object.fromEntries(this.memoryDb.heads),
        campaigns: Object.fromEntries(this.memoryDb.campaigns),
        slots: Object.fromEntries(this.memoryDb.slots),
        metadata: Object.fromEntries(this.memoryDb.metadata),
      };
    }
    return new Promise((resolve, reject) => {
      const tx = this.db.transaction([STORE_HEAD, STORE_CAMPAIGNS, STORE_SLOTS, STORE_META], 'readonly');
      const heads = {}, campaigns = {}, slots = {}, metadata = {};
      tx.objectStore(STORE_HEAD).openCursor().onsuccess = e => {
        const c = e.target.result;
        if (c) { heads[c.key] = c.value; c.continue(); }
      };
      tx.objectStore(STORE_CAMPAIGNS).openCursor().onsuccess = e => {
        const c = e.target.result;
        if (c) { campaigns[c.key] = c.value; c.continue(); }
      };
      tx.objectStore(STORE_SLOTS).openCursor().onsuccess = e => {
        const c = e.target.result;
        if (c) { slots[c.key] = c.value; c.continue(); }
      };
      tx.objectStore(STORE_META).openCursor().onsuccess = e => {
        const c = e.target.result;
        if (c) { metadata[c.key] = c.value; c.continue(); }
      };
      tx.oncomplete = () => resolve({ heads, campaigns, slots, metadata });
      tx.onabort = tx.onerror = () => reject(new Error('export failed: ' + tx.error));
    });
  }
}
