#!/usr/bin/env python3
"""
generate_status.py - Generates a sleek, executive-grade Status & Availability Pill SVG
"""

import os

def render_status_svg(output_path="assets/status-dark.svg", theme="dark"):
    width = 720
    height = 36
    
    if theme == "dark":
        bg_color = "#161b22"
        border_color = "#30363d"
        text_primary = "#f0f6fc"
        text_muted = "#8b949e"
        accent = "#38bdf8"
        dot_color = "#38bdf8"
        dot_glow = "rgba(56, 189, 248, 0.25)"
    else:
        bg_color = "#f6f8fa"
        border_color = "#d0d7de"
        text_primary = "#1f2328"
        text_muted = "#656d76"
        accent = "#0284c7"
        dot_color = "#0284c7"
        dot_glow = "rgba(2, 132, 199, 0.20)"

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  <!-- Background Pill -->
  <rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="17" fill="{bg_color}" stroke="{border_color}" stroke-width="1"/>

  <g transform="translate(20, 22)">
    <!-- Status Dot -->
    <circle cx="4" cy="-4" r="5" fill="{dot_glow}"/>
    <circle cx="4" cy="-4" r="3" fill="{dot_color}"/>
    
    <!-- Status Text -->
    <text x="16" y="0" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif" font-size="11" font-weight="700" fill="{accent}" letter-spacing="0.4">STATUS:</text>
    <text x="68" y="0" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif" font-size="11" font-weight="600" fill="{text_primary}">Open for Agentic AI Collaborations</text>
    
    <!-- Divider 1 -->
    <text x="295" y="-1" font-family="monospace" font-size="12" fill="{border_color}">|</text>
    
    <!-- Timezone -->
    <text x="312" y="0" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif" font-size="11" font-weight="500" fill="{text_muted}">IST (UTC+5:30)</text>
    
    <!-- Divider 2 -->
    <text x="410" y="-1" font-family="monospace" font-size="12" fill="{border_color}">|</text>
    
    <!-- Response Time -->
    <text x="428" y="0" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif" font-size="11" font-weight="500" fill="{text_muted}">Response Time:</text>
    <text x="518" y="0" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif" font-size="11" font-weight="700" fill="{accent}">&lt; 24h</text>
  </g>
</svg>"""

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Generated Status Pill: {output_path}")

if __name__ == "__main__":
    render_status_svg("assets/status-dark.svg", "dark")
    render_status_svg("assets/status-light.svg", "light")
