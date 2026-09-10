#!/usr/bin/env python3
"""
generate_animated_hero.py - Creates an ultra-crisp, optimized animated hero portrait for GitHub README (< 2.0 MB)
"""

import math
import os
import sys
from PIL import Image, ImageEnhance, ImageFilter, ImageChops

def create_animated_hero(
    source_path="assets/hero-portrait.png",
    output_gif="assets/hero-portrait-animated.gif",
    target_size=(500, 500),
    num_frames=20,
    frame_duration_ms=115,
    num_colors=160
):
    print(f"Loading source portrait from: {source_path}", flush=True)
    orig_img = Image.open(source_path).convert("RGBA")
    
    # Scale base image to target size (500x500, 1.47x crisp retina for 340px README display)
    base_img = orig_img.resize(target_size, Image.Resampling.LANCZOS)
    w, h = target_size
    
    r, g, b, alpha = base_img.split()
    base_rgb = Image.merge("RGB", (r, g, b))
    
    # Edge mask for subtle warm rim flare along portrait contour
    edge_mask = alpha.filter(ImageFilter.FIND_EDGES).filter(ImageFilter.GaussianBlur(radius=2.0))
    
    frames_rgba = []
    
    for i in range(num_frames):
        t = i / num_frames
        # Smooth cosine cycle: 0 -> 1 -> 0 for perfectly seamless looping
        cycle = (1.0 - math.cos(2 * math.pi * t)) / 2.0
        
        # 1. Subtle cinematic push-in (0% to 2.0% zoom)
        zoom = 1.0 + (0.020 * cycle)
        new_w = int(w * zoom)
        new_h = int(h * zoom)
        
        scaled_rgb = base_rgb.resize((new_w, new_h), Image.Resampling.BILINEAR)
        scaled_alpha = alpha.resize((new_w, new_h), Image.Resampling.BILINEAR)
        
        crop_x = (new_w - w) // 2
        crop_y = int((new_h - h) * 0.40)
        
        frame_rgb = scaled_rgb.crop((crop_x, crop_y, crop_x + w, crop_y + h))
        frame_alpha = scaled_alpha.crop((crop_x, crop_y, crop_x + w, crop_y + h))
        
        # 2. Exposure & Contrast Breathing
        brightness_val = 1.0 + (0.045 * cycle)
        enhancer_b = ImageEnhance.Brightness(frame_rgb)
        frame_rgb = enhancer_b.enhance(brightness_val)
        
        contrast_val = 1.0 + (0.025 * cycle)
        enhancer_c = ImageEnhance.Contrast(frame_rgb)
        frame_rgb = enhancer_c.enhance(contrast_val)
        
        # 3. Subtle Warm Ambient Rim-Light Flare
        warm_overlay = Image.new("RGB", (w, h), (255, 140, 45))
        glow_intensity = int(32 * cycle)
        if glow_intensity > 0:
            frame_edge = edge_mask.resize((new_w, new_h), Image.Resampling.BILINEAR).crop((crop_x, crop_y, crop_x + w, crop_y + h))
            frame_edge_pulse = frame_edge.point(lambda p: int(p * (glow_intensity / 255.0)))
            frame_rgb = Image.composite(ImageChops.screen(frame_rgb, warm_overlay), frame_rgb, frame_edge_pulse)
        
        fr_r, fr_g, fr_b = frame_rgb.split()
        final_frame = Image.merge("RGBA", (fr_r, fr_g, fr_b, frame_alpha))
        frames_rgba.append(final_frame)

    print(f"Generated {len(frames_rgba)} frames. Building unified global color palette...", flush=True)

    # Compute optimal global palette across all frames for maximum compression efficiency
    combined = Image.new("RGBA", (w * len(frames_rgba), h))
    for idx, fr in enumerate(frames_rgba):
        combined.paste(fr, (idx * w, 0))
    
    matte_bg = Image.new("RGB", combined.size, (13, 17, 23))
    matte_bg.paste(combined, mask=combined.split()[3])
    global_pal_img = matte_bg.quantize(colors=num_colors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)

    quantized_frames = []
    for f in frames_rgba:
        a = f.split()[3]
        bg = Image.new("RGB", (w, h), (13, 17, 23))
        bg.paste(f, mask=a)
        
        # Map frame to optimal global palette
        p_frame = bg.quantize(palette=global_pal_img, dither=Image.Dither.NONE)
        
        a_bytes = a.tobytes()
        p_bytes = p_frame.tobytes()
        new_p_bytes = bytearray(p_bytes)
        
        # Clean threshold for transparent boundary
        for pi in range(w * h):
            if a_bytes[pi] < 30:
                new_p_bytes[pi] = 255
                
        p_frame.frombytes(bytes(new_p_bytes))
        quantized_frames.append(p_frame)

    os.makedirs(os.path.dirname(output_gif), exist_ok=True)
    quantized_frames[0].save(
        output_gif,
        save_all=True,
        append_images=quantized_frames[1:],
        duration=frame_duration_ms,
        loop=0,
        disposal=2,
        transparency=255,
        optimize=True
    )
    
    size_bytes = os.path.getsize(output_gif)
    size_mb = size_bytes / (1024.0 * 1024.0)
    print(f"Saved Optimized Animated Hero GIF: {output_gif}", flush=True)
    print(f"  Dimensions: {w}x{h} px", flush=True)
    print(f"  Frames: {num_frames} frames", flush=True)
    print(f"  Duration: {(num_frames * frame_duration_ms) / 1000.0:.2f}s", flush=True)
    print(f"  File Size: {size_mb:.2f} MB ({size_bytes:,} bytes)", flush=True)

if __name__ == "__main__":
    create_animated_hero()
