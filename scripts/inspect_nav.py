import glob, re

for p in glob.glob('src/**/*.js', recursive=True):
    txt = open(p, encoding='utf-8').read()
    if 'nav:' in txt:
        print("Found nav: in", p)
        for line in txt.splitlines():
            if 'nav:' in line:
                print("  ", line.strip())

