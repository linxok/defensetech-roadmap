import os

def test_modules_exist():
    base = os.path.dirname(os.path.dirname(__file__))
    for i in range(18):
        prefix = f'{i:02d}-'
        matches = [d for d in os.listdir(base) if d.startswith(prefix) and os.path.isdir(os.path.join(base, d))]
        assert matches, f'Module {prefix} not found'

def test_root_files_exist():
    base = os.path.dirname(os.path.dirname(__file__))
    for name in ['README.md', 'LICENSE', 'CONTRIBUTING.md', 'ROADMAP.md', 'mkdocs.yml']:
        assert os.path.exists(os.path.join(base, name)), f'{name} not found'
