# NaBot

AI content automation system built on [Claude Code](https://claude.ai/claude-code). Generates tweets, LinkedIn posts, and newsletters in your voice — with built-in research, engagement tracking, and a feedback loop that learns what works.

Not a writing template. An automation system with a tweet bot CLI, engagement scraping, podcast transcription pipeline, and AI writing decontamination.

## How it works

```
Scrape engagement → Research news → Generate content → Humanize → Approve → Post
         ↑                                                                    |
         └────────────────── feedback loop ───────────────────────────────────┘
```

1. **Build your voice profile** — Feed it your tweets, podcast episodes, or writing samples. It extracts patterns, phrases, tone, and style.
2. **Set your context** — Fill in the template with your voice, audience, and business info. One file, markdown, done.
3. **Generate content** — Skills handle specific content types (tweets, LinkedIn, newsletters). Each reads your context and produces content in your voice.
4. **Humanize** — Every piece of content runs through a 24-pattern AI writing detector that strips out the robot.
5. **Post and learn** — Scrape engagement data from your posts. The system tracks what resonates and adjusts.

## Quick start

### 1. Clone and install

```bash
git clone https://github.com/navotvolkgroundup/nabot.git
cd nabot
pip install feedparser openai-whisper camoufox
```

### 2. Set up your context

Copy the template and fill it in:

```bash
cp context/TEMPLATE.md context/voice.md
# Or use JSON if you prefer structured data — see TEMPLATE.md for sections
```

### 3. Set up X.com auth (for posting/scraping)

```bash
# Install Cookie-Editor browser extension
# Go to x.com, log in
# Export cookies → save as browser_cookies.json
python3 import_cookies.py
```

### 4. Environment variables

```bash
export X_HANDLE=your_twitter_handle
export X_PERSONAL_HANDLE=your_main_handle
export PODCAST_RSS_URL=https://your-rss-feed-url
```

### 5. Generate content

Open Claude Code in this directory:

```
"write today's tweets"     → x-tweet skill
"write a linkedin post"    → linkedin-post skill
"write a newsletter"       → thought-leadership skill
```

## Project structure

```
nabot/
├── CLAUDE.md                    # System instructions for Claude
├── context/                     # Your context (voice, audience, business)
│   ├── TEMPLATE.md             # Start here — fill this in
│   ├── voice.json              # Your voice profile (gitignored)
│   ├── audience.json           # Your audience (gitignored)
│   └── business-*.json         # Your business context (gitignored)
├── .claude/
│   ├── skills/                 # Content generation skills
│   │   ├── x-tweet/           # Tweet generation with research pipeline
│   │   ├── linkedin-post/     # LinkedIn post generation
│   │   ├── humanizer/         # AI writing pattern removal (24 patterns)
│   │   └── thought-leadership/ # Newsletter writing
│   └── agents/                 # Specialized agents
│       ├── researcher-agent.md # Parallel news research
│       ├── voice-analyzer.md   # Voice analysis from content
│       ├── newsletter-agent.md # Newsletter coordination
│       └── book-agent.md       # Book outline generation
├── knowledge/                   # Your content and data (gitignored)
│   ├── engagement/             # Engagement logs and metrics
│   ├── content/                # Published content
│   ├── drafts/                 # Work in progress
│   └── notes/                  # Ideas and research
├── podcast/                     # Podcast voice analysis pipeline
│   ├── pipeline.py             # Download → transcribe → analyze
│   ├── download_episodes.py    # RSS feed downloader
│   ├── transcribe.py           # Whisper transcription (local)
│   └── analyze_voice.py        # Extract voice patterns from transcripts
├── bot.py                       # Tweet bot CLI (generate/approve/post)
├── scrape_profile.py            # Scrape engagement from your X profile
├── scrape_personal.py           # Scrape personal account for voice analysis
└── import_cookies.py            # Import browser cookies for X.com auth
```

## Tweet bot

The CLI for managing your tweet pipeline:

```bash
python3 bot.py generate   # Generate tweets via Claude
python3 bot.py add "text" # Add a tweet to the approval queue
python3 bot.py approve    # Interactive review (approve/reject/edit)
python3 bot.py post       # Post approved tweets to X.com
python3 bot.py analyze    # Scrape engagement metrics
python3 bot.py status     # Show queue status
```

## Skills

### x-tweet
Generates 3 tweets/day with a mandatory pipeline:
1. Scrape engagement on past tweets
2. Research current news (3 parallel agents)
3. Write a mix of news-reactive and original tweets
4. Humanize before presenting

### linkedin-post
Pattern recognition, contrarian takes, tactical playbooks, ecosystem commentary. Humanized.

### humanizer
Strips 24 AI writing patterns from all content. Based on Wikipedia's "Signs of AI writing" guide. Runs automatically as the final step on everything.

### thought-leadership
Newsletters (800-1,500 words) with subject lines, skimmable headers, actionable content.

## Voice analysis pipeline

Build your voice profile from multiple sources:

### From tweets
```bash
python3 scrape_personal.py your_handle
# Then ask Claude to analyze and update your voice profile
```

### From podcast episodes
```bash
export PODCAST_RSS_URL=https://your-rss-feed
python3 podcast/pipeline.py        # Download + transcribe with Whisper
python3 podcast/analyze_voice.py   # Extract voice patterns
```

### From any content
Use the voice-analyzer agent — paste or screenshot your top-performing content and it extracts patterns.

## Requirements

- [Claude Code](https://claude.ai/claude-code)
- Python 3.10+
- `pip install feedparser openai-whisper camoufox`
- Browser with Cookie-Editor extension (for X.com auth)

## License

MIT
