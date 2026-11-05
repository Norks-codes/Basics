#!/usr/bin/env python3
"""Build the tool from src/app.html.

index.html    - one self-contained file to double-click (JSZip inlined).
artifact.html - the same tool as page content for a private Claude page.
"""
import re
from pathlib import Path
here = Path(__file__).parent
app = (here / 'src' / 'app.html').read_text(encoding='utf-8')
lib = (here / 'vendor' / 'jszip.min.js').read_text(encoding='utf-8')
assert '</script' not in lib.lower()
full = app.replace('<!--JSZIP-->', '<script>/* JSZip 3.10.1, MIT licence: see vendor/JSZIP-LICENSE.md */\n' + lib + '\n</script>', 1)
(here / 'index.html').write_text(full, encoding='utf-8')
title = re.search(r'<title>.*?</title>', full, re.S).group(0)
style = re.search(r'<style>.*?</style>', full, re.S).group(0)
body = re.search(r'<body>(.*)</body>', full, re.S).group(1)
art = title + '\n<meta name="claude:viewport-fit-sides" content="cover">\n' + style + '\n' + body
(here / 'artifact.html').write_text(art, encoding='utf-8')
print('index.html', len(full) // 1024, 'KB; artifact.html', len(art) // 1024, 'KB')
