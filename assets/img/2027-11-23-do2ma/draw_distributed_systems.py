"""Draw the three diagrams using only Python's standard library.

Run: python3 assets/img/2027-11-23-do2ma/draw_distributed_systems.py
All SVGs are editable vectors; no external icons or generated imagery are used.
"""
from pathlib import Path
from html import escape

OUT = Path(__file__).resolve().parent
INK = '#000000'
BLUE = '#000000'
PALE = '#ffffff'
EDGE = '#000000'
WIDTH, HEIGHT = 360, 330


def rect(x, y, w, h, r=4, fill='white', stroke=INK, sw=2):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'


def line(x1, y1, x2, y2, color=EDGE, sw=2):
    return f'<path d="M{x1} {y1} L{x2} {y2}" fill="none" stroke="{color}" stroke-width="{sw}" stroke-linecap="round"/>'


def circle(x, y, radius, fill=BLUE):
    return f'<circle cx="{x}" cy="{y}" r="{radius}" fill="{fill}"/>'


def polygon(points, fill):
    coords = ' '.join(f'{x},{y}' for x, y in points)
    return f'<polygon points="{coords}" fill="{fill}" stroke="{INK}" stroke-width="1.8" stroke-linejoin="round"/>'


def server(cx, cy, size=1):
    # Tall three-dimensional cabinet, with a dark header and full-height grille.
    x, y, w, h, dx, dy = -18, -35, 36, 70, 16, -11
    faces = polygon([(x,y),(x+dx,y+dy),(x+w+dx,y+dy),(x+w,y)], 'white')
    faces += polygon([(x+w,y),(x+w+dx,y+dy),(x+w+dx,y+h+dy),(x+w,y+h)], 'white')
    faces += rect(x,y,w,h,0,'white',INK,1.8)
    faces += rect(x+4,y+5,w-8,12,0,INK,INK,0)
    faces += circle(x+w-9,y+11,1.5,'white')
    faces += line(x+8,y+11,x+17,y+11,'white',1.2)
    faces += rect(x+4,y+22,w-8,38,0,'white',INK,1.2)
    for row in range(8):
        yy = y+26+row*4.2
        faces += line(x+8,yy,x+w-8,yy,INK,1.1)
    faces += line(x+7,y+h-5,x+w-7,y+h-5,INK,1.5)
    return f'<g transform="translate({cx},{cy}) scale({size})">{faces}</g>'


def connection(a, b):
    return line(a[0], a[1], b[0], b[1], EDGE, 1.6)


def phone(cx, cy):
    return (rect(cx - 17, cy - 31, 34, 62, 6, 'white')
            + rect(cx - 12, cy - 22, 24, 40, 2, PALE, BLUE, 1.5)
            + line(cx - 4, cy - 26, cx + 4, cy - 26, INK, 1.5)
            + circle(cx, cy + 24, 2, INK))


def hospital(cx, cy):
    s = rect(cx - 27, cy - 25, 54, 56, 2, 'white')
    s += rect(cx - 10, cy + 12, 20, 19, 1, PALE, INK, 1.5)
    s += f'<path d="M{cx-3} {cy-17} h6 v6 h6 v6 h-6 v6 h-6 v-6 h-6 v-6 h6 Z" fill="{BLUE}"/>'
    for x in [cx - 19, cx + 14]:
        s += rect(x, cy + 3, 5, 6, 0, PALE, INK, 1)
    return s


def bank(cx, cy):
    s = f'<path d="M{cx-32} {cy-13} L{cx} {cy-31} L{cx+32} {cy-13} Z" fill="{PALE}" stroke="{INK}" stroke-width="2" stroke-linejoin="round"/>'
    for x in [cx - 21, cx - 3, cx + 15]:
        s += rect(x, cy - 7, 6, 30, 1, 'white', INK, 1.5)
    s += line(cx - 28, cy - 7, cx + 28, cy - 7, INK)
    s += line(cx - 29, cy + 24, cx + 29, cy + 24, INK)
    s += line(cx - 33, cy + 31, cx + 33, cy + 31, INK)
    return s


def panel_title(text):
    return f'<text x="180" y="310" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="16" font-weight="600" fill="#000000">{escape(text)}</text>'


def datacenter():
    # A close 2-by-2 cluster; rear row drawn first, with no connections.
    return ''.join(server(x, y, 1.13) for x, y in [(150, 122), (197, 122), (128, 177), (175, 177)])


def gossip():
    points = [(174, 64), (75, 158), (273, 158), (174, 253)]
    edges = ''.join(connection(a,b) for i,a in enumerate(points) for b in points[i+1:])
    return edges + ''.join(server(*point, .82) for point in points)


def federated():
    s = ''.join(connection((174,100),(x,220)) for x in [70,174,278])
    return s + server(174,86) + phone(70,235) + hospital(174,235) + bank(278,235)


def svg(body, width, title):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{HEIGHT}" viewBox="0 0 {width} {HEIGHT}" role="img" aria-labelledby="title">
<title id="title">{escape(title)}</title>
<rect width="100%" height="100%" fill="white"/>
{body}
</svg>\n'''


def main():
    panels = [
        ('data-center-training', 'Distributed Training in Data Center', datacenter()),
        ('gossip-p2p', 'Gossip-Based P2P', gossip()),
        ('federated-learning', 'Federated Learning', federated()),
    ]
    combined = []
    for index, (filename, title, drawing) in enumerate(panels):
        body = panel_title(title) + drawing
        (OUT / f'{filename}.svg').write_text(svg(body, WIDTH, title))
        combined.append(f'<g transform="translate({index * WIDTH},0)">{body}</g>')
    (OUT / 'distributed-systems.svg').write_text(svg('\n'.join(combined), WIDTH * 3, 'Data-center training, fully connected gossip workers, and federated learning'))
    print('Wrote three individual SVGs and distributed-systems.svg')


if __name__ == '__main__':
    main()
