// One page's writes share an ordered head. The adapter supplies the atomic
// cross-window CAS. Replacement invalidates older queued autosaves immediately.
export class SaveQueue {
  constructor(adapter, data, head = null) {
    this.adapter = adapter;
    this.data = data;
    this.head = head;
    this.generation = 0;
    this.sequence = 0;
    this.tail = Promise.resolve();
    this.queued = null;
    this.status = { kind: 'committed', sequence: 0, head };
  }
  write(raw, view, replacement = false) {
    if (replacement) this.generation++;
    const generation = this.generation, sequence = ++this.sequence;
    this.status = { kind: 'pending', sequence };
    let resolve, reject;
    const acknowledgement = new Promise((yes, no) => { resolve = yes; reject = no; });
    if (!replacement && this.queued && !this.queued.replacement && this.queued.generation === generation) {
      // Only the newest not-yet-started snapshot needs a transaction. Earlier
      // callers wait for that encompassing snapshot's actual acknowledgement.
      Object.assign(this.queued, { raw, view, sequence });
      this.queued.waiters.push({ resolve, reject });
      return acknowledgement;
    }
    const entry = { raw, view, sequence, generation, replacement, waiters: [{ resolve, reject }] };
    this.queued = entry;
    const work = this.tail.then(async () => {
      if (this.queued === entry) this.queued = null;
      if (entry.generation !== this.generation) {
        entry.waiters.forEach(waiter => waiter.resolve(false));
        return;
      }
      try {
        const method = entry.replacement ? 'replace' : 'commit';
        const next = await this.adapter[method](this.head, entry.raw, this.data, entry.view);
        this.head = next;
        if (entry.sequence === this.sequence) this.status = { kind: 'committed', sequence: entry.sequence, head: next };
        entry.waiters.forEach(waiter => waiter.resolve(true));
      } catch (error) {
        // Never adopt another writer's head and retry an old in-memory snapshot.
        // That would make CAS protection ineffective. Keep the candidate exportable.
        if (entry.sequence === this.sequence) this.status = { kind: 'failed', sequence: entry.sequence, error: error.message };
        entry.waiters.forEach(waiter => waiter.reject(error));
      }
    });
    this.tail = work.catch(() => {});
    return acknowledgement;
  }
}
