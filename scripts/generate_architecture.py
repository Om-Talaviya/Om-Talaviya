#!/usr/bin/env python3
"""
generate_architecture.py - Generates an interactive-style AI System Architecture Card
Showcases the signature Agentic Platform & Multimodal RAG Pipeline in Vector SVG.
"""

import os

def render_architecture_svg(output_path="assets/architecture-dark.svg", theme="dark"):
    width = 900
    height = 240
    
    if theme == "dark":
        bg_color = "#0d1117"
        card_border = "#30363d"
        text_primary = "#f0f6fc"
        text_secondary = "#8b949e"
        node_bg = "#161b22"
        node_border = "#38bdf8"
        node_border_sub = "#21262d"
        accent = "#38bdf8"
        accent_dim = "rgba(56, 189, 248, 0.15)"
        line_color = "#38bdf8"
        tag_bg = "rgba(56, 189, 248, 0.10)"
    else:
        bg_color = "#ffffff"
        card_border = "#d0d7de"
        text_primary = "#1f2328"
        text_secondary = "#656d76"
        node_bg = "#f6f8fa"
        node_border = "#0284c7"
        node_border_sub = "#eaeef2"
        accent = "#0284c7"
        accent_dim = "rgba(2, 132, 199, 0.12)"
        line_color = "#0284c7"
        tag_bg = "rgba(2, 132, 199, 0.08)"

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  <defs>
    <linearGradient id="glowGrad-{theme}" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{accent}" stop-opacity="0.8"/>
      <stop offset="100%" stop-color="{accent}" stop-opacity="0.2"/>
    </linearGradient>
    <filter id="shadow-{theme}" x="-10%" y="-10%" width="120%" height="120%">
      <feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="{accent}" flood-opacity="0.15"/>
    </filter>
  </defs>

  <!-- Container -->
  <rect width="{width}" height="{height}" rx="12" fill="{bg_color}" stroke="{card_border}" stroke-width="1"/>

  <!-- Header -->
  <g transform="translate(24, 30)">
    <circle cx="6" cy="-4" r="5" fill="{accent}"/>
    <text x="20" y="0" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="13" font-weight="700" fill="{text_primary}" letter-spacing="0.5">AGENTIC ARCHITECTURE &bull; PIPELINE TOPOLOGY</text>
    <text x="{width - 48}" y="0" font-family="'JetBrains Mono', monospace" font-size="11" font-weight="600" fill="{accent}" text-anchor="end">Deterministic v2.4</text>
  </g>
  <line x1="24" y1="42" x2="{width - 24}" y2="42" stroke="{card_border}" stroke-width="1"/>

  <!-- Nodes Layout -->
  
  <!-- Node 1: Input -->
  <g transform="translate(36, 68)">
    <rect width="180" height="136" rx="10" fill="{node_bg}" stroke="{node_border_sub}" stroke-width="1.5"/>
    <rect width="180" height="28" rx="10" fill="{tag_bg}"/>
    <text x="14" y="19" font-family="'JetBrains Mono', monospace" font-size="11" font-weight="700" fill="{accent}">01. INGESTION</text>
    <text x="14" y="54" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="13" font-weight="700" fill="{text_primary}">Multimodal Inputs</text>
    <text x="14" y="74" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="11" fill="{text_secondary}">&bull; Context & AST Code</text>
    <text x="14" y="94" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="11" fill="{text_secondary}">&bull; Vectorized Embeddings</text>
    <text x="14" y="114" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="11" fill="{text_secondary}">&bull; Live Telemetry Feed</text>
  </g>

  <!-- Arrow 1 -> 2 -->
  <g transform="translate(224, 130)">
    <line x1="0" y1="0" x2="24" y2="0" stroke="{line_color}" stroke-width="2" stroke-dasharray="4,3"/>
    <polygon points="24,-4 32,0 24,4" fill="{line_color}"/>
  </g>

  <!-- Node 2: Router -->
  <g transform="translate(264, 68)" filter="url(#shadow-{theme})">
    <rect width="180" height="136" rx="10" fill="{node_bg}" stroke="{node_border}" stroke-width="1.5"/>
    <rect width="180" height="28" rx="10" fill="{accent_dim}"/>
    <text x="14" y="19" font-family="'JetBrains Mono', monospace" font-size="11" font-weight="700" fill="{accent}">02. ORCHESTRATION</text>
    <text x="14" y="54" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="13" font-weight="700" fill="{text_primary}">Model Gateway</text>
    <text x="14" y="74" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="11" fill="{text_secondary}">&bull; Dynamic Routing Logic</text>
    <text x="14" y="94" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="11" fill="{text_secondary}">&bull; Latency/Cost Optimizer</text>
    <text x="14" y="114" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="11" fill="{text_secondary}">&bull; Fallback Consensus</text>
  </g>

  <!-- Arrow 2 -> 3 -->
  <g transform="translate(452, 130)">
    <line x1="0" y1="0" x2="24" y2="0" stroke="{line_color}" stroke-width="2" stroke-dasharray="4,3"/>
    <polygon points="24,-4 32,0 24,4" fill="{line_color}"/>
  </g>

  <!-- Node 3: Hybrid Retrieval -->
  <g transform="translate(488, 68)">
    <rect width="180" height="136" rx="10" fill="{node_bg}" stroke="{node_border_sub}" stroke-width="1.5"/>
    <rect width="180" height="28" rx="10" fill="{tag_bg}"/>
    <text x="14" y="19" font-family="'JetBrains Mono', monospace" font-size="11" font-weight="700" fill="{accent}">03. KNOWLEDGE</text>
    <text x="14" y="54" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="13" font-weight="700" fill="{text_primary}">Hybrid RAG Engine</text>
    <text x="14" y="74" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="11" fill="{text_secondary}">&bull; Dense + Sparse Vectors</text>
    <text x="14" y="94" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="11" fill="{text_secondary}">&bull; Reciprocal Rank Fusion</text>
    <text x="14" y="114" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="11" fill="{text_secondary}">&bull; Graph Memory Cache</text>
  </g>

  <!-- Arrow 3 -> 4 -->
  <g transform="translate(676, 130)">
    <line x1="0" y1="0" x2="24" y2="0" stroke="{line_color}" stroke-width="2" stroke-dasharray="4,3"/>
    <polygon points="24,-4 32,0 24,4" fill="{line_color}"/>
  </g>

  <!-- Node 4: Autonomous Execution -->
  <g transform="translate(712, 68)">
    <rect width="152" height="136" rx="10" fill="{node_bg}" stroke="{node_border_sub}" stroke-width="1.5"/>
    <rect width="152" height="28" rx="10" fill="{tag_bg}"/>
    <text x="14" y="19" font-family="'JetBrains Mono', monospace" font-size="11" font-weight="700" fill="{accent}">04. EXECUTION</text>
    <text x="14" y="54" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="13" font-weight="700" fill="{text_primary}">Agentic Actions</text>
    <text x="14" y="74" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="11" fill="{text_secondary}">&bull; Sandbox Verification</text>
    <text x="14" y="94" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="11" fill="{text_secondary}">&bull; Automated PR & Git</text>
    <text x="14" y="114" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="11" fill="{text_secondary}">&bull; Deterministic Tests</text>
  </g>

</svg>"""

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Generated Architecture SVG: {output_path}")

if __name__ == "__main__":
    render_architecture_svg("assets/architecture-dark.svg", "dark")
    render_architecture_svg("assets/architecture-light.svg", "light")
