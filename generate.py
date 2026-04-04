import random
import math
import urllib.parse
import re
import os

width = 650
height = 650
num_nodes = 45
max_dist = 180

# fixed seed for reproducibility so it always looks exactly the same and doesn't flap around
random.seed(42)

nodes = []
# generate more and filter
for _ in range(num_nodes * 2):
    x = random.uniform(100, 650)
    y = random.uniform(0, 550)
    dist_from_tr = math.sqrt((x - 650)**2 + (y - 0)**2)
    if dist_from_tr < 550:
        nodes.append((x, y))
    if len(nodes) >= num_nodes:
        break

# Add some explicitly near the edges so it touches nicely
nodes.extend([(600, 30), (620, 100), (400, 20), (550, 10)])

svg = [f"<svg xmlns='http://www.w3.org/2000/svg' width='{width}' height='{height}' viewBox='0 0 {width} {height}'>"]
svg.append("<g stroke='#64748b' stroke-width='1'>")
for i, (x1, y1) in enumerate(nodes):
    for j, (x2, y2) in enumerate(nodes[i+1:]):
        dist = math.sqrt((x1-x2)**2 + (y1-y2)**2)
        if dist < max_dist:
            op = 1 - (dist / max_dist)
            op = op * 0.8
            svg.append(f"<line x1='{x1:.1f}' y1='{y1:.1f}' x2='{x2:.1f}' y2='{y2:.1f}' stroke-opacity='{op:.2f}'/>")

svg.append("</g><g fill='#64748b'>")
for x, y in nodes:
    r = random.uniform(1.5, 3.5)
    svg.append(f"<circle cx='{x:.1f}' cy='{y:.1f}' r='{r:.1f}'/>")
svg.append("</g></svg>")

xml_str = ''.join(svg)
encoded = urllib.parse.quote(xml_str)
data_url = f'data:image/svg+xml,{encoded}'

file_path = os.path.join('home', 'templates', 'home.html')
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace before
content = re.sub(
    r'(\.plexus-layer::before\s*\{[^\}]*?background-image:\s*url\(").*?("\);[^\}]*?\})',
    lambda m: m.group(1) + data_url + m.group(2),
    content,
    flags=re.DOTALL
)

# Replace after, change rotate(0deg) to rotate(180deg) so that top-right becomes bottom-left
def repl_after(m):
    return m.group(1) + data_url + m.group(2) + '180deg' + m.group(3)

content = re.sub(
    r'(\.plexus-layer::after\s*\{[^\}]*?background-image:\s*url\(").*?("\);[^\}]*?transform:\s*rotate\()0deg(\);[^\}]*?\})',
    repl_after,
    content,
    flags=re.DOTALL
)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print('Successfully updated home.html')
