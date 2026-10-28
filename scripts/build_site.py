#!/usr/bin/env python3
"""Package the public website from its referenced assets, never from the whole repo."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / '_site'
PRIVATE = {'text-editor', 'video-review', '.git', '.github'}

class References(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []
        self.ids = set()
    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if values.get('id'):
            self.ids.add(values['id'])
        for name in ('href', 'src', 'poster'):
            if values.get(name):
                self.urls.append(values[name])


def public_assets():
    page = References()
    page.feed((ROOT / 'index.html').read_text())
    files = {'index.html', '.nojekyll'}
    queue = [(url, ROOT) for url in page.urls]
    while queue:
        url, parent = queue.pop()
        parsed = urlsplit(url)
        if parsed.scheme or parsed.netloc:
            continue
        if not parsed.path:
            if parsed.fragment and parsed.fragment not in page.ids:
                raise ValueError(f'Broken page anchor: {url}')
            continue
        candidate = parent / unquote(parsed.path)
        if candidate.is_symlink():
            raise ValueError(f'Symlinks are not public assets: {url}')
        candidate = candidate.resolve()
        relative = candidate.relative_to(ROOT)
        if PRIVATE.intersection(relative.parts):
            raise ValueError(f'Private path referenced by website: {relative}')
        if relative.parts[0] != 'static' and relative.as_posix() not in {'index.html', '.nojekyll'}:
            raise ValueError(f'Unexpected public asset: {relative}')
        if not candidate.is_file():
            raise FileNotFoundError(f'Missing website asset: {relative}')
        name = relative.as_posix()
        if name in files:
            continue
        files.add(name)
        if candidate.suffix == '.css':
            queue.extend((match.strip(' \"\''), candidate.parent)
                         for match in re.findall(r'url\(([^)]+)\)', candidate.read_text()))
    return sorted(files)


def main():
    assets = public_assets()
    if DEST.exists():
        shutil.rmtree(DEST)
    DEST.mkdir()
    for name in assets:
        target = DEST / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / name, target)
    size = sum((DEST / name).stat().st_size for name in assets)
    print(f'Packaged {len(assets)} public files ({size / 1024 / 1024:.2f} MiB) in {DEST.name}/')
    for name in assets:
        print(name)

if __name__ == '__main__':
    main()
