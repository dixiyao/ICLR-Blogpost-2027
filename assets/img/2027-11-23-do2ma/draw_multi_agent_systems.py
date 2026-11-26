"""Draw multi-agent diagrams with colored task icons as editable SVGs (no external icons).

Run: python3 assets/img/2027-11-23-do2ma/draw_multi_agent_systems.py
"""
from pathlib import Path
from html import escape
from math import hypot
from draw_distributed_systems import rect, line, circle, server

OUT = Path(__file__).resolve().parent
WIDTH, HEIGHT = 360, 340
# SchemeColor: https://www.schemecolor.com/subtle-autumnal-rainbow.php
TASK_COLORS = ['#8BB9D4', '#A6CFA1', '#AE9CD6', '#E1B298']
SHARED_TASK_COLOR = '#DAD6A1' 
POINTS = [(180, 51), (65, 145), (295, 145), (180, 234)]


def agent(cx, cy):
    # Simple labeled nodes, following the visual vocabulary of agent flow diagrams.
    return (rect(cx-29, cy-17, 58, 34, 9, 'white', '#000000', 1.8)
            + f'<text x="{cx}" y="{cy+4}" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="black">Agent</text>')


def task(cx, cy, scale=1, color=SHARED_TASK_COLOR):
    s = f'<path d="M-16 -23 H8 L16 -15 V23 H-16 Z M8 -23 V-15 H16" fill="{color}" stroke="black" stroke-width="1.7" stroke-linejoin="round"/>'
    for yy in [-7, 3, 13]:
        s += f'<path d="M-11 {yy} l2 2 l4 -5" fill="none" stroke="black" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>'
        s += line(-1, yy, 10, yy, '#000000', 1.4)
    return f'<g transform="translate({cx},{cy}) scale({scale})">{s}</g>'


def agent_with_task(cx, cy, color):
    return agent(cx-7, cy) + task(cx+29, cy+22, .65, color)


def edge(a, b):
    return line(*a, *b, '#000000', 1.6)


def communication(a, b):
    # One stroke with an arrowhead at each end: a two-way exchange of messages.
    dx, dy = b[0]-a[0], b[1]-a[1]
    length = hypot(dx, dy)
    ux, uy = dx/length, dy/length
    pad = 36
    start = (a[0]+ux*pad, a[1]+uy*pad)
    end = (b[0]-ux*pad, b[1]-uy*pad)
    s = edge(start, end)
    for point, sign in [(start, 1), (end, -1)]:
        for side in [-1, 1]:
            s += edge(point, (point[0]+sign*ux*6-side*uy*3,
                              point[1]+sign*uy*6+side*ux*3))
    return s


def shared():
    ring = [POINTS[0], POINTS[1], POINTS[3], POINTS[2]]
    return (''.join(edge(p, (180, 145)) for p in POINTS)
            + ''.join(communication(ring[i], ring[(i+1) % 4]) for i in range(4))
            + task(180, 145, 1.35)
            + ''.join(agent(*p) for p in POINTS))


def federated():
    return (''.join(edge(p, (180, 145)) for p in POINTS)
            + server(180, 145, .7)
            + ''.join(agent_with_task(*p, color) for p, color in zip(POINTS, TASK_COLORS)))


def decentralized():
    return (''.join(edge(a, b) for i, a in enumerate(POINTS) for b in POINTS[i+1:])
            + ''.join(agent_with_task(*p, color) for p, color in zip(POINTS, TASK_COLORS)))


def caption(lines):
    return ''.join(f'<text x="180" y="{297+i*21}" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="15" font-weight="600" fill="black">{escape(text)}</text>' for i, text in enumerate(lines))


def svg(body, width, title):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{HEIGHT}" viewBox="0 0 {width} {HEIGHT}" role="img" aria-labelledby="title"><title id="title">{escape(title)}</title><rect width="100%" height="100%" fill="white"/>{body}</svg>\n'


def main():
    panels = [
        ('multi-agent-shared-task', ['Multi-Agent Solve One Complex Task'], shared()),
        ('multi-agent-federated', ['Multiple Agents Collaborate to Solve', 'Individual Tasks (Federated)'], federated()),
        ('multi-agent-decentralized', ['Multiple Agents Collaborate to Solve', 'Individual Tasks (Decentralized)'], decentralized()),
    ]
    combined = []
    for i, (name, title, drawing) in enumerate(panels):
        body = drawing + caption(title)
        (OUT / f'{name}.svg').write_text(svg(body, WIDTH, ' '.join(title)))
        combined.append(f'<g transform="translate({i*WIDTH},0)">{body}</g>')
    (OUT / 'multi-agent-systems.svg').write_text(svg(''.join(combined), WIDTH*3, 'Multi-agent collaboration: one shared task, individual tasks with a central coordinator, and individual tasks with decentralized communication'))


if __name__ == '__main__':
    main()
