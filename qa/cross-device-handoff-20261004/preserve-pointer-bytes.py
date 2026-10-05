"""Keep pre-existing pointer-document bytes exact after adding a short banner."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
rows=json.loads((OUT/'documentation-pointers.json').read_text())
for r in rows:
 p=ROOT/r['path'];raw=p.read_bytes();prefix,tail=raw.split(b'\n',2)[0],raw.split(b'\n',2)[2]
 # write_text added one CR to each old LF on Windows; undo just that insertion.
 original=tail.replace(b'\r\n',b'\n')
 assert hashlib.sha256(original).hexdigest()==r['beforeSHA256'],r['path']
 p.write_bytes(prefix.rstrip(b'\r')+b'\n\n'+original)
 r['afterSHA256']=hashlib.sha256(p.read_bytes()).hexdigest()
 r['existingContentBytePreserved']=True
(OUT/'documentation-pointers.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
print('All seven original document bodies preserved byte-for-byte; only new banner prepended.')
