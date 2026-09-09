#!/usr/bin/env python3
"""
dotify.py - Dot-Matrix SVG Portrait Generator
Converts any image into a sleek, responsive dot-matrix SVG portrait
with histogram equalization, edge-detail preservation, and CSS animations.
"""

import argparse
import math
import os
import sys

try:
    from PIL import Image, ImageEnhance, ImageFilter, ImageOps
except ImportError:
    print("Pillow is required. Install with: pip install pillow", file=sys.stderr)
    sys.exit(1)


def create_default_avatar_image(width=400, height=400):
    """Creates an elegant default developer/AI engineer silhouette if no image provided."""
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    from PIL import ImageDraw
    draw = ImageDraw.Draw(img)
    
    # Head
    head_center = (width // 2, int(height * 0.38))
    head_radius = int(width * 0.22)
    draw.ellipse([
        head_center[0] - head_radius,
        head_center[1] - head_radius,
        head_center[0] + head_radius,
        head_center[1] + head_radius
    ], fill=(220, 230, 245, 255))
    
    # Shoulders / Torso
    torso_top = int(height * 0.65)
    torso_radius_x = int(width * 0.42)
    torso_radius_y = int(height * 0.35)
    draw.ellipse([
        width // 2 - torso_radius_x,
        torso_top,
        width // 2 + torso_radius_x,
        torso_top + torso_radius_y * 2
    ], fill=(180, 200, 225, 255))
    
    # Subtle glasses / tech visor outline
    glasses_y = int(height * 0.36)
    glasses_w = int(width * 0.14)
    glasses_h = int(height * 0.07)
    draw.rounded_rectangle([
        head_center[0] - glasses_w - 6, glasses_y,
        head_center[0] - 6, glasses_y + glasses_h
    ], radius=6, fill=(40, 60, 90, 255))
    draw.rounded_rectangle([
        head_center[0] + 6, glasses_y,
        head_center[0] + glasses_w + 6, glasses_y + glasses_h
    ], radius=6, fill=(40, 60, 90, 255))
    draw.line([head_center[0] - 6, glasses_y + glasses_h // 2, head_center[0] + 6, glasses_y + glasses_h // 2], fill=(40, 60, 90, 255), width=3)
    
    return img


def process_image(img, cols=88, equalize=True, detail=0.5, circle=False, square=False, focus=(0.5, 0.5), invert=False):
    # Handle transparency
    if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
        rgba = img.convert("RGBA")
        alpha = rgba.split()[-1]
    else:
        rgba = img.convert("RGBA")
        alpha = Image.new("L", rgba.size, 255)

    # Square crop if requested
    w, h = rgba.size
    if square:
        dim = min(w, h)
        fx, fy = focus
        cx = int(w * fx)
        cy = int(h * fy)
        left = max(0, min(cx - dim // 2, w - dim))
        top = max(0, min(cy - dim // 2, h - dim))
        rgba = rgba.crop((left, top, left + dim, top + dim))
        alpha = alpha.crop((left, top, left + dim, top + dim))
        w, h = dim, dim

    aspect = h / w
    rows = max(1, int(cols * aspect))

    # Resize alpha and image
    alpha_small = alpha.resize((cols, rows), Image.Resampling.BILINEAR)
    img_small = rgba.resize((cols, rows), Image.Resampling.BILINEAR)

    # Convert to grayscale for brightness analysis
    gray = img_small.convert("L")

    if equalize:
        # Masked equalization if alpha exists
        gray = ImageOps.equalize(gray)

    if detail > 0:
        # Unsharp mask for edge preservation
        blurred = gray.filter(ImageFilter.GaussianBlur(radius=1.2))
        high_pass = ImageEnhance.Contrast(gray).enhance(1.0 + detail)
        gray = Image.blend(gray, high_pass, min(1.0, detail))

    return img_small, gray, alpha_small, cols, rows


def generate_svg(img_small, gray, alpha_small, cols, rows, accent="#38bdf8", color_mode=False,
                 reveal=True, reveal_time=2.5, reveal_fade=0.45, reveal_dir="down",
                 animate=False, circle=False, invert=False, mode="dots", theme="dark"):
    
    cell_size = 10
    svg_w = cols * cell_size
    svg_h = rows * cell_size
    max_radius = (cell_size / 2) * 0.92

    css = []
    
    if reveal:
        css.append("""
        @keyframes dotReveal {
            0% { opacity: 0; transform: scale(0); }
            60% { opacity: 0.8; transform: scale(1.15); }
            100% { opacity: 1; transform: scale(1); }
        }
        .dot {
            transform-origin: center;
            animation: dotReveal var(--fade-duration, 0.45s) cubic-bezier(0.16, 1, 0.3, 1) forwards;
            opacity: 0;
        }
        """)

    if animate:
        css.append("""
        @keyframes shimmerWave {
            0%, 100% { opacity: 0.35; transform: scale(0.85); }
            50% { opacity: 1; transform: scale(1.08); }
        }
        .shimmer {
            animation: shimmerWave 3.5s ease-in-out infinite;
        }
        """)

    elements = []
    
    # Calculate radius and colors
    cx_center = cols / 2.0
    cy_center = rows / 2.0
    max_dist = math.sqrt(cx_center**2 + cy_center**2)

    for y in range(rows):
        for x in range(cols):
            a = alpha_small.getpixel((x, y))
            if a < 15:
                continue

            b = gray.getpixel((x, y))
            if invert:
                b = 255 - b

            # Brightness to radius
            # Normalized 0.0 to 1.0
            norm_b = b / 255.0
            
            # Feathered circular mask if requested
            if circle:
                dist = math.sqrt((x - cx_center)**2 + (y - cy_center)**2)
                edge_factor = 1.0 - smoothstep(cx_center * 0.82, cx_center * 0.98, dist)
                if edge_factor <= 0.01:
                    continue
                norm_b *= edge_factor

            r = norm_b * max_radius
            if r < 0.5:
                continue

            cx = x * cell_size + cell_size / 2.0
            cy = y * cell_size + cell_size / 2.0

            # Determine color
            if color_mode:
                orig_r, orig_g, orig_b, _ = img_small.getpixel((x, y))
                fill = f"rgb({orig_r},{orig_g},{orig_b})"
            else:
                if theme == "dark":
                    # Gradient tone from bright accent to subdued tech blue
                    alpha_val = 0.25 + 0.75 * norm_b
                    fill = accent
                else:
                    # Light mode: darker high-contrast accent
                    fill = "#0369a1" if accent == "#38bdf8" else accent

            # Animation delay
            style_attrs = []
            classes = ["dot"] if reveal else []
            if animate:
                classes.append("shimmer")

            if reveal:
                if reveal_dir == "down":
                    delay = (y / rows) * reveal_time
                elif reveal_dir == "up":
                    delay = ((rows - 1 - y) / rows) * reveal_time
                else:
                    dist = math.sqrt((x - cx_center)**2 + (y - cy_center)**2)
                    delay = (dist / max_dist) * reveal_time
                
                style_attrs.append(f"animation-delay: {delay:.3f}s; --fade-duration: {reveal_fade:.3f}s;")

            if animate:
                anim_delay = (x / cols) * 2.0
                style_attrs.append(f"animation-delay: {anim_delay:.3f}s;")

            style_str = f' style="{" ".join(style_attrs)}"' if style_attrs else ""
            class_str = f' class="{" ".join(classes)}"' if classes else ""

            if mode == "dots":
                opacity_str = f' fill-opacity="{0.35 + 0.65 * norm_b:.2f}"' if not color_mode else ""
                elements.append(
                    f'  <circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.2f}" fill="{fill}"{opacity_str}{class_str}{style_str}/>'
                )
            elif mode == "binary":
                char = "1" if norm_b > 0.5 else "0"
                font_sz = cell_size * 0.95
                elements.append(
                    f'  <text x="{cx:.1f}" y="{cy + font_sz*0.35:.1f}" font-family="monospace" font-weight="700" font-size="{font_sz:.1f}" fill="{fill}" text-anchor="middle"{class_str}{style_str}>{char}</text>'
                )

    style_block = f"<style>\n{''.join(css)}\n</style>" if css else ""

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_w} {svg_h}" width="{svg_w}" height="{svg_h}">
{style_block}
<g>
{chr(10).join(elements)}
</g>
</svg>"""
    return svg


def smoothstep(edge0, edge1, x):
    t = max(0.0, min(1.0, (x - edge0) / (edge1 - edge0)))
    return t * t * (3.0 - 2.0 * t)


def main():
    parser = argparse.ArgumentParser(description="Convert an image to a dot-matrix SVG portrait.")
    parser.add_argument("image", nargs="?", default=None, help="Input image path (optional)")
    parser.add_argument("-o", "--out", default="assets/portrait", help="Output path without extension")
    parser.add_argument("--cols", type=int, default=88, help="Number of horizontal dots (default: 88)")
    parser.add_argument("--equalize", action="store_true", default=True, help="Equalize brightness histogram")
    parser.add_argument("--detail", type=float, default=0.5, help="High-pass detail sharpness (0.0 to 1.5)")
    parser.add_argument("--color", action="store_true", help="Preserve source image colors")
    parser.add_argument("--accent", default="#38bdf8", help="Accent hex color (default: #38bdf8)")
    parser.add_argument("--reveal", action="store_true", default=True, help="Enable entry sweep animation")
    parser.add_argument("--reveal-time", type=float, default=2.2, help="Reveal animation duration (seconds)")
    parser.add_argument("--reveal-fade", type=float, default=0.4, help="Individual row fade duration")
    parser.add_argument("--reveal-dir", default="down", choices=["down", "up", "radial"], help="Sweep direction")
    parser.add_argument("--animate", action="store_true", help="Enable continuous shimmer wave")
    parser.add_argument("--circle", action="store_true", default=True, help="Crop with smooth circular vignette")
    parser.add_argument("--square", action="store_true", default=True, help="Crop to 1:1 aspect ratio")
    parser.add_argument("--focus", default="0.5,0.45", help="Crop center focus point x,y")
    parser.add_argument("--invert", action="store_true", help="Invert brightness")
    parser.add_argument("--mode", default="dots", choices=["dots", "binary"], help="Rendering mode")

    args = parser.parse_args()

    fx, fy = map(float, args.focus.split(","))

    if args.image and os.path.exists(args.image):
        print(f"Loading portrait from: {args.image}")
        img = Image.open(args.image)
    else:
        print("No portrait image provided. Generating modern AI/Software Engineer dot-matrix avatar...")
        img = create_default_avatar_image()

    out_dir = os.path.dirname(args.out)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    img_small, gray, alpha_small, cols, rows = process_image(
        img,
        cols=args.cols,
        equalize=args.equalize,
        detail=args.detail,
        circle=args.circle,
        square=args.square,
        focus=(fx, fy),
        invert=args.invert
    )

    if args.color:
        svg_content = generate_svg(
            img_small, gray, alpha_small, cols, rows,
            accent=args.accent, color_mode=True, reveal=args.reveal,
            reveal_time=args.reveal_time, reveal_fade=args.reveal_fade,
            reveal_dir=args.reveal_dir, animate=args.animate,
            circle=args.circle, invert=args.invert, mode=args.mode, theme="dark"
        )
        out_path = f"{args.out}.svg"
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(svg_content)
        print(f"Generated: {out_path}")
    else:
        # Generate dark and light pair
        dark_svg = generate_svg(
            img_small, gray, alpha_small, cols, rows,
            accent=args.accent, color_mode=False, reveal=args.reveal,
            reveal_time=args.reveal_time, reveal_fade=args.reveal_fade,
            reveal_dir=args.reveal_dir, animate=args.animate,
            circle=args.circle, invert=args.invert, mode=args.mode, theme="dark"
        )
        light_svg = generate_svg(
            img_small, gray, alpha_small, cols, rows,
            accent="#0284c7", color_mode=False, reveal=args.reveal,
            reveal_time=args.reveal_time, reveal_fade=args.reveal_fade,
            reveal_dir=args.reveal_dir, animate=args.animate,
            circle=args.circle, invert=args.invert, mode=args.mode, theme="light"
        )

        with open(f"{args.out}-dark.svg", "w", encoding="utf-8") as f:
            f.write(dark_svg)
        with open(f"{args.out}-light.svg", "w", encoding="utf-8") as f:
            f.write(light_svg)
        with open(f"{args.out}.svg", "w", encoding="utf-8") as f:
            f.write(dark_svg)
        print(f"Generated: {args.out}-dark.svg, {args.out}-light.svg, {args.out}.svg")


if __name__ == "__main__":
    main()
