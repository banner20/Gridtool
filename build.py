# Re-inlines grid-tool.css + grid-tool.js back into a single portable HTML.
# Usage: python build.py   ->   produces grid-tool-dist.html
import re
SRC='grid-tool WORKING COPY.html'
h=open(SRC,encoding='utf-8').read()
css=open('grid-tool.css',encoding='utf-8').read()
js=open('grid-tool.js',encoding='utf-8').read()
# Match the link/script tags with an optional ?v= cache-buster query, and inline.
# Use lambda replacements so backslashes/$ in css/js are not treated as regex group refs.
h,nc=re.subn(r'<link rel="stylesheet" href="grid-tool\.css[^"]*">', lambda m: '<style>'+css+'</style>', h)
h,nj=re.subn(r'<script src="grid-tool\.js[^"]*"></script>', lambda m: '<script>'+js+'</script>', h)
if nc==0: print('WARNING: CSS <link> not found - CSS NOT inlined!')
if nj==0: print('WARNING: JS <script> not found - JS NOT inlined!')
open('grid-tool-dist.html','w',encoding='utf-8').write(h)
print('Wrote grid-tool-dist.html', len(h), 'bytes  (css inlined:', nc, ', js inlined:', nj, ')')
