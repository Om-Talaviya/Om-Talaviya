#!/usr/bin/env python3
"""
generate_animated_hero.py - Single-play (stops on final photo) Dot Assembly with 100% exact photo color matching.
"""

import math
import os
import random
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

def ease_out_quint(x):
    return 1 - math.pow(1 - x, 5)

def ease_in_out_sine(x):
    return -(math.cos(math.pi * x) - 1) / 2

def generate_exact_color_assembly(
    source_path="assets/hero-portrait.png",
    output_gif="assets/hero-portrait-scramble.gif",
    target_size=(500, 500),
    num_frames=26,
    frame_duration_ms=90,
    grid_step=8,
    num_colors=200
):
    print(f"Loading source portrait from: {source_path}", flush=True)
    orig_img = Image.open(source_path).convert("RGBA")
    base_img = orig_img.resize(target_size, Image.Resampling.LANCZOS)
    w, h = target_size
    
    r, g, b, alpha = base_img.split()
    base_rgb = Image.merge("RGB", (r, g, b))
    gray = base_img.convert("L")
    
    # Sample exact dots from image
    particles = []
    rng = random.Random(42)
    
    for y in range(grid_step // 2, h, grid_step):
        for x in range(grid_step // 2, w, grid_step):
            a_val = alpha.getpixel((x, y))
            if a_val > 35:
                # Exact color from the original photo
                col = base_rgb.getpixel((x, y))
                lum = gray.getpixel((x, y))
                
                # Size based on local luminance and alpha
                max_r = grid_step * 0.58
                radius = max(1.5, (lum / 255.0) * max_r * (a_val / 255.0))
                
                # Scramble coordinates
                dx = x - (w / 2)
                dy = y - (h / 2)
                dist_center = math.hypot(dx, dy)
                angle = math.atan2(dy, dx) + rng.uniform(-0.6, 0.6)
                
                scatter_dist = rng.uniform(80, 200) + (dist_center * rng.uniform(0.25, 0.6))
                x_scramble = x + math.cos(angle) * scatter_dist + rng.uniform(-30, 30)
                y_scramble = y + math.sin(angle) * scatter_dist + rng.uniform(-30, 30)
                
                stagger = rng.uniform(0.0, 0.30)
                
                particles.append({
                    'target_x': x,
                    'target_y': y,
                    'scramble_x': x_scramble,
                    'scramble_y': y_scramble,
                    'radius': radius,
                    'color': col, # 100% exact RGB from photo
                    'alpha': a_val,
                    'stagger': stagger
                })
                
    print(f"Sampled {len(particles)} exact-color portrait dots.", flush=True)

    frames_rgba = []
    
    # 26 frames total:
    # Frame 0 to 14 (0.0s - 1.35s): Scramble and fly in to exact grid positions
    # Frame 15 to 22 (1.35s - 2.05s): Cross-dissolve into full high-res photo
    # Frame 23 to 25 (2.05s - 2.34s): Pure final high-res photo (final frame holds permanently)
    
    assemble_frames = 15
    dissolve_frames = 8
    hold_frames = 3
    
    # 1. Assemble Phase
    for fi in range(assemble_frames):
        p_raw = fi / (assemble_frames - 1)
        frame_canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(frame_canvas)
        
        for p in particles:
            local_p = min(1.0, max(0.0, (p_raw - p['stagger']) / (1.0 - p['stagger'] + 0.001)))
            ease_p = ease_out_quint(local_p)
            
            cur_x = p['scramble_x'] + (p['target_x'] - p['scramble_x']) * ease_p
            cur_y = p['scramble_y'] + (p['target_y'] - p['scramble_y']) * ease_p
            
            p_alpha = int(p['alpha'] * min(1.0, 0.25 + (ease_p * 0.75)))
            r_cur = max(1.0, p['radius'] * (0.4 + 0.6 * ease_p))
            
            # Exact photo RGB with faded alpha
            col = (*p['color'], p_alpha)
            draw.ellipse([cur_x - r_cur, cur_y - r_cur, cur_x + r_cur, cur_y + r_cur], fill=col)
            
        frames_rgba.append(frame_canvas)

    # 2. Cross-Dissolve Phase
    # Create final dots image
    dots_full = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw_dots = ImageDraw.Draw(dots_full)
    for p in particles:
        draw_dots.ellipse([
            p['target_x'] - p['radius'], p['target_y'] - p['radius'],
            p['target_x'] + p['radius'], p['target_y'] + p['radius']
        ], fill=(*p['color'], p['alpha']))
        
    for di in range(1, dissolve_frames + 1):
        blend_val = ease_in_out_sine(di / dissolve_frames)
        blended = Image.blend(dots_full, base_img, blend_val)
        frames_rgba.append(blended)
        
    # 3. Final Pristine Photo Frame (holds indefinitely)
    for hi in range(hold_frames):
        frames_rgba.append(base_img.copy())

    print(f"Generated {len(frames_rgba)} frames. Building global color palette...", flush=True)

    # Build optimal global palette
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
        
        p_frame = bg.quantize(palette=global_pal_img, dither=Image.Dither.NONE)
        a_bytes = a.tobytes()
        p_bytes = p_frame.tobytes()
        new_p_bytes = bytearray(p_bytes)
        
        for pi in range(w * h):
            if a_bytes[pi] < 25:
                new_p_bytes[pi] = 255
                
        p_frame.frombytes(bytes(new_p_bytes))
        quantized_frames.append(p_frame)

    # Set loop=1 so it plays ONCE on page load and STOPS permanently on the final photo
    os.makedirs(os.path.dirname(output_gif), exist_ok=True)
    quantized_frames[0].save(
        output_gif,
        save_all=True,
        append_images=quantized_frames[1:],
        duration=frame_duration_ms,
        loop=1, # Plays once and stops on final frame
        disposal=2,
        transparency=255,
        optimize=True
    )
    
    # Also save as hero-portrait-animated.gif
    alt_output = "assets/hero-portrait-animated.gif"
    quantized_frames[0].save(
        alt_output,
        save_all=True,
        append_images=quantized_frames[1:],
        duration=frame_duration_ms,
        loop=1,
        disposal=2,
        transparency=255,
        optimize=True
    )
    
    size_mb = os.path.getsize(output_gif) / (1024.0 * 1024.0)
    print(f"Generated Single-Play Exact-Color Hero GIF: {output_gif} ({size_mb:.2f} MB, {len(frames_rgba)} frames, loop=1)", flush=True)

if __name__ == "__main__":
    generate_exact_color_assembly()
