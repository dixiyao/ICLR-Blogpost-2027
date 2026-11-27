"""Restyle the supplied workflow copy and create a matching interactive web figure.

The original Federation-of-Text/figures/workflow.drawio is never written.
Run this script from any working directory to regenerate the assets.
"""
from pathlib import Path
from html import escape
from urllib.parse import quote
import xml.etree.ElementTree as ET
from draw_distributed_systems import server

OUT = Path(__file__).resolve().parent
HTML = OUT.parents[1] / 'html' / OUT.name
DRAWIO = OUT / 'fedavg-fot-foh-workflow.drawio'
W, H = 1120, 486
BLACK = '#000000'
BLUE = '#2563eb'
# Preserve the copied document's identity, replacing its diagram cells with the restyled layout.
tree = ET.parse(DRAWIO)
model = tree.find('.//mxGraphModel')
model.set('pageWidth', str(W))
model.set('pageHeight', str(H))
root = model.find('root')
root.clear()
ET.SubElement(root, 'mxCell', id='0')
ET.SubElement(root, 'mxCell', id='1', parent='0')
parts = []
serial = 0


def cell(value, x, y, w, h, style, match=None):
    global serial
    serial += 1
    c = ET.SubElement(root, 'mxCell', id=f'workflow-{serial}', value=value,
                      style=style, vertex='1', parent='1')
    if match:
        c.set('tooltip', f'Corresponding component on both sides: {match}')
    ET.SubElement(c, 'mxGeometry', x=str(x), y=str(y), width=str(w), height=str(h), attrib={'as':'geometry'})


def text(lines, x, y, width, size=15, weight=400, match=None):
    height = 21*len(lines)
    cell('\n'.join(lines), x-width/2, y-size, width, height,
         f'text;html=0;align=center;verticalAlign=middle;whiteSpace=wrap;fontFamily=Arial;fontSize={size};fontStyle={1 if weight==600 else 0};fontColor={BLACK};', match)
    return ''.join(f'<text x="{x}" y="{y+i*21}" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="{size}" font-weight="{weight}">{escape(t)}</text>' for i,t in enumerate(lines))


def group(body, match, label):
    return f'<g class="match" data-match="{match}" tabindex="0" role="group" aria-label="{escape(label)}">{body}</g>'


def card(lines, x, y, w, h, match):
    cell('\n'.join(lines), x, y, w, h,
         f'rounded=1;arcSize=15;whiteSpace=wrap;html=0;fillColor=#ffffff;strokeColor=#000000;strokeWidth=1;fontColor={BLACK};fontFamily=Arial;fontSize=15;spacing=9;', match)
    body = f'<rect class="card" x="{x}" y="{y}" width="{w}" height="{h}" rx="9" fill="white" stroke="#000000"/>'
    start = y+h/2-(len(lines)-1)*10.5+5
    body += ''.join(f'<text x="{x+w/2}" y="{start+i*21}" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="15">{escape(t)}</text>' for i,t in enumerate(lines))
    return group(body, match, ' '.join(lines))


def path(points, match):
    global serial
    serial += 1
    c = ET.SubElement(root, 'mxCell', id=f'workflow-{serial}', edge='1', parent='1',
                      style=f'edgeStyle=none;rounded=0;html=0;strokeColor={BLACK};strokeWidth=1.5;endArrow=block;endFill=1;')
    g=ET.SubElement(c,'mxGeometry',relative='1',attrib={'as':'geometry'})
    for name, (x,y) in [('sourcePoint',points[0]),('targetPoint',points[-1])]:
        ET.SubElement(g,'mxPoint',x=str(x),y=str(y),attrib={'as':name})
    if len(points)>2:
        arr=ET.SubElement(g,'Array',attrib={'as':'points'})
        for x,y in points[1:-1]:
            ET.SubElement(arr,'mxPoint',x=str(x),y=str(y))
    d='M'+' L'.join(f'{x} {y}' for x,y in points)
    return f'<g class="match connector" data-match="{match}"><path d="{d}" fill="none" stroke="{BLACK}" stroke-width="1.5" stroke-linejoin="round" marker-end="url(#arrow)"/></g>'


for offset, name, state, local, upload, aggregate, client in [
    (0, 'FedAvg', 'Global model', 'Local optimization', 'Upload model weights', ['Aggregate', 'model weights to', 'update the model'], 'Client'),
    (580, 'FoT/FoH', 'Shared memory/harness', 'Local reasoning and self-reflection', 'Upload reasoning traces', ['Aggregate traces', 'to update shared', 'memory/harness'], 'Agent'),
]:
    x=lambda n: n+offset
    parts.append(text([name],x(270),470,300,22,600))
    parts.append(group(text([state],x(270),61,290,15,600,'state'),'state',state))
    # User's edited arrangement: server -> aggregation -> broadcast;
    # each client performs its own local work and uploads back to the server.
    parts.append(path([(x(250),108),(x(224),108)],'4'))
    parts.append(path([(x(129),154),(x(129),180)],'1'))
    for target in [110,270,430]:
        parts.append(path([(x(129),238),(x(129),255),(x(target),255),(x(target),280)],'1'))
        parts.append(path([(x(target),318),(x(target),329)],'2'))
        parts.append(path([(x(target),399),(x(target),414),(x(522),414),(x(522),231)],'3'))
    parts.append(path([(x(431),173),(x(431),115),(x(294),115)],'3'))
    icon=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-20 -48 57 85">{server(0,0)}</svg>'
    cell('',x(250),79,45.6,68,
         'shape=image;verticalLabelPosition=bottom;verticalAlign=top;imageAspect=0;aspect=fixed;image=data:image/svg+xml,'+quote(icon,safe='')+';','server')
    parts.append(group(server(x(266),117,.8),'server','Server'))
    parts.append(card(['1. Broadcast', 'global model' if name=='FedAvg' else 'memory/harness'],x(30),180,198,58,'1'))
    parts.append(card(['3. Upload', 'model weights' if name=='FedAvg' else 'reasoning traces'],x(326),173,210,58,'3'))
    parts.append(card(['4. '+aggregate[0],*aggregate[1:]],x(31),72,193,82,'4'))
    for cx in [110,270,430]:
        parts.append(card([client],x(cx-46),280,92,38,'clients'))
        local_lines = ['2. Local', 'optimization'] if name=='FedAvg' else ['2. Local reasoning', 'and self-reflection']
        parts.append(card(local_lines,x(cx-72),329,144,70,'2'))

body='\n'.join(parts)
# No external fonts, scripts, images, or libraries are required by the web figure.
style='''
text { fill: #000000; }
.match { outline: none; }
.match text, .match rect, .match path { transition: fill .15s, stroke .15s, filter .15s; }
.match.active text { fill: #2563eb; }
.match.active [stroke] { stroke: #2563eb; }
.match.active .card { fill: #eff6ff; filter: drop-shadow(0 2px 4px #2563eb25); }
.match.active.connector path { marker-end: url(#arrow-blue); }
@media (prefers-reduced-motion: reduce) { .match * { transition: none; } }
'''
defs='''<defs><marker id="arrow" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0 L8 4 L0 8 Z" fill="#000000"/></marker><marker id="arrow-blue" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0 L8 4 L0 8 Z" fill="#2563eb"/></marker></defs>'''
svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="FedAvg and FoT/FoH workflows"><style>{style}</style>{defs}<rect width="100%" height="100%" fill="white"/>{body}</svg>'
(OUT/'fedavg-fot-foh-workflow.svg').write_text(svg)
ET.indent(tree, space='  ')
tree.write(DRAWIO, encoding='unicode')
script='''
const items = [...document.querySelectorAll('[data-match]')];
function highlight(key) {
  items.forEach(item => item.classList.toggle('active', item.dataset.match === key));
}
items.forEach(item => {
  item.addEventListener('pointerenter', () => highlight(item.dataset.match));
  item.addEventListener('pointerleave', () => highlight(document.activeElement?.dataset.match));
  item.addEventListener('focus', () => highlight(item.dataset.match));
  item.addEventListener('blur', () => highlight(null));
});
'''
(HTML/'fedavg-fot-foh-workflow.html').write_text(f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>FedAvg and FoT/FoH</title><style>html,body{{margin:0;background:white}}svg{{display:block;width:100%;height:auto}}</style></head>
<body>{svg}<script>{script}</script></body></html>''')
print('Updated Draw.io copy, SVG, and interactive HTML.')
