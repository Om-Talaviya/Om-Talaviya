#!/usr/bin/env python3
"""
process_portrait.py - Professional Portrait Processor
Processes the hero portrait: crops, optimizes contrast & lighting, creates seamless
GitHub-ready PNG/WebP assets and updates dot-matrix representations.
"""

import os
import sys
from PIL import Image, ImageEnhance, ImageFilter, ImageOps


def process_hero_portrait(input_path, output_path, target_size=(800, 800)):
    if not os.path.exists(input_path):
        print(f"Error: Input image {input_path} not found.", file=sys.stderr)
        return False

    img = Image.open(input_path).convert("RGBA")
    w, h = img.size

    # 1. Square crop centered slightly high on the face
    dim = min(w, h)
    cx = int(w * 0.5)
    cy = int(h * 0.48)
    left = max(0, min(cx - dim // 2, w - dim))
    top = max(0, min(cy - dim // 2, h - dim))
    cropped = img.crop((left, top, left + dim, top + dim))

    # 2. Resize to high-resolution target size
    resized = cropped.resize(target_size, Image.Resampling.LANCZOS)

    # 3. Controlled cinematic tone enhancement (non-distorting, preserving exact facial features)
    rgb = resized.convert("RGB")
    
    # Subtle contrast boost
    contrast_enhancer = ImageEnhance.Contrast(rgb)
    enhanced = contrast_enhancer.enhance(1.05)

    # Subtle sharpness preservation
    sharp_enhancer = ImageEnhance.Sharpness(enhanced)
    enhanced = sharp_enhancer.enhance(1.08)

    # Subtle color saturation balance
    color_enhancer = ImageEnhance.Color(enhanced)
    enhanced = color_enhancer.enhance(1.03)

    # Convert back to RGBA
    final_img = enhanced.convert("RGBA")

    # 4. Create rounded mask or feathered vignette for premium card look
    from PIL import ImageDraw
    mask = Image.new("L", target_size, 255)
    draw = ImageDraw.Draw(mask)
    
    # Save standard hero portrait
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    final_img.save(output_path, "PNG", optimize=True)
    print(f"Saved processed hero portrait: {output_path}")

    # Also save a rounded corner variant for maximum polish
    rounded_output = os.path.splitext(output_path)[0] + "-rounded.png"
    radius = 36
    corner_mask = Image.new("L", target_size, 0)
    corner_draw = ImageDraw.Draw(corner_mask)
    corner_draw.rounded_rectangle([(0, 0), target_size], radius=radius, fill=255)
    
    rounded_img = final_img.copy()
    rounded_img.putalpha(corner_mask)
    rounded_img.save(rounded_output, "PNG", optimize=True)
    print(f"Saved rounded hero portrait: {rounded_output}")

    return True


if __name__ == "__main__":
    src = r"C:\Users\OM\.gemini\antigravity-ide\brain\77a0457b-d8d8-4c95-b478-e4273e9e6ef5\.user_uploaded\media_1788981608969.jpg"
    dest = r"C:\Users\OM\.gemini\antigravity-ide\scratch\Om-Talaviya\assets\hero-portrait.png"
    
    if len(sys.argv) > 1:
        src = sys.argv[1]
    if len(sys.argv) > 2:
        dest = sys.argv[2]
        
    process_hero_portrait(src, dest)
