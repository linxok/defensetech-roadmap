#!/usr/bin/env python3
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
md_count = 0
line_count = 0
for dirpath, dirnames, filenames in os.walk(BASE):
    for f in filenames:
        if f.endswith('.md'):
            md_count += 1
            with open(os.path.join(dirpath, f), encoding='utf-8', errors='ignore') as fh:
                line_count += len(fh.readlines())
print(f'Markdown files: {md_count}')
print(f'Markdown lines: {line_count}')
print(f'Approx pages: {line_count // 50}')
