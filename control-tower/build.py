#!/usr/bin/env python3
"""Inline vendor/jszip.min.js into src/app.html and write index.html (one self-contained file)."""
from pathlib import Path
here = Path(__file__).parent
app = (here / 'src' / 'app.html').read_text(encoding='utf-8')
lib = (here / 'vendor' / 'jszip.min.js').read_text(encoding='utf-8')
assert '</script' not in lib.lower()
out = app.replace('<!--JSZIP-->', '<script>/* JSZip 3.10.1, MIT licence: see vendor/JSZIP-LICENSE.md */\n' + lib + '\n</script>', 1)
(here / 'index.html').write_text(out, encoding='utf-8')
print('index.html', len(out) // 1024, 'KB')
