# NaBot

AI co-writing system that learns your voice and creates content that sounds like you. Built on [Claude Code](https://claude.ai/claude-code).

NaBot generates tweets, LinkedIn posts, newsletters, and more — all matching your authentic voice, not generic AI output. It learns from your existing content (tweets, podcast episodes, writing samples) to build a voice DNA profile, then uses that profile across all content skills.

## How It Works

```
Your Content (tweets, podcasts, writing)
         ↓
   Voice DNA Analysis
         ↓
   Context Profiles (voice, audience, business)
         ↓
   Skills (tweet, linkedin, newsletter...)
         ↓
   Content That Sounds Like You
```

1. **Analyze your voice** — Feed it your tweets, podcast episodes, or writing samples. It extracts your patterns, phrases, tone, and style into a voice DNA profile.
2. **Define your context** — Fill in templates for your audience (ICP), business profile, and voice DNA. These are the source of truth for all content.
3. **Generate content** — Use skills to create tweets, LinkedIn posts, newsletters. Each skill reads your context profiles and produces content in your voice.
4. **Learn from engagement** — Scrape engagement data from your posts. The system learns what resonates and adjusts.

## Quick Start

### 1. Clone and set up

```bash
git clone https://github.com/navotvolkgroundup/nabot.git
cd nabot
pip install feedparser openai-whisper camoufox
```

### 2. Create your context profiles

Copy the templates and fill them in with your own information:

```bash
cp context/core/voice-dna-template.json context/core/voice-dna.json
cp context/core/icp-template.json context/core/icp.json
cp context/core/business-profile-template.json context/core/business-profile.json
```

Edit each file — the `_instructions` fields tell you what to put in each section.

### 3. Set up X.com authentication (for posting/scraping)

```bash
# Install Cookie-Editor browser extension
# Go to x.com, log in to your account
# Export cookies → save as browser_cookies.json
python3 import_cookies.py
```

### 4. Set environment variables

```bash
export X_HANDLE=your_twitter_handle        # For scraping/posting
export X_PERSONAL_HANDLE=your_main_handle  # For voice analysis from personal account
export PODCAST_RSS_URL=https://your-rss-feed-url  # For podcast pipeline
```

### 5. Generate content

Open Claude Code in this directory and ask:

```
"write today's tweets"     → uses x-tweet skill
"write a linkedin post"    → uses linkedin-post skill
"write a newsletter"       → uses newsletter agent
```

## Project Structure

```
nabot/
├── CLAUDE.md                    # System instructions for Claude
├── context/core/                # Your context profiles
│   ├── voice-dna.json          # How you sound (create from template)
│   ├── icp.json                # Who you write for (create from template)
│   ├── business-profile.json   # What you offer (create from template)
│   └── *-template.json         # Templates to get started
├── .claude/
│   ├── skills/                 # Content generation skills
│   │   ├── x-tweet/           # Tweet generation with research pipeline
│   │   ├── linkedin-post/     # LinkedIn post generation
│   │   └── thought-leadership/ # Newsletter writing
│   └── agents/                 # Specialized agents
│       ├── researcher-agent.md # Research and analysis
│       ├── voice-analyzer.md   # Voice DNA analysis from content
│       ├── newsletter-agent.md # Newsletter coordination
│       └── book-agent.md       # Book outline generation
├── knowledge/                   # Your content and data (gitignored)
│   ├── engagement/             # Engagement logs and tweet data
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

## Skills

Skills are reusable instructions for specific content types. Claude reads your context profiles + the skill instructions and generates content that matches your voice.

### x-tweet
Generates 3 tweets/day with a mandatory research pipeline:
1. Scrape engagement on past tweets
2. Research current news (3 parallel agents)
3. Write a mix of news-reactive and original tweets

### linkedin-post
Generates LinkedIn posts: pattern recognition, contrarian takes, tactical playbooks, ecosystem commentary.

### thought-leadership
Creates newsletters (800-1,500 words) with subject lines, skimmable headers, and actionable content.

## Voice DNA Pipeline

Enrich your voice profile from multiple sources:

### From tweets
```bash
# Scrape your personal account
python3 scrape_personal.py your_handle
# Then ask Claude to analyze and update voice-dna.json
```

### From podcast episodes
```bash
# Set your RSS feed
export PODCAST_RSS_URL=https://your-rss-feed

# Run the pipeline (downloads, transcribes with Whisper, deletes audio)
python3 podcast/pipeline.py

# Analyze transcripts for voice patterns
python3 podcast/analyze_voice.py
```

### From any content
Use the voice-analyzer agent — paste or screenshot your top-performing content and it extracts patterns and updates your voice DNA.

## Tweet Bot

```bash
python3 bot.py generate   # Prompt to generate tweets via Claude
python3 bot.py add "text" # Add a tweet to the approval queue
python3 bot.py approve    # Interactive review (approve/reject/edit)
python3 bot.py post       # Post approved tweets to X.com
python3 bot.py analyze    # Scrape engagement metrics
python3 bot.py status     # Show queue status
```

## Requirements

- [Claude Code](https://claude.ai/claude-code) (for content generation)
- Python 3.10+
- `pip install feedparser openai-whisper camoufox`
- Browser with Cookie-Editor extension (for X.com auth)

## License

MIT
