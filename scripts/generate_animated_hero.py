#!/usr/bin/env python3
"""
generate_dot_assembly.py
Creates a futuristic Particle/Dot-Matrix Scramble-and-Assemble Animation for Om Talaviya's Hero Portrait.
Effect Sequence:
1. Particles start scattered/scrambled in space.
2. Particles converge and snap together into a structured dot-matrix portrait of Om.
3. A light sweep/hologram phase materializes the full photographic hero portrait.
4. Holds on the crystal-clear portrait with subtle ambient breathing.
5. Smoothly dissolves/scatters back into floating cyber dots for a seamless loop.
"""

import math
import os
import random
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageChops

def ease_in_out_cubic(x):
    return 4 * x * x * x if x < 0.5 else 1 - math.pow(-2 * x + 2, 3) / 2

def ease_out_quint(x):
    return 1 - math.pow(1 - x, 5)

def ease_in_out_sine(x):
    return -(math.cos(math.pi * x) - 1) / 2

def generate_dot_assembly_animation(
    source_path="assets/hero-portrait.png",
    output_gif="assets/hero-portrait-animated.gif",
    target_size=(500, 500),
    num_frames=28,
    frame_duration_ms=110,
    grid_step=9,
    num_colors=160
):
    print(f"Loading source portrait from: {source_path}", flush=True)
    orig_img = Image.open(source_path).convert("RGBA")
    base_img = orig_img.resize(target_size, Image.Resampling.LANCZOS)
    w, h = target_size
    
    r, g, b, alpha = base_img.split()
    base_rgb = Image.merge("RGB", (r, g, b))
    
    # 1. Sample particle grid from the image
    particles = []
    # Seed for deterministic beautiful scatter
    rng = random.Random(42)
    
    # Analyze brightness and alpha
    gray = base_img.convert("L")
    
    for y in range(grid_step // 2, h, grid_step):
        for x in range(grid_step // 2, w, grid_step):
            a_val = alpha.getpixel((x, y))
            if a_val > 40:
                # Sample color
                col = base_rgb.getpixel((x, y))
                lum = gray.getpixel((x, y))
                
                # Target radius based on brightness and alpha
                max_r = (grid_step * 0.58)
                radius = max(1.2, (lum / 255.0) * max_r * (a_val / 255.0))
                
                # Scrambled initial position (burst out from center or random vector)
                dx = x - (w / 2)
                dy = y - (h / 2)
                dist_center = math.hypot(dx, dy)
                angle = math.atan2(dy, dx) + rng.uniform(-0.8, 0.8)
                
                scatter_dist = rng.uniform(70, 220) + (dist_center * rng.uniform(0.3, 0.7))
                x_scramble = x + math.cos(angle) * scatter_dist + rng.uniform(-40, 40)
                y_scramble = y + math.sin(angle) * scatter_dist + rng.uniform(-40, 40)
                
                # Individual particle arrival stagger [0.0 to 0.35]
                stagger = rng.uniform(0.0, 0.35)
                
                # Accent color: mix photo color with vibrant cyan/orange cybernetic highlights
                if rng.random() < 0.15:
                    accent_col = (56, 189, 248) if rng.random() < 0.6 else (255, 160, 60)
                    particle_col = (
                        int(col[0]*0.4 + accent_col[0]*0.6),
                        int(col[1]*0.4 + accent_col[1]*0.6),
                        int(col[2]*0.4 + accent_col[2]*0.6),
                        a_val
                    )
                else:
                    # Enhanced vibrancy
                    particle_col = (
                        min(255, int(col[0] * 1.15)),
                        min(255, int(col[1] * 1.15)),
                        min(255, int(col[2] * 1.15)),
                        a_val
                    )
                
                particles.append({
                    'target_x': x,
                    'target_y': y,
                    'scramble_x': x_scramble,
                    'scramble_y': y_scramble,
                    'radius': radius,
                    'color': particle_col,
                    'alpha': a_val,
                    'stagger': stagger
                })
                
    print(f"Sampled {len(particles)} structured portrait particles.", flush=True)

    frames_rgba = []
    
    # Timing intervals (normalized 0.0 to 1.0 across num_frames):
    # 0.00 -> 0.40: Particles scramble and converge to grid
    # 0.40 -> 0.50: Grid lock & subtle scanline / glow pulse
    # 0.50 -> 0.70: Smooth cross-dissolve to full crystal-clear photo
    # 0.70 -> 0.88: Hold on full portrait with gentle breathing
    # 0.88 -> 1.00: Smooth dissolve back to starting scattered dots (seamless loop)
    
    for i in range(num_frames):
        t = i / num_frames
        
        # Create blank RGBA frame
        frame_canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(frame_canvas)
        
        # Compute phase blend factors
        if t <= 0.42:
            # Phase 1: Convergence
            # Progress of convergence from 0 to 1
            raw_p = t / 0.42
            
            for p in particles:
                # Apply per-particle stagger
                local_p = min(1.0, max(0.0, (raw_p - p['stagger']) / (1.0 - p['stagger'] + 0.001)))
                ease_p = ease_out_quint(local_p)
                
                cur_x = p['scramble_x'] + (p['target_x'] - p['scramble_x']) * ease_p
                cur_y = p['scramble_y'] + (p['target_y'] - p['scramble_y']) * ease_p
                
                # Alpha fades in as it approaches
                p_alpha = int(p['alpha'] * min(1.0, 0.2 + (ease_p * 0.8)))
                
                # Size grows to target
                r_cur = max(0.8, p['radius'] * (0.4 + 0.6 * ease_p))
                
                col = (p['color'][0], p['color'][1], p['color'][2], p_alpha)
                draw.ellipse([cur_x - r_cur, cur_y - r_cur, cur_x + r_cur, cur_y + r_cur], fill=col)
                
            final_frame = frame_canvas
            
        elif t <= 0.52:
            # Phase 2: Grid Lock with subtle horizontal cyan scan/glow wave
            p_scan = (t - 0.42) / 0.10
            scan_y = h * p_scan
            
            for p in particles:
                # Subtle glow if near scanline
                dist_scan = abs(p['target_y'] - scan_y)
                glow_boost = max(0, 1.0 - (dist_scan / 50.0)) * 0.4
                
                r_cur = p['radius'] * (1.0 + glow_boost * 0.5)
                r_c = min(255, int(p['color'][0] + glow_boost * 60))
                g_c = min(255, int(p['color'][1] + glow_boost * 80))
                b_c = min(255, int(p['color'][2] + glow_boost * 100))
                
                draw.ellipse([
                    p['target_x'] - r_cur, p['target_y'] - r_cur,
                    p['target_x'] + r_cur, p['target_y'] + r_cur
                ], fill=(r_c, g_c, b_c, p['alpha']))
                
            final_frame = frame_canvas
            
        elif t <= 0.72:
            # Phase 3: Cross-dissolve from Dot Matrix to Full Photo
            blend_val = ease_in_out_sine((t - 0.52) / 0.20)
            
            # Draw fully assembled dots
            for p in particles:
                draw.ellipse([
                    p['target_x'] - p['radius'], p['target_y'] - p['radius'],
                    p['target_x'] + p['radius'], p['target_y'] + p['radius']
                ], fill=p['color'])
                
            # Blend frame_canvas (dots) with base_img (photo)
            final_frame = Image.blend(frame_canvas, base_img, blend_val)
            
        elif t <= 0.88:
            # Phase 4: Hold on full portrait with subtle exposure/rim breath
            hold_p = (t - 0.72) / 0.16
            breath = math.sin(math.pi * hold_p) * 0.05
            
            enhancer = ImageEnhance.Brightness(base_img.convert("RGB"))
            b_rgb = enhancer.enhance(1.0 + breath)
            
            # Reattach alpha
            final_frame = Image.merge("RGBA", (*b_rgb.split(), alpha))
            
        else:
            # Phase 5: Smooth dissolve back to starting scattered dots (for loop)
            dissolve_p = ease_in_out_sine((t - 0.88) / 0.12)
            
            # Interpolate particles back to scrambled
            for p in particles:
                local_p = dissolve_p
                cur_x = p['target_x'] + (p['scramble_x'] - p['target_x']) * local_p
                cur_y = p['target_y'] + (p['scramble_y'] - p['target_y']) * local_p
                
                p_alpha = int(p['alpha'] * max(0.0, 1.0 - local_p * 0.6))
                r_cur = max(0.8, p['radius'] * (1.0 - 0.3 * local_p))
                
                draw.ellipse([cur_x - r_cur, cur_y - r_cur, cur_x + r_cur, cur_y + r_cur], fill=(*p['color'][:3], p_alpha))
                
            final_frame = Image.blend(base_img, frame_canvas, dissolve_p)

        frames_rgba.append(final_frame)

    print(f"Generated {len(frames_rgba)} animation frames. Computing global palette...", flush=True)

    # Global palette quantization for clean GIF compression (< 2 MB)
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
    
    size_mb = os.path.getsize(output_gif) / (1024.0 * 1024.0)
    print(f"Demo GIF Created: {output_gif}", flush=True)
    print(f"  Dimensions: {w}x{h} px | Frames: {num_frames} | Total Duration: {(num_frames*frame_duration_ms)/1000.0:.2f}s | Size: {size_mb:.2f} MB", flush=True)
    return output_gif

if __name__ == "__main__":
    generate_dot_assembly_animation()
