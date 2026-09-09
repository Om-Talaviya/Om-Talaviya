#!/usr/bin/env python3
"""
radar.py - Dual Theme Radar Chart Generator
Generates self-rated skill radars or live GitHub repository language radars
with dark/light theme support, custom curves, and clean vector geometry.
"""

import argparse
import json
import math
import os
import sys
import urllib.request
import urllib.error


DEFAULT_EXCLUDES = [
    "html", "css", "shell", "makefile", "dockerfile", "batchfile", "procfile",
    "powershell", "cmake", "tex", "jupyter notebook"
]


def fetch_github_languages(username, token=None, excludes=None, limit=7, curve=0.4):
    excludes = [e.lower().strip() for e in (excludes or DEFAULT_EXCLUDES)]
    
    headers = {
        "User-Agent": f"{username}-profile-generator",
        "Accept": "application/vnd.github.v3+json"
    }
    if token:
        headers["Authorization"] = f"token {token}"
    
    # 1. Fetch public repos
    url = f"https://api.github.com/users/{username}/repos?per_page=100&type=owner"
    req = urllib.request.Request(url, headers=headers)
    
    try:
        with urllib.request.urlopen(req) as resp:
            repos = json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as e:
        print(f"Warning: Could not fetch GitHub repos ({e}). Using cached/fallback languages.", file=sys.stderr)
        return get_fallback_languages()

    lang_totals = {}

    for repo in repos:
        if repo.get("fork"):
            continue
        lang_url = repo.get("languages_url")
        if not lang_url:
            continue
        
        try:
            req_l = urllib.request.Request(lang_url, headers=headers)
            with urllib.request.urlopen(req_l) as resp_l:
                langs = json.loads(resp_l.read().decode("utf-8"))
                for lang_name, byte_count in langs.items():
                    if lang_name.lower() in excludes:
                        continue
                    lang_totals[lang_name] = lang_totals.get(lang_name, 0) + byte_count
        except Exception as err:
            print(f"Notice: Skip repo language fetch ({err})", file=sys.stderr)
            continue

    if not lang_totals:
        print("Notice: No languages found. Using fallback languages.", file=sys.stderr)
        return get_fallback_languages()

    # Sort languages by byte count descending
    sorted_langs = sorted(lang_totals.items(), key=lambda x: x[1], reverse=True)[:limit]
    
    # Apply curve scaling (log-like power scale so top language doesn't overshadow others)
    max_bytes = sorted_langs[0][1] if sorted_langs else 1
    
    axes = []
    for lang, b_count in sorted_langs:
        # Scale to 0..100 using power curve
        ratio = b_count / max_bytes
        val = int(round((ratio ** curve) * 100))
        val = max(25, min(100, val)) # Keep legible bounds
        axes.append({
            "label": lang,
            "value": val,
            "raw_bytes": b_count
        })

    return {
        "title": "Language Distribution",
        "axes": axes
    }


def get_fallback_languages():
    return {
        "title": "Language Distribution",
        "axes": [
            { "label": "Python", "value": 94, "raw_bytes": 1250000 },
            { "label": "TypeScript", "value": 86, "raw_bytes": 780000 },
            { "label": "JavaScript", "value": 78, "raw_bytes": 450000 },
            { "label": "SQL / Vector", "value": 72, "raw_bytes": 280000 },
            { "label": "C++", "value": 65, "raw_bytes": 150000 }
        ]
    }


def render_radar_svg(data, theme="dark", accent="#38bdf8", show_values=True, width=420, height=380):
    axes = data.get("axes", [])
    title = data.get("title", "Radar Chart")
    n = len(axes)
    if n < 3:
        raise ValueError("Radar chart requires at least 3 axes.")

    cx = width / 2.0
    cy = (height / 2.0) + 12
    max_r = min(width, height) * 0.33

    # Theme colors
    if theme == "dark":
        bg_color = "#0d1117"
        card_border = "#30363d"
        text_primary = "#f0f6fc"
        text_secondary = "#8b949e"
        grid_stroke = "#21262d"
        axis_stroke = "#30363d"
        accent_color = accent
        fill_opacity = "0.22"
        badge_bg = "rgba(56, 189, 248, 0.12)"
    else:
        bg_color = "#ffffff"
        card_border = "#d0d7de"
        text_primary = "#1f2328"
        text_secondary = "#656d76"
        grid_stroke = "#eaeef2"
        axis_stroke = "#d0d7de"
        accent_color = "#0284c7" if accent == "#38bdf8" else accent
        fill_opacity = "0.20"
        badge_bg = "rgba(2, 132, 199, 0.10)"

    # Angle helper: top is -pi/2
    def get_coords(index, radius):
        angle = (2 * math.pi / n) * index - (math.pi / 2)
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)
        return x, y, angle

    svg_elements = []

    # 1. Background Card
    svg_elements.append(
        f'  <rect width="{width}" height="{height}" rx="12" fill="{bg_color}" stroke="{card_border}" stroke-width="1"/>'
    )

    # 2. Card Header
    svg_elements.append(
        f'  <text x="{width/2}" y="32" font-family="-apple-system, BlinkMacSystemFont, \'Segoe UI\', Roboto, Helvetica, Arial, sans-serif" font-size="14" font-weight="700" fill="{text_primary}" text-anchor="middle" letter-spacing="0.5">{title.upper()}</text>'
    )
    svg_elements.append(
        f'  <line x1="{width*0.25}" y1="44" x2="{width*0.75}" y2="44" stroke="{accent_color}" stroke-opacity="0.35" stroke-width="1.5" stroke-linecap="round"/>'
    )

    # 3. Concentric Grid Polygons
    levels = [0.2, 0.4, 0.6, 0.8, 1.0]
    for lvl in levels:
        poly_pts = []
        for i in range(n):
            px, py, _ = get_coords(i, max_r * lvl)
            poly_pts.append(f"{px:.1f},{py:.1f}")
        pts_str = " ".join(poly_pts)
        svg_elements.append(
            f'  <polygon points="{pts_str}" fill="none" stroke="{grid_stroke}" stroke-width="1" stroke-dasharray="{"none" if lvl == 1.0 else "3,3"}"/>'
        )

    # 4. Radial Spokes
    for i in range(n):
        px, py, _ = get_coords(i, max_r)
        svg_elements.append(
            f'  <line x1="{cx:.1f}" y1="{cy:.1f}" x2="{px:.1f}" y2="{py:.1f}" stroke="{axis_stroke}" stroke-width="1"/>'
        )

    # 5. Data Polygon & Glow
    data_pts = []
    vertex_elements = []
    for i, axis in enumerate(axes):
        val = max(0, min(100, axis.get("value", 50)))
        r_val = (val / 100.0) * max_r
        px, py, angle = get_coords(i, r_val)
        data_pts.append(f"{px:.1f},{py:.1f}")
        
        # Vertex point
        vertex_elements.append(
            f'  <circle cx="{px:.1f}" cy="{py:.1f}" r="4" fill="{accent_color}" stroke="{bg_color}" stroke-width="2"/>'
        )

    data_pts_str = " ".join(data_pts)
    
    # Polygon Area
    svg_elements.append(
        f'  <polygon points="{data_pts_str}" fill="{accent_color}" fill-opacity="{fill_opacity}" stroke="{accent_color}" stroke-width="2.5" stroke-linejoin="round"/>'
    )
    svg_elements.extend(vertex_elements)

    # 6. Labels and Values
    for i, axis in enumerate(axes):
        label = axis.get("label", "")
        val = axis.get("value", "")
        px, py, angle = get_coords(i, max_r + 24)

        cos_a = math.cos(angle)
        sin_a = math.sin(angle)

        if abs(cos_a) < 0.15:
            anchor = "middle"
        elif cos_a > 0:
            anchor = "start"
        else:
            anchor = "end"

        # Shift text slightly for visual balance
        text_y = py + 4

        display_text = f"{label}"
        if show_values and val != "":
            display_text += f" ({val})"

        label_color = text_primary if theme == "dark" else "#24292f"
        svg_elements.append(
            f'  <text x="{px:.1f}" y="{text_y:.1f}" font-family="-apple-system, BlinkMacSystemFont, \'Segoe UI\', Roboto, Helvetica, Arial, sans-serif" font-size="11" font-weight="600" fill="{label_color}" text-anchor="{anchor}">{display_text}</text>'
        )

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
{chr(10).join(svg_elements)}
</svg>"""
    return svg


def main():
    parser = argparse.ArgumentParser(description="Generate dark and light radar SVGs.")
    parser.add_argument("--data", help="JSON file containing radar data (skills.json)")
    parser.add_argument("--github", help="GitHub username to aggregate languages for")
    parser.add_argument("--token", help="GitHub API token (optional)")
    parser.add_argument("-o", "--out", default="assets/radar", help="Output file prefix")
    parser.add_argument("--limit", type=int, default=7, help="Max number of axes (default: 7)")
    parser.add_argument("--curve", type=float, default=0.4, help="Scale curve factor (default: 0.4)")
    parser.add_argument("--exclude", default="", help="Comma-separated languages to exclude")
    parser.add_argument("--values", action="store_true", default=True, help="Display numerical values on labels")
    parser.add_argument("--accent", default="#38bdf8", help="Accent color (default: #38bdf8)")

    args = parser.parse_args()

    if args.github:
        excludes = [x.strip() for x in args.exclude.split(",") if x.strip()] if args.exclude else DEFAULT_EXCLUDES
        data = fetch_github_languages(
            args.github,
            token=args.token or os.getenv("GITHUB_TOKEN"),
            excludes=excludes,
            limit=args.limit,
            curve=args.curve
        )
    elif args.data and os.path.exists(args.data):
        with open(args.data, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        print("Error: Specify either --data <json_file> or --github <username>", file=sys.stderr)
        sys.exit(1)

    out_dir = os.path.dirname(args.out)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    dark_svg = render_radar_svg(data, theme="dark", accent=args.accent, show_values=args.values)
    light_svg = render_radar_svg(data, theme="light", accent=args.accent, show_values=args.values)

    with open(f"{args.out}-dark.svg", "w", encoding="utf-8") as f:
        f.write(dark_svg)
    with open(f"{args.out}-light.svg", "w", encoding="utf-8") as f:
        f.write(light_svg)

    print(f"Generated: {args.out}-dark.svg and {args.out}-light.svg")


if __name__ == "__main__":
    main()
