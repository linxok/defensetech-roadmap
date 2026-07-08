#!/usr/bin/env python3
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

errors = []

for i in range(18):
    prefix = f'{i:02d}-'
    matches = [d for d in os.listdir(BASE) if d.startswith(prefix) and os.path.isdir(os.path.join(BASE, d))]
    if not matches:
        errors.append(f'Module {prefix} missing')

required_root = ['README.md', 'LICENSE', 'CONTRIBUTING.md', 'ROADMAP.md', 'mkdocs.yml', 'QUICKSTART.md', 'requirements.txt']
for name in required_root:
    if not os.path.exists(os.path.join(BASE, name)):
        errors.append(f'{name} missing')

md_count = 0
line_count = 0
for dirpath, dirnames, filenames in os.walk(BASE):
    for f in filenames:
        if f.endswith('.md'):
            md_count += 1
            with open(os.path.join(dirpath, f), encoding='utf-8', errors='ignore') as fh:
                line_count += len(fh.readlines())

print(f'Modules: {18 - len([e for e in errors if "Module" in e])}/18')
print(f'Markdown files: {md_count}')
print(f'Markdown lines: {line_count}')
print(f'Approx pages: {line_count // 50}')

if errors:
    print('ERRORS:')
    for e in errors:
        print(f'  - {e}')
    sys.exit(1)

print('All checks passed.')
