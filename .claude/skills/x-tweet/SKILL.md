---
name: x-tweet
description: Generate tweets that match the voice profile and resonate with your target audience. Tweets should feel like authentic observations from an experienced insider, not marketing content.
---

# X Tweet Generator

## Overview

Generate 3 tweets per day that sound like a clear-eyed insider sharing observations, not doing content marketing. Voice, audience, and topics are defined by your context profiles.

## Before Writing

### Step 1: Read Context
1. **Read context profiles** in `/context/`:
   - `voice.json` — How to sound
   - `audience.json` — Who you're writing for
   - Any business profile JSONs — Business context

2. **Check engagement data** in `/knowledge/engagement/` for what's working

3. **Check tweet history** — Read `/knowledge/content/tweet_history.json` for previously written/posted tweets. Do NOT repeat the same topic or angle unless the user explicitly asks. If a topic was already covered, find a different angle or skip it entirely.

### Step 2: Scrape Engagement (MANDATORY — run BEFORE research)
4. **Scrape your profile** — Run `scrape_profile.py` to get latest engagement data on recent tweets. Update `engagement_log.json`. Review what's working (likes, views, replies) and what's not. Use this to inform today's tweet strategy.

### Step 3: Research (MANDATORY — use researcher-agent for all 3 in parallel)
5. **Current tech news** — Search for today's top tech headlines (AI, startups, VC, big tech). Get specific names, numbers, details.
6. **Industry Twitter trends** — Search for what's trending among your target audience, industry news, exits, funding, layoffs, controversies.
7. **Topics you care about** — Search for topics relevant to your voice profile and business profile (defined in context profiles).

### Step 4: Write
8. **Mix news-reactive and evergreen tweets.** At least 1 tweet should react to a specific current event/news item. The others can be original pattern observations, but should be informed by what's happening now — not generic.

## Tweet Types (Rotate Daily)

### 1. Pattern Observation (Primary — 40% of tweets)
Spot something in your industry and name the pattern.
- Start with a specific detail or observation
- Build to a broader insight
- Let the pattern speak for itself

### 2. Contrarian / Anti-Hype (25% of tweets)
Challenge conventional wisdom, call out spin, cut through noise.
- Mock discourse fatigue
- Question what everyone accepts
- Skeptical but not cynical

### 3. Founder/Insider Insight (20% of tweets)
Share practical wisdom from experience.
- Real operational insight, not motivational fluff
- Specific enough to be useful
- From experience, not theory

### 4. Cultural Commentary (15% of tweets)
Industry culture, work life, ecosystem observations.
- Natural language mixing if bilingual
- Pop culture timestamps
- Self-deprecating mundane contrasts

## Voice Rules

### ALWAYS
- Sound like someone who's been in the room
- Be a pattern spotter, not a preacher
- Be skeptical but not bitter
- Use simple language for sophisticated observations
- Short paragraphs, breathing room
- Trust the reader to connect the dots
- Follow voice.json for specific voice patterns

### NEVER
- Management consultant speak
- Breathless hype ("game-changing", "revolutionary")
- Motivational speaker energy
- Corporate press release tone
- Humble-bragging
- Excessive emojis
- Thread announcements
- Generic advice

### Signature Phrases
Use sparingly — pull from voice.json `signature_concepts` and `colloquialisms`.

### Twitter-Specific Patterns
- **Brevity**: Cut connective tissue, not substance
- **Single-line punch**: One powerful observation, full stop
- **Setup → Evidence**: First tweet poses observation, thread continues with proof

## Language

Defined by your voice.json. Supports:
- Primary language tweets
- Secondary language tweets for broader reach (1 in 3)
- Natural code-switching between languages

## Length

- **Ideal**: 1-3 sentences (under 280 chars)
- **Max**: 4-5 sentences for thread starters
- Short and punchy beats long and complete

## Daily Generation

Generate 3 tweets with variety across languages and tweet types.

Each tweet should be independent (not a thread) unless specifically requested.

### Step 5: Humanize (MANDATORY — run AFTER writing)
9. **Run humanizer** — Apply the `/humanizer` skill to all tweets before presenting. Remove AI-isms, inject personality, ensure they sound like a real person wrote them.

## Quality Checklist

Before delivering:
- [ ] Would this stop someone from scrolling?
- [ ] Does it sound like a person, not a brand?
- [ ] Is there a real insight, not just a take?
- [ ] Would your target audience share this?
- [ ] Is it under 280 characters?
- [ ] Does it match the voice profile?
- [ ] Has it been run through the humanizer?

## Tweet History

After presenting tweets to the user, **always update** `/knowledge/content/tweet_history.json` with each tweet's date, topic, angle, status, and text preview. This prevents repeating the same topics/angles across sessions.

## Engagement Learning

Check `/knowledge/engagement/engagement_log.json` for data on what works.
Patterns to optimize for:
- Which tweet types get most engagement
- Which topics resonate
- Language performance differences
- Time-of-day patterns
- What language/phrases trigger shares
