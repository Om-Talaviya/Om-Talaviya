#!/usr/bin/env python3
"""
generate_isocalendar.py - Generates an initial 3D Isometric GitHub Contribution Calendar
Matches the lowlighter/metrics plugin_isocalendar output style with custom Cyber Cyan accents.
"""

import math
import os

def render_isocalendar_svg(output_path="assets/metrics.isocalendar.svg", theme="dark"):
    width = 960
    height = 290
    
    bg_color = "#0d1117" if theme == "dark" else "#ffffff"
    border_color = "#30363d" if theme == "dark" else "#d0d7de"
    text_color = "#f0f6fc" if theme == "dark" else "#1f2328"
    subtext_color = "#8b949e" if theme == "dark" else "#656d76"
    
    # 3D isometric projection angles
    # iso: x_screen = (x - y) * cos(30), y_screen = (x + y) * sin(30) - z
    cos30 = math.cos(math.radians(30))
    sin30 = math.sin(math.radians(30))
    
    cell_w = 12
    cell_h = 12
    
    # Grid: 26 weeks across, 7 days down
    weeks = 26
    days = 7
    
    origin_x = 480
    origin_y = 70
    
    polys = []
    
    import random
    random.seed(42) # Deterministic realistic activity pattern
    
    colors_dark = [
        ("#161b22", "#0d1117", "#21262d"),       # Empty
        ("#0c4a6e", "#082f49", "#0284c7"),       # Low (Cyan 900)
        ("#0284c7", "#0369a1", "#38bdf8"),       # Medium (Sky 600)
        ("#38bdf8", "#0284c7", "#7dd3fc"),       # High (Sky 400)
        ("#bae6fd", "#38bdf8", "#f0f9ff")        # Peak (Sky 200)
    ]
    
    for w in range(weeks):
        for d in range(days):
            # Decide height/intensity based on position
            r = random.random()
            if (w > 18) or (8 < w < 14 and d < 5):
                lvl = random.choices([0, 1, 2, 3, 4], weights=[0.1, 0.2, 0.35, 0.25, 0.1])[0]
            else:
                lvl = random.choices([0, 1, 2, 3], weights=[0.4, 0.3, 0.2, 0.1])[0]
                
            block_h = lvl * 6
            top_color, left_color, right_color = colors_dark[lvl]
            
            # Iso base coords
            bx = origin_x + (w - d) * (cell_w * cos30)
            by = origin_y + (w + d) * (cell_h * sin30)
            
            # 3D Points
            # Top face
            p0 = (bx, by - block_h)
            p1 = (bx + cell_w * cos30, by + cell_h * sin30 - block_h)
            p2 = (bx, by + cell_h * 2 * sin30 - block_h)
            p3 = (bx - cell_w * cos30, by + cell_h * sin30 - block_h)
            
            # Left side
            p4 = (p3[0], p3[1] + block_h)
            p5 = (p2[0], p2[1] + block_h)
            
            # Right side
            p6 = (p1[0], p1[1] + block_h)
            
            # Draw sides if height > 0
            if block_h > 0:
                # Left Face
                polys.append(f'<polygon points="{p3[0]:.1f},{p3[1]:.1f} {p2[0]:.1f},{p2[1]:.1f} {p5[0]:.1f},{p5[1]:.1f} {p4[0]:.1f},{p4[1]:.1f}" fill="{left_color}" stroke="{border_color}" stroke-width="0.3"/>')
                # Right Face
                polys.append(f'<polygon points="{p2[0]:.1f},{p2[1]:.1f} {p1[0]:.1f},{p1[1]:.1f} {p6[0]:.1f},{p6[1]:.1f} {p5[0]:.1f},{p5[1]:.1f}" fill="{right_color}" stroke="{border_color}" stroke-width="0.3"/>')
            
            # Top Face
            polys.append(f'<polygon points="{p0[0]:.1f},{p0[1]:.1f} {p1[0]:.1f},{p1[1]:.1f} {p2[0]:.1f},{p2[1]:.1f} {p3[0]:.1f},{p3[1]:.1f}" fill="{top_color}" stroke="{border_color}" stroke-width="0.3"/>')

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  <rect width="{width}" height="{height}" rx="12" fill="{bg_color}" stroke="{border_color}" stroke-width="1"/>
  
  <g transform="translate(24, 30)">
    <circle cx="6" cy="-4" r="5" fill="#38bdf8"/>
    <text x="20" y="0" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif" font-size="13" font-weight="700" fill="{text_color}" letter-spacing="0.5">3D ISOMETRIC CONTRIBUTION GRAPH</text>
    <text x="{width - 48}" y="0" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif" font-size="11" font-weight="500" fill="{subtext_color}" text-anchor="end">Half-Year Activity Projection</text>
  </g>
  <line x1="24" y1="42" x2="{width - 24}" y2="42" stroke="{border_color}" stroke-width="1"/>

  <g transform="translate(0, 10)">
    {''.join(polys)}
  </g>
</svg>"""

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Generated 3D Isometric Calendar: {output_path}")

if __name__ == "__main__":
    render_isocalendar_svg("assets/metrics.isocalendar.svg")
