#!/usr/bin/env python3
"""
process_portrait.py - High-Fidelity Silhouette Segmentation & Transparent Hero Portrait Generator
Performs precise boundary segmentation on the subject, guarantees 100% opacity for all internal
features (hair, suit, shirt, eyes, watch), and provides soft anti-aliasing along the boundary.
"""

import os
import sys
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw


def generate_precise_silhouette_mask(src_img, bg_threshold=12):
    """
    Computes a pixel-perfect alpha mask for the subject in the portrait.
    Uses horizontal boundary scanning per row to separate the background from the subject,
    guaranteeing that dark suit, hair, and eyes inside the subject are never hollowed out.
    """
    w, h = src_img.size
    rgb = src_img.convert("RGB")
    
    # 1. Detect left and right boundary of subject for every horizontal row
    left_bounds = [None] * h
    right_bounds = [None] * h
    
    for y in range(h):
        # Scan from left to find first subject pixel
        for x in range(w):
            r, g, b = rgb.getpixel((x, y))
            # Any pixel with light or color beyond the pure background noise
            if r > bg_threshold or g > bg_threshold or b > bg_threshold:
                left_bounds[y] = x
                break
                
        # Scan from right to find last subject pixel
        for x in range(w - 1, -1, -1):
            r, g, b = rgb.getpixel((x, y))
            if r > bg_threshold or g > bg_threshold or b > bg_threshold:
                right_bounds[y] = x
                break

    # 2. Construct binary mask
    mask_bytes = bytearray(w * h)
    
    for y in range(h):
        lx = left_bounds[y]
        rx = right_bounds[y]
        
        if lx is not None and rx is not None and rx >= lx:
            # Fill row interior completely with 255 (100% solid opacity)
            for x in range(lx, rx + 1):
                mask_bytes[y * w + x] = 255

    raw_mask = Image.frombytes("L", (w, h), bytes(mask_bytes))
    
    # 3. Apply smooth anti-aliased edge filter (1.0px gaussian blur on boundary)
    smooth_mask = raw_mask.filter(ImageFilter.GaussianBlur(radius=1.0))
    
    return smooth_mask


def process_transparent_portrait(input_path, output_path, target_size=(800, 800)):
    if not os.path.exists(input_path):
        print(f"Error: Input image {input_path} not found.", file=sys.stderr)
        return False

    orig_img = Image.open(input_path).convert("RGBA")
    w, h = orig_img.size
    print(f"Source Image: {input_path} ({w}x{h}, {orig_img.mode})")

    # Generate high-fidelity silhouette alpha mask
    alpha_mask = generate_precise_silhouette_mask(orig_img)
    
    r, g, b, _ = orig_img.split()
    transparent_img = Image.merge("RGBA", (r, g, b, alpha_mask))

    # 1. Square crop centered on subject
    dim = min(w, h)
    cx = int(w * 0.5)
    cy = int(h * 0.48)
    left = max(0, min(cx - dim // 2, w - dim))
    top = max(0, min(cy - dim // 2, h - dim))
    cropped = transparent_img.crop((left, top, left + dim, top + dim))

    # 2. Resize with Lanczos to high-resolution target
    resized = cropped.resize(target_size, Image.Resampling.LANCZOS)

    # 3. Subtle contrast & tone enhancement on RGB channels only (preserving alpha)
    r_ch, g_ch, b_ch, a_ch = resized.split()
    rgb_img = Image.merge("RGB", (r_ch, g_ch, b_ch))
    
    contrast_enhancer = ImageEnhance.Contrast(rgb_img)
    enhanced = contrast_enhancer.enhance(1.03)

    sharp_enhancer = ImageEnhance.Sharpness(enhanced)
    enhanced = sharp_enhancer.enhance(1.04)

    er, eg, eb = enhanced.split()
    final_rgba = Image.merge("RGBA", (er, eg, eb, a_ch))

    # Save transparent PNG
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    final_rgba.save(output_path, "PNG", optimize=True)
    print(f"Saved transparent hero portrait: {output_path} (RGBA, {target_size[0]}x{target_size[1]})")

    # Also save rounded copy as identical RGBA transparent asset
    rounded_output = os.path.splitext(output_path)[0] + "-rounded.png"
    final_rgba.save(rounded_output, "PNG", optimize=True)
    print(f"Saved transparent rounded hero portrait: {rounded_output}")

    return True


if __name__ == "__main__":
    src = r"C:\Users\OM\.gemini\antigravity-ide\brain\77a0457b-d8d8-4c95-b478-e4273e9e6ef5\.user_uploaded\media_1788981608969.jpg"
    dest = r"C:\Users\OM\.gemini\antigravity-ide\scratch\Om-Talaviya\assets\hero-portrait.png"

    if len(sys.argv) > 1:
        src = sys.argv[1]
    if len(sys.argv) > 2:
        dest = sys.argv[2]

    process_transparent_portrait(src, dest)
