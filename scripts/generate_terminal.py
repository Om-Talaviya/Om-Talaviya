#!/usr/bin/env python3
"""
generate_terminal.py - Generates an executive-grade interactive-style Terminal Window SVG
for the `~/ whoami` section.
"""

import os

def render_terminal_svg(output_path="assets/terminal-dark.svg", theme="dark"):
    width = 900
    height = 230
    
    if theme == "dark":
        bg_color = "#0d1117"
        term_header = "#161b22"
        card_border = "#30363d"
        text_primary = "#f0f6fc"
        text_muted = "#8b949e"
        accent = "#38bdf8"
        green = "#3fb950"
        purple = "#bc8cff"
        yellow = "#d29922"
    else:
        bg_color = "#ffffff"
        term_header = "#f6f8fa"
        card_border = "#d0d7de"
        text_primary = "#1f2328"
        text_muted = "#656d76"
        accent = "#0284c7"
        green = "#1a7f37"
        purple = "#8250df"
        yellow = "#9a6700"

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  <!-- Window Container -->
  <rect width="{width}" height="{height}" rx="10" fill="{bg_color}" stroke="{card_border}" stroke-width="1"/>
  
  <!-- Terminal Title Bar -->
  <path d="M 0 10 Q 0 0 10 0 L {width - 10} 0 Q {width} 0 {width} 10 L {width} 36 L 0 36 Z" fill="{term_header}"/>
  <line x1="0" y1="36" x2="{width}" y2="36" stroke="{card_border}" stroke-width="1"/>

  <!-- macOS Window Controls -->
  <circle cx="20" cy="18" r="5.5" fill="#ff5f56"/>
  <circle cx="38" cy="18" r="5.5" fill="#ffbd2e"/>
  <circle cx="56" cy="18" r="5.5" fill="#27c93f"/>

  <!-- Title -->
  <text x="{width / 2}" y="22" font-family="'JetBrains Mono', monospace" font-size="12" font-weight="600" fill="{text_muted}" text-anchor="middle">om@agentic-core: ~</text>

  <!-- Terminal Content -->
  <g transform="translate(24, 66)" font-family="'JetBrains Mono', 'Fira Code', monospace" font-size="13">
    <!-- Command Line -->
    <text x="0" y="0">
      <tspan font-weight="700" fill="{accent}">om@agentic-core:~$ </tspan>
      <tspan font-weight="500" fill="{text_primary}">whoami --verbose --systems</tspan>
    </text>

    <!-- Line 1: Identity -->
    <text x="0" y="28">
      <tspan font-weight="700" fill="{green}">NAME    :: </tspan>
      <tspan font-weight="600" fill="{text_primary}">Om Talaviya </tspan>
      <tspan fill="{text_muted}">[AI &amp; Systems Engineer &#8226; Agentic Platforms]</tspan>
    </text>

    <!-- Line 2: Focus -->
    <text x="0" y="52">
      <tspan font-weight="700" fill="{purple}">FOCUS   :: </tspan>
      <tspan fill="{text_primary}">Agentic AI Orchestration &#8226; Multimodal RAG &#8226; Model Gateways</tspan>
    </text>

    <!-- Line 3: Active Systems -->
    <text x="0" y="76">
      <tspan font-weight="700" fill="{yellow}">ACTIVE  :: </tspan>
      <tspan font-weight="600" fill="{accent}">Universal-Coding-Agent </tspan>
      <tspan fill="{text_muted}">[Supervisor] &amp; </tspan>
      <tspan font-weight="600" fill="{accent}">Research-Platform </tspan>
      <tspan fill="{text_muted}">[Multimodal RAG]</tspan>
    </text>

    <!-- Line 4: Core Stack -->
    <text x="0" y="100">
      <tspan font-weight="700" fill="{green}">STACK   :: </tspan>
      <tspan fill="{text_primary}">Python &#8226; TypeScript &#8226; FastAPI &#8226; Next.js &#8226; Vector DBs &#8226; Docker</tspan>
    </text>

    <!-- Line 5: Approach -->
    <text x="0" y="124">
      <tspan font-weight="700" fill="{accent}">STATUS  :: </tspan>
      <tspan fill="{text_muted}">Architecting deterministic, autonomous AI software systems</tspan>
    </text>
  </g>
</svg>"""

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Generated Terminal SVG: {output_path}")

if __name__ == "__main__":
    render_terminal_svg("assets/terminal-dark.svg", "dark")
    render_terminal_svg("assets/terminal-light.svg", "light")
