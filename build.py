# Re-inlines grid-tool.css + grid-tool.js back into a single portable HTML.
# Usage: python build.py   ->   produces grid-tool-dist.html
SRC='grid-tool WORKING COPY.html'
h=open(SRC,encoding='utf-8').read()
css=open('grid-tool.css',encoding='utf-8').read()
js=open('grid-tool.js',encoding='utf-8').read()
h=h.replace('<link rel="stylesheet" href="grid-tool.css">','<style>'+css+'</style>')
h=h.replace('<script src="grid-tool.js"></script>','<script>'+js+'</script>')
open('grid-tool-dist.html','w',encoding='utf-8').write(h)
print('Wrote grid-tool-dist.html', len(h), 'bytes')
