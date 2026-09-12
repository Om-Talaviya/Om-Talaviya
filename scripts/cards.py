#!/usr/bin/env python3
"""
cards.py - Self-Hosted GitHub Stat Card, Activity Velocity Card & Project Cards Generator
Generates premium dark and light mode SVG cards with perfect 2-column alignment and no truncated pitches.
"""

import argparse
import html
import json
import os
import sys
import urllib.request
import urllib.error

LANGUAGE_COLORS = {
    "Python": "#3572A5",
    "TypeScript": "#3178c6",
    "JavaScript": "#f1e05a",
    "HTML": "#e34c26",
    "CSS": "#563d7c",
    "Go": "#00ADD8",
    "Rust": "#dea584",
    "C++": "#f34b7d",
    "C": "#555555",
    "Java": "#b07219",
    "Shell": "#89e051",
    "Docker": "#384d54",
    "Vue": "#41b883",
    "React": "#61dafb",
    "Jupyter Notebook": "#DA5B0B"
}


def fetch_json(url, token=None):
    headers = {
        "User-Agent": "profile-readme-card-generator",
        "Accept": "application/vnd.github.v3+json"
    }
    if token:
        headers["Authorization"] = f"token {token}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as e:
        print(f"Notice: Could not fetch {url} ({e})", file=sys.stderr)
        return None


def fetch_user_stats(username, token=None):
    user_data = fetch_json(f"https://api.github.com/users/{username}", token)
    repos_data = fetch_json(f"https://api.github.com/users/{username}/repos?per_page=100&type=owner", token)

    public_repos = user_data.get("public_repos", 0) if user_data else 6
    followers = user_data.get("followers", 0) if user_data else 0
    created_at = user_data.get("created_at", "2025")[:4] if user_data else "2025"

    total_stars = 0
    total_forks = 0
    if repos_data and isinstance(repos_data, list):
        for r in repos_data:
            if not r.get("fork"):
                total_stars += r.get("stargazers_count", 0)
                total_forks += r.get("forks_count", 0)

    # If user has GraphQL token for contributions
    contributions = None
    if token:
        gql_query = """
        query($login: String!) {
          user(login: $login) {
            contributionsCollection {
              contributionCalendar {
                totalContributions
              }
            }
          }
        }
        """
        try:
            req = urllib.request.Request(
                "https://api.github.com/graphql",
                data=json.dumps({"query": gql_query, "variables": {"login": username}}).encode("utf-8"),
                headers={
                    "Authorization": f"bearer {token}",
                    "User-Agent": "profile-readme-card-generator"
                }
            )
            with urllib.request.urlopen(req) as resp:
                gql_res = json.loads(resp.read().decode("utf-8"))
                contributions = (
                    gql_res.get("data", {})
                    .get("user", {})
                    .get("contributionsCollection", {})
                    .get("contributionCalendar", {})
                    .get("totalContributions")
                )
        except Exception:
            pass

    return {
        "username": username,
        "public_repos": public_repos,
        "stars": total_stars,
        "forks": total_forks,
        "followers": followers,
        "contributions": contributions,
        "since": created_at
    }


def render_stat_card(stats, theme="dark", accent="#38bdf8", width=440, height=210):
    if theme == "dark":
        bg_color = "#0d1117"
        card_border = "#30363d"
        text_primary = "#f0f6fc"
        text_secondary = "#8b949e"
        tile_bg = "#161b22"
        tile_border = "#21262d"
        accent_color = accent
    else:
        bg_color = "#ffffff"
        card_border = "#d0d7de"
        text_primary = "#1f2328"
        text_secondary = "#656d76"
        tile_bg = "#f6f8fa"
        tile_border = "#eaeef2"
        accent_color = "#0284c7" if accent == "#38bdf8" else accent

    tiles = [
        {"label": "Public Repos", "val": str(stats["public_repos"])},
        {"label": "Total Stars", "val": str(stats["stars"])},
        {"label": "Forks", "val": str(stats["forks"])}
    ]
    if stats.get("contributions") is not None:
        tiles.append({"label": "Contributions", "val": str(stats["contributions"])})
    else:
        tiles.append({"label": "Active Since", "val": str(stats["since"])})

    svg_tiles = []
    tile_w = 186
    tile_h = 60
    positions = [
        (22, 64),
        (232, 64),
        (22, 134),
        (232, 134)
    ]

    for i, t in enumerate(tiles[:4]):
        tx, ty = positions[i]
        svg_tiles.append(f"""
        <g transform="translate({tx}, {ty})">
            <rect width="{tile_w}" height="{tile_h}" rx="8" fill="{tile_bg}" stroke="{tile_border}" stroke-width="1"/>
            <text x="14" y="24" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif" font-size="11" font-weight="600" fill="{text_secondary}">{t['label'].upper()}</text>
            <text x="14" y="48" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif" font-size="19" font-weight="700" fill="{accent_color}">{t['val']}</text>
        </g>
        """)

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  <rect width="{width}" height="{height}" rx="12" fill="{bg_color}" stroke="{card_border}" stroke-width="1"/>
  
  <!-- Header -->
  <g transform="translate(22, 34)">
    <circle cx="6" cy="-4" r="5" fill="{accent_color}"/>
    <text x="20" y="0" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif" font-size="14" font-weight="700" fill="{text_primary}">ENGINEERING METRICS</text>
  </g>
  <line x1="22" y1="48" x2="{width - 22}" y2="48" stroke="{tile_border}" stroke-width="1"/>

  {''.join(svg_tiles)}
</svg>"""
    return svg


def render_activity_velocity_card(stats, theme="dark", accent="#38bdf8", width=440, height=210):
    if theme == "dark":
        bg_color = "#0d1117"
        card_border = "#30363d"
        text_primary = "#f0f6fc"
        text_secondary = "#8b949e"
        tile_bg = "#161b22"
        tile_border = "#21262d"
        accent_color = accent
        badge_bg = "rgba(56, 189, 248, 0.12)"
    else:
        bg_color = "#ffffff"
        card_border = "#d0d7de"
        text_primary = "#1f2328"
        text_secondary = "#656d76"
        tile_bg = "#f6f8fa"
        tile_border = "#eaeef2"
        accent_color = "#0284c7" if accent == "#38bdf8" else accent
        badge_bg = "rgba(2, 132, 199, 0.10)"

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  <rect width="{width}" height="{height}" rx="12" fill="{bg_color}" stroke="{card_border}" stroke-width="1"/>
  
  <!-- Header -->
  <g transform="translate(22, 34)">
    <circle cx="6" cy="-4" r="5" fill="{accent_color}"/>
    <text x="20" y="0" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif" font-size="14" font-weight="700" fill="{text_primary}">DEVELOPMENT PROFILE</text>
  </g>
  <line x1="22" y1="48" x2="{width - 22}" y2="48" stroke="{tile_border}" stroke-width="1"/>

  <!-- Row 1: Focus Area -->
  <g transform="translate(22, 64)">
    <rect width="396" height="60" rx="8" fill="{tile_bg}" stroke="{tile_border}" stroke-width="1"/>
    <text x="14" y="24" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif" font-size="11" font-weight="600" fill="{text_secondary}">SPECIALIZATION</text>
    <text x="14" y="47" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif" font-size="14" font-weight="700" fill="{accent_color}">Agentic AI &#8226; Multimodal RAG &#8226; Distributed Systems</text>
  </g>

  <!-- Row 2: Status & Mode -->
  <g transform="translate(22, 134)">
    <rect width="186" height="60" rx="8" fill="{tile_bg}" stroke="{tile_border}" stroke-width="1"/>
    <text x="14" y="24" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif" font-size="11" font-weight="600" fill="{text_secondary}">ACTIVITY STATUS</text>
    <text x="14" y="47" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif" font-size="14" font-weight="700" fill="{text_primary}">Daily Engineering</text>
  </g>

  <g transform="translate(232, 134)">
    <rect width="186" height="60" rx="8" fill="{tile_bg}" stroke="{tile_border}" stroke-width="1"/>
    <text x="14" y="24" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif" font-size="11" font-weight="600" fill="{text_secondary}">PRIMARY RUNTIME</text>
    <text x="14" y="47" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif" font-size="14" font-weight="700" fill="{text_primary}">Python &#8226; TypeScript</text>
  </g>
</svg>"""
    return svg


def wrap_text_lines(text, max_chars_per_line=48, max_lines=3):
    words = text.split(" ")
    lines = []
    current_line = []
    current_len = 0

    for word in words:
        if current_len + len(word) + (1 if current_line else 0) <= max_chars_per_line:
            current_line.append(word)
            current_len += len(word) + (1 if len(current_line) > 1 else 0)
        else:
            if len(lines) < max_lines - 1:
                lines.append(" ".join(current_line))
                current_line = [word]
                current_len = len(word)
            else:
                current_line.append(word)
                break

    if current_line and len(lines) < max_lines:
        lines.append(" ".join(current_line))

    # Clean up trailing truncation if needed
    for i in range(len(lines)):
        lines[i] = html.escape(lines[i])

    return lines[:max_lines]


def render_project_card(repo_data, override_desc=None, theme="dark", accent="#38bdf8", width=440, height=180):
    if theme == "dark":
        bg_color = "#0d1117"
        card_border = "#30363d"
        text_primary = "#58a6ff"
        text_desc = "#8b949e"
        text_meta = "#7d8590"
        tag_bg = "#161b22"
        tag_border = "#30363d"
        accent_color = accent
    else:
        bg_color = "#ffffff"
        card_border = "#d0d7de"
        text_primary = "#0969da"
        text_desc = "#57606a"
        text_meta = "#656d76"
        tag_bg = "#f6f8fa"
        tag_border = "#d0d7de"
        accent_color = "#0284c7" if accent == "#38bdf8" else accent

    name = repo_data.get("name", "Project")
    raw_desc = override_desc or repo_data.get("description") or "Autonomous software system."
    lines = wrap_text_lines(raw_desc, max_chars_per_line=50, max_lines=3)
    
    lang = repo_data.get("language") or "Python"
    lang_color = LANGUAGE_COLORS.get(lang, "#8b949e")
    stars = repo_data.get("stargazers_count", 0)
    forks = repo_data.get("forks_count", 0)

    desc_svg = []
    y_start = 68
    for i, line in enumerate(lines):
        desc_svg.append(
            f'<text x="24" y="{y_start + i * 20}" font-family="-apple-system, BlinkMacSystemFont, \'Segoe UI\', Roboto, Helvetica, Arial, sans-serif" font-size="12.5" fill="{text_desc}">{line}</text>'
        )

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  <!-- Card Base -->
  <rect width="{width}" height="{height}" rx="12" fill="{bg_color}" stroke="{card_border}" stroke-width="1"/>
  
  <!-- Left Accent Bar -->
  <rect x="0" y="16" width="4" height="{height - 32}" rx="2" fill="{accent_color}"/>

  <!-- Repository Title -->
  <g transform="translate(24, 34)">
    <!-- Book/Repo Icon -->
    <path d="M0 1.75A.75.75 0 0 1 .75 1h4.253c1.227 0 2.317.59 3 1.501A3.743 3.743 0 0 1 11 1h4.25a.75.75 0 0 1 .75.75v10.5a.75.75 0 0 1-.75.75h-4.25a2.25 2.25 0 0 0-1.75.836A.75.75 0 0 1 8.5 14a.75.75 0 0 1-.5-.164A2.25 2.25 0 0 0 6.25 13H2a.75.75 0 0 1-.75-.75V1.75z" fill="{text_primary}" transform="scale(1.1)"/>
    <text x="26" y="11" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif" font-size="15" font-weight="700" fill="{text_primary}">{name}</text>
  </g>

  <!-- Description Lines -->
  {''.join(desc_svg)}

  <!-- Card Meta Footer -->
  <g transform="translate(24, 150)">
    <!-- Language -->
    <circle cx="5" cy="-4" r="5" fill="{lang_color}"/>
    <text x="16" y="0" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif" font-size="11.5" font-weight="600" fill="{text_meta}">{lang}</text>

    <!-- Star Count -->
    <g transform="translate(130, 0)">
      <path d="M8 .25a.75.75 0 0 1 .673.418l1.882 3.815 4.21.612a.75.75 0 0 1 .416 1.279l-3.046 2.97.719 4.192a.75.75 0 0 1-1.088.791L8 12.347l-3.766 1.98a.75.75 0 0 1-1.088-.79l.72-4.194L.818 6.374a.75.75 0 0 1 .416-1.28l4.21-.611L7.327.668A.75.75 0 0 1 8 .25z" fill="{text_meta}" transform="scale(0.85) translate(0, -10)"/>
      <text x="18" y="0" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif" font-size="11.5" fill="{text_meta}">{stars}</text>
    </g>

    <!-- Fork Count -->
    <g transform="translate(210, 0)">
      <path d="M5 3.25a.75.75 0 1 1-1.5 0 .75.75 0 0 1 1.5 0zm0 2.122a2.25 2.25 0 1 0-1.5 0v.878A2.25 2.25 0 0 0 5.75 8.5h1.5v2.128a2.251 2.251 0 1 0 1.5 0V8.5A2.25 2.25 0 0 0 6.5 6.25h-.75V5.372z" fill="{text_meta}" transform="scale(0.9) translate(0, -10)"/>
      <text x="16" y="0" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif" font-size="11.5" fill="{text_meta}">{forks}</text>
    </g>
  </g>
</svg>"""
    return svg


def main():
    parser = argparse.ArgumentParser(description="Generate self-hosted stat card, activity card and project cards.")
    parser.add_argument("--user", required=True, help="GitHub username")
    parser.add_argument("--token", help="GitHub API token (optional)")
    parser.add_argument("--out", default="assets", help="Output directory")
    parser.add_argument("--projects", default="assets/projects.json", help="Projects configuration JSON file")
    parser.add_argument("--accent", default="#38bdf8", help="Accent color (default: #38bdf8)")

    args = parser.parse_args()

    token = args.token or os.getenv("GITHUB_TOKEN") or os.getenv("METRICS_TOKEN")
    os.makedirs(args.out, exist_ok=True)

    # 1. Fetch & Generate Stat Card & Activity Velocity Card
    print(f"Fetching statistics for @{args.user}...")
    stats = fetch_user_stats(args.user, token=token)
    
    stat_dark = render_stat_card(stats, theme="dark", accent=args.accent)
    stat_light = render_stat_card(stats, theme="light", accent=args.accent)

    with open(os.path.join(args.out, "card-stats-dark.svg"), "w", encoding="utf-8") as f:
        f.write(stat_dark)
    with open(os.path.join(args.out, "card-stats-light.svg"), "w", encoding="utf-8") as f:
        f.write(stat_light)

    activity_dark = render_activity_velocity_card(stats, theme="dark", accent=args.accent)
    activity_light = render_activity_velocity_card(stats, theme="light", accent=args.accent)

    with open(os.path.join(args.out, "card-activity-dark.svg"), "w", encoding="utf-8") as f:
        f.write(activity_dark)
    with open(os.path.join(args.out, "card-activity-light.svg"), "w", encoding="utf-8") as f:
        f.write(activity_light)

    print("Generated stat cards: card-stats-*.svg and card-activity-*.svg")

    # 2. Project Cards
    projects_list = []
    if os.path.exists(args.projects):
        with open(args.projects, "r", encoding="utf-8") as f:
            p_data = json.load(f)
            projects_list = p_data.get("projects", [])

    # Fetch all user repos to match info
    repos_map = {}
    repos_res = fetch_json(f"https://api.github.com/users/{args.user}/repos?per_page=100&type=owner", token)
    if repos_res and isinstance(repos_res, list):
        for r in repos_res:
            repos_map[r.get("name", "").lower()] = r

    for p in projects_list:
        repo_name = p.get("repo")
        override_desc = p.get("description")
        explicit_lang = p.get("language")
        repo_info = repos_map.get(repo_name.lower()) or {
            "name": repo_name,
            "description": override_desc,
            "language": explicit_lang or ("Python" if any(k in repo_name.lower() for k in ("research", "knowledge", "curl", "skill")) else "TypeScript"),
            "stargazers_count": 0,
            "forks_count": 0
        }
        if explicit_lang:
            repo_info["language"] = explicit_lang

        # Safe slug for filename
        slug = repo_name.lower().replace("/", "-")
        card_dark = render_project_card(repo_info, override_desc=override_desc, theme="dark", accent=args.accent)
        card_light = render_project_card(repo_info, override_desc=override_desc, theme="light", accent=args.accent)

        dark_file = os.path.join(args.out, f"card-{slug}-dark.svg")
        light_file = os.path.join(args.out, f"card-{slug}-light.svg")

        with open(dark_file, "w", encoding="utf-8") as f:
            f.write(card_dark)
        with open(light_file, "w", encoding="utf-8") as f:
            f.write(card_light)

        print(f"Generated project card: card-{slug}-dark.svg and card-{slug}-light.svg")


if __name__ == "__main__":
    main()
