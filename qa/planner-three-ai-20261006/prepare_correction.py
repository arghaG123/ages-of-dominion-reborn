from pathlib import Path
p=Path(__file__).resolve().parent
for n in ['browser-report.json','browser-run.log']:
    q=p/n
    if q.exists(): (p/(q.stem+'-harness-before-correction'+q.suffix)).write_bytes(q.read_bytes())
f=p/'capture.mjs'
s=f.read_text()
s=s.replace("const shots = path.join(qa, 'shots');", "const shots = path.join(qa, 'shots');")
# Repeated capture is justified by incomplete image loading in first snapshots.
s=s.replace("async function shot(page, name) {", """async function shot(page, name) {
  await page.waitForTimeout(1200);
  await page.evaluate(async () => {
    await Promise.all([...document.images].map(img => img.decode().catch(() => {})));
    const urls = [...document.querySelectorAll('svg image')].map(n => n.getAttribute('href')).filter(Boolean);
    await Promise.all(urls.map(url => new Promise(resolve => { const im = new Image(); im.onload = im.onerror = resolve; im.src = url; })));
  });
  await page.waitForTimeout(100);
""")
s=s.replace('qa/planner-three-ai-20261006/visual','qa/planner-three-ai-20261006/visual-loaded')
s=s.replace('const port = 4362','const port = 4364')
(p/'capture-loaded.mjs').write_text(s)
print('Raw snapshots preserved; loaded capture has distinct output and port')
