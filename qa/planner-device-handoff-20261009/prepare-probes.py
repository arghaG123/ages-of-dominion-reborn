from pathlib import Path
import subprocess,json
root=Path(__file__).resolve().parents[2]
out=Path(__file__).resolve().parent
def adapt(old,new,changes):
    t=(root/old).read_text()
    for a,b in changes:
        assert a in t,a
        t=t.replace(a,b)
    (out/new).write_text('// Isolated adaptation of '+old+'; source preserved.\n'+t)
adapt('qa/planner-post-code-20261007/browser-audit.mjs','browser-audit.mjs',[
 ('qa/planner-post-code-20261007','qa/planner-device-handoff-20261009'),('4427','4501')])
adapt('qa/planner-post-code-20261007/modal-targeted.mjs','modal-targeted.mjs',[
 ('qa/planner-post-code-20261007','qa/planner-device-handoff-20261009'),('4429','4502')])
adapt('qa/planner-three-ai-20261006/natural-journey.mjs','natural-journey.mjs',[
 ('qa/planner-three-ai-20261006','qa/planner-device-handoff-20261009'),('4363','4503')])
adapt('scripts/build.mjs','isolated-build.mjs',[
 ("const root = path.resolve(fileURLToPath(new URL('..', import.meta.url)));","const root = process.cwd();"),
 ("const dist = path.join(root, 'dist');","const dist = path.join(root, 'qa/planner-device-handoff-20261009/static-package');"),
 ("'qa/recovery-executor-20261003'","'qa/planner-device-handoff-20261009'"),
 ("'qa/recovery-executor-20261003/dist-closure.json'","'qa/planner-device-handoff-20261009/dist-closure.json'")])
node='C:/Users/TechnoExponent/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
r=subprocess.run([node,'--test',*[str(p) for p in (root/'tests').glob('*.test.mjs')]],cwd=root,capture_output=True,text=True,encoding='utf-8')
(out/'node-tests.txt').write_text(r.stdout+'\n'+r.stderr,encoding='utf-8')
(out/'test-result.json').write_text(json.dumps({'exitCode':r.returncode,'node':subprocess.check_output([node,'--version'],text=True).strip()},indent=2))
print('Tests captured',r.returncode)
