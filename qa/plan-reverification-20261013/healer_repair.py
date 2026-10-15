"""One owner-authorized, no-retry Vertex repair. Import/prepare/selftest do not dispatch.

Reuses the existing coordinator; the adapter persists definite 429 deadlines,
fsyncs write-ahead files, verifies both owners before transport, and releases
cloud CAS before the local mutex. Full raw image payloads remain under assets/.
"""
import argparse, base64, hashlib, importlib.util, json, os, sys, tempfile, time
import urllib.request, urllib.error
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
PACK = ROOT / 'assets/raw/image-repair-20261013/healer-standing-ancient'
CONTROL = ROOT / 'docs/plan/image-production'
LEDGER = CONTROL / 'budget-ledger.json'
ATTEMPT = 'class-healer-standing-body-repair-20261013-1'
HOLD = 0.75
KEY = 'healerRepair20261013'

def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    obj = importlib.util.module_from_spec(spec); spec.loader.exec_module(obj)
    return obj

base = module('repair_coordinator', ROOT / 'qa/image-unified-reserve-20261009/helpers/coordinator.py')
vertex = module('repair_vertex', ROOT / 'scripts/vertex-production.py')
def read(path): return json.loads(path.read_text(encoding='utf-8-sig'))
def sha(data): return hashlib.sha256(data).hexdigest()
def now(): return datetime.now(timezone.utc).isoformat()
def atomic(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + f'.tmp.{os.getpid()}')
    with tmp.open('wb') as f:
        f.write(data); f.flush(); os.fsync(f.fileno())
    os.replace(tmp, path)
def write(path, value): atomic(path, (json.dumps(value, indent=2) + '\n').encode())

class OwnedCoordinator(base.Coordinator):
    def _atomic_write(self, path, data): atomic(path, data)
    def check_owner(self):
        local = read(self.mutex_file)
        if not self.has_lock or not local.get('active') or local.get('owner') != self.owner_id or local.get('pid') != self.pid or local.get('runUuid') != self.run_uuid:
            raise base.MutexError('Local mutex ownership changed')
        current, generation = self._get_cloud_lock(self._token())
        if str(generation) != str(self.cloud_lock_generation) or current.get('owner') != self.owner_id:
            raise base.MutexError('Cloud CAS ownership changed')
    def transport_once(self, endpoint, wire):
        self.check_owner()
        item = read(LEDGER)[KEY]
        if item['attemptId'] != ATTEMPT or item['retainedUSD'] != HOLD or item['wireBodySHA256'] != sha(wire):
            raise base.BudgetError('Global durable reservation changed')
        self.dispatched = True
        req = urllib.request.Request(endpoint, data=wire, method='POST', headers={'Authorization': 'Bearer ' + self._token(), 'Content-Type': 'application/json'})
        try:
            with urllib.request.urlopen(req, timeout=180) as response:
                return response.read(), response.status, dict(response.headers)
        except urllib.error.HTTPError as error:
            # Return every definite HTTP response to the existing durable finalizer.
            return error.read(), error.code, dict(error.headers or {})
        except (TimeoutError, urllib.error.URLError, ConnectionError) as error:
            raise base.UnknownLiabilityError(type(error).__name__) from None
    def release_mutex(self, state='RELEASED'):
        if self.blocked or self.unresolved_items:
            return super().release_mutex(state)
        self.check_owner()
        terminal = {'batch_id': ATTEMPT, 'model': base.MODEL, 'project': base.PROJECT, 'account': base.ACCOUNT,
                    'state': 'JOB_STATE_SUCCEEDED', 'workflow_state': 'TERMINAL_COLLECTED',
                    'owner': self.owner_id, 'releasedAt': now(), 'lastState': state}
        generation = self._put_cloud_lock(terminal, self.cloud_lock_generation, self._token())
        terminal['cloud_lock_generation'] = generation
        write(CONTROL / 'active-batch.lock.json', terminal)
        self.cloud_lock_enabled = False
        return super().release_mutex(state)

PROMPT = '''Create exactly one coherent full-body standing character illustration for Ages of Dominion.
The first image defines the Healer woman's identity: same adult face, brown eyes, braided brown hair.
The second sheet supplies identity and earthy linen/leather material inspiration only; it is NOT the layout to reproduce.
Generate a single anatomically connected adult woman, realistic 7 to 7.5 head proportions, head naturally attached through neck to shoulders, exactly two arms ending in two complete hands, two legs ending in two complete leather shoes. Front-facing calm neutral standing pose, arms comfortably lowered a little away from torso, open relaxed empty hands, both feet on the same baseline. Full figure from crown to soles wholly inside the frame, generous margin on all sides. Do not crop anything.
This is her ANCIENT base outfit for Stone/Bronze/Iron, with zero equipped items: modest ankle-length undyed beige woven linen robe, simple brown leather waist tie, plain soft leather footwear, restrained woven sage trim. Hair neatly braided as the reference. NO metal circlet, plates, pauldrons, armor, greaves, jewelry, ring, weapon, shield, staff, magical orb or hand-held item. The medieval metal pieces in the references must not appear. No modern tailoring, exposed midriff or glamour pose.
High-quality painterly realistic game character matching the supplied face, restrained natural colors, soft upper-left lighting, detailed face, hands, folds and soles, clear silhouette. Single front view only. Do not make a component sheet, portrait, collage, spare limbs or alternative views.
BACKGROUND: perfectly uniform bright pure magenta RGB(255,0,255) everywhere outside the character, including gaps between limbs, for deterministic local alpha extraction. No magenta clothing or reflected magenta rim. No floor, ground shadow, pedestal, plants, scene, text, labels, divider lines, border, UI, watermark or extra object. Figure fills about 88 percent of image height. Return one 2K square image.'''

def prepare():
    if (PACK / 'write_ahead_request.json').exists(): raise RuntimeError('Existing attempt: inspect receipt; never prepare a resend')
    refs = ['assets/derivatives/rigs/v9/healer/healer-head-front-bust.png', 'assets/high-res/final-native2k/rig-source-parts-healer.png']
    parts = [{'text': PROMPT}]; sources = []
    for rel in refs:
        data = (ROOT / rel).read_bytes()
        assert len(data) < 7_000_000
        with Image.open(ROOT / rel) as im: dimensions = list(im.size)
        parts.append({'inlineData': {'mimeType': 'image/png', 'data': base64.b64encode(data).decode()}})
        sources.append({'path': rel, 'sha256': sha(data), 'dimensions': dimensions, 'bytes': len(data)})
    body = {'contents': [{'role': 'user', 'parts': parts}], 'generationConfig': {'candidateCount': 1, 'responseModalities': ['TEXT', 'IMAGE'], 'maxOutputTokens': 8192, 'imageConfig': {'aspectRatio': '1:1', 'imageSize': '2K'}}}
    wire = json.dumps(body, separators=(',', ':')).encode()
    atomic(PACK / 'prepared_request.json', wire)
    info = {'at': now(), 'id': 'class-healer-standing-body', 'attemptId': ATTEMPT, 'owner': 'ACTORS', 'wireBodySHA256': sha(wire), 'sources': sources,
            'prompt': PROMPT, 'project': base.PROJECT, 'model': base.MODEL, 'resolution': '2K', 'reservationUSD': HOLD,
            'reservationBasis': '8192 max output tokens all priced pessimistically as image: 0.49152 USD; 2 inputs at 1120 tokens plus prompt at <=1 token/character; total below 0.496 USD before 0.254 USD overhead buffer. Retain full 0.75 until invoice reconciliation.',
            'priorAttempt': '9 October prepared healer-class-standing-body was NOT_POSTED; seven other classes purchased; current mixed-part Healer fails anatomy.',
            'materialDifference': 'Generate a coherent empty-handed ancient base figure from native identity references; no assembly or repeated failed free-layout request.',
            'ledgerSHA256': sha(LEDGER.read_bytes()), 'paidPosts': 0, 'invoiceStatus': 'UNKNOWN'}
    write(OUT / 'healer-prepared.json', info)
    print(json.dumps({'prepared': True, 'sources': len(sources), 'wireSHA256': info['wireBodySHA256'], 'holdUSD': HOLD}))

def selftest():
    cases = []
    with tempfile.TemporaryDirectory(prefix='aod-healer-guard-') as tmp:
        root = Path(tmp); clock = [100.0]
        def sleep(secs): clock[0] += secs
        release = read(LEDGER)['ownerReserveRelease20261009']
        for name, code, headers in [('success', 200, {}), ('quota', 429, {'Retry-After': '90'}), ('unknown', 503, {})]:
            c = OwnedCoordinator(root / name, release=release, clock=lambda: clock[0], sleeper=sleep, success_gap=20, transport=lambda e,w: (b'{}', code, headers))
            c.acquire_mutex(); wire=b'{}'; meta={'id':name, 'attemptId':name, 'wireBodySHA256':sha(wire)}
            try: c.execute_prepared(root / name / 'pack', wire, meta, HOLD)
            except (base.QuotaStop, base.UnknownLiabilityError): pass
            if name=='success':
                assert read(c.pacing_file)['nextAllowedPOSTAtTs'] == clock[0]+20
                c._enforce_pacing(); assert clock[0]==120
            if name=='quota': assert read(c.pacing_file)['nextEligibleRetryAtTs']==clock[0]+90
            if name=='unknown':
                assert read(root / name / 'pack/write_ahead_request.json')['status']=='UNKNOWN'
                try: c.execute_prepared(root / name / 'pack', wire, meta, HOLD)
                except base.UnknownLiabilityError: pass
                else: raise AssertionError('UNKNOWN resent')
            assert c.reservations[0]['retained']
            cases.append({'case':name, 'pass':True})
        for name, changes in [('budget', {'new_reservation_usd':16}), ('duplicate', {'known_attempt_ids':{'x'}}), ('double-release', {'prior_liability_usd':49.8327}), ('unknown-hold', {'unknown_outstanding':True})]:
            args=dict(release=release,prior_liability_usd=64.8327,other_effective_holds_usd=0,new_reservation_usd=HOLD,effective_reserve_usd=0,known_attempt_ids=set(),attempt_id='x',unknown_outstanding=False,double_subtracted=False); args.update(changes)
            try: base.guard_post(**args)
            except base.BudgetError: cases.append({'case':name,'pass':True})
            else: raise AssertionError(name)
    write(OUT / 'healer-coordinator-selftest.json', {'networkCalls':0,'productionWrites':0,'cases':cases})
    print(json.dumps(cases))

def run():
    info=read(OUT / 'healer-prepared.json'); wire=(PACK / 'prepared_request.json').read_bytes()
    inventory=read(OUT / 'provider-inventory.json')
    assert inventory['status']=='PASS_METADATA_ONLY' and not inventory['nonterminalJobs'] and not inventory['errors']
    assert (datetime.now(timezone.utc)-datetime.fromisoformat(inventory['at'])).total_seconds()<3600, 'Refresh metadata inventory'
    assert sha(wire)==info['wireBodySHA256'] and sha(LEDGER.read_bytes())==info['ledgerSHA256'], 'Prepared snapshot drift'
    assert all(x['pass'] for x in read(OUT / 'healer-coordinator-selftest.json')['cases'])
    ledger=read(LEDGER); assert KEY not in ledger, 'Attempt already reserved; inspect, never replay'
    c=OwnedCoordinator(OUT / 'healer-control', owner_id=f'healer-repair-20261013-pid{os.getpid()}', release=ledger['ownerReserveRelease20261009'], cloud_lock_enabled=True,
                       mutex_file=CONTROL/'submission.mutex.json', pacing_file=CONTROL/'pacing_state.json', token_provider=vertex.auth, success_gap=20)
    c.dispatched=False; c.transport=c.transport_once
    c.acquire_mutex()
    try:
        c.check_owner()
        assert sha(LEDGER.read_bytes())==info['ledgerSHA256'], 'Ledger changed while acquiring'
        for location in ['global','us-central1']:
            prefix='' if location=='global' else location+'-'
            url=f'https://{prefix}aiplatform.googleapis.com/v1/projects/{base.PROJECT}/locations/{location}/batchPredictionJobs?pageSize=100'
            while url:
                data=vertex.api(url)
                assert all(job.get('state') in vertex.TERMINAL for job in data.get('batchPredictionJobs',[])), 'Active or unknown job'
                token=data.get('nextPageToken'); url=url.split('&pageToken=')[0]+'&pageToken='+base.urllib.parse.quote(token,safe='') if token else None
        base.guard_post(release=c.release, prior_liability_usd=64.8327,other_effective_holds_usd=0,new_reservation_usd=HOLD,effective_reserve_usd=0,known_attempt_ids=set(),attempt_id=ATTEMPT,unknown_outstanding=False,double_subtracted=False)
        ledger[KEY]={'attemptId':ATTEMPT,'itemId':info['id'],'at':now(),'retainedUSD':HOLD,'effectiveLiabilityUSD':round(64.8327+HOLD,4),'remainingHeadroomUSD':round(80-64.8327-HOLD,4),'effectiveReserveUSD':0,'invoiceStatus':'UNKNOWN','status':'RESERVED_BEFORE_POST','wireBodySHA256':sha(wire),'receipt':'qa/plan-reverification-20261013/healer-receipt.json','authority':'Owner request in this chat plus OWNER-PAID-BATCH-PROGRESSIVE-AUTHORITY-2026-10-11.md'}
        write(LEDGER,ledger)
        result=c.execute_prepared(PACK,wire,info,HOLD)
        ledger=read(LEDGER); assert ledger[KEY]['attemptId']==ATTEMPT
        ledger[KEY]['status']=result['status']+'_LIABILITY_RETAINED'; write(LEDGER,ledger)
        result.update({'at':now(),'invoiceStatus':'UNKNOWN','effectiveLiabilityUSD':round(64.8327+HOLD,4),'headroomUSD':round(80-64.8327-HOLD,4),'wireBodySHA256':sha(wire),'visualAcceptance':'UNVERIFIED'})
        write(OUT/'healer-receipt.json', result)
        c.release_mutex('RELEASED_AFTER_RECORDED_RESPONSE')
        print(json.dumps(result))
    except Exception as exc:
        report={'at':now(),'error':type(exc).__name__,'reason':str(exc)[:400],'dispatched':c.dispatched,'retainHold':True,'automaticRetry':False}
        write(OUT/'healer-dispatch-error.json',report)
        if c.dispatched:
            c.blocked=True; c.block_reason=type(exc).__name__; c.release_mutex('UNKNOWN' if c.unresolved_items else 'STOPPED_REVIEW_REQUIRED')
        elif c.has_lock:
            c.release_mutex('RELEASED_NO_GENERATION_POST')
        raise

if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    parser=argparse.ArgumentParser(); parser.add_argument('action',choices=['prepare','selftest','run']); args=parser.parse_args()
    {'prepare':prepare,'selftest':selftest,'run':run}[args.action]()
