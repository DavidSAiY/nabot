---
name: linkedin-post
description: Generate LinkedIn posts that match the voice DNA and resonate with your target audience. Posts should feel like real thinking from someone in the arena - not thought leadership content marketing.
---

# LinkedIn Post Generator

## Overview

Generate 3-5 LinkedIn posts per week that read like a sharp operator sharing what they actually see, not building a personal brand. Voice, audience, and business context come from your context profiles.

## Before Writing

1. **Read context profiles** in `/context/core/`:
   - `voice-dna.json` - How to sound
   - `icp.json` - Who you're writing for
   - Any business profile JSONs - Business context

2. **Check engagement data** in `/knowledge/engagement/` for what's working

3. **Check recent posts** to avoid repetition and ensure topic variety

## Post Types (Rotate Weekly)

### 1. Pattern Recognition (Primary - 35% of posts)
Name something you're seeing across your industry.
- Open with the pattern, not the preamble
- Ground it in specific (anonymized) examples
- End with the implication, not a call to action

### 2. Contrarian / Myth-Busting (25% of posts)
Challenge accepted wisdom in your domain.
- Lead with the thing everyone says
- Show why it's wrong, incomplete, or outdated
- Back it up with what you actually see
- Skeptical but constructive

### 3. Practitioner Playbook (20% of posts)
Tactical, operational insight from experience.
- One specific thing, explained clearly
- From pattern-matching and experience, not theory
- Concrete enough that someone can act on it Monday morning

### 4. Ecosystem Commentary (15% of posts)
Industry culture, landscape observations, global context through a local lens.
- Where things sit globally right now
- Cultural dynamics that outsiders miss
- Honest takes on ecosystem strengths and blind spots

### 5. Content / Portfolio Signal (5% of posts)
Light promotion of your content or wins.
- Never the main event - always wrapped in an insight
- Framed as signals, not press releases

## Voice Rules

### ALWAYS
- Write like you're texting a smart friend, not posting for an audience
- Open strong - the first line is the scroll-stopper
- Use white space generously (LinkedIn rewards readability)
- One idea per post, fully developed
- Specificity over generality
- Trust the reader's intelligence
- End with something that lingers, not a question bait
- Follow voice-dna.json for specific voice patterns

### NEVER
- "I'm humbled to announce..."
- "Here are 7 lessons I learned from..."
- Numbered listicles disguised as wisdom
- Engagement bait questions ("Agree?")
- Emoji bullet points
- "Let that sink in."
- Tagging people for visibility
- Reposting with "THIS."
- LinkedIn broetry (one. word. per. line.)
- Humble-bragging wrapped in gratitude
- Corporate jargon: synergy, leverage, ecosystem play, value-add

### Signature Phrases
Use sparingly — pull from voice-dna.json.

### LinkedIn-Specific Patterns
- **Hook line**: First 1-2 lines visible before "see more" - make them count
- **White space**: Short paragraphs (1-3 sentences), line breaks between ideas
- **No wall of text**: If it looks dense in preview, it won't get read
- **Single insight, developed**: Better to go deep on one thing than shallow on three

## Language

Defined by your voice-dna.json. Supports primary and secondary languages with natural code-switching.

## Length

- **Sweet spot**: 150-300 words (800-1,500 characters)
- **Hook**: First 2 lines must work as a standalone teaser (visible before "see more")
- **Min**: 80 words - shorter than that, use Twitter instead
- **Max**: 500 words for deep-dive posts (use sparingly, 1x/week max)

## Formatting

- Line breaks between paragraphs (LinkedIn collapses dense text)
- Bold sparingly for emphasis on key phrases
- No hashtags in the body of the post
- 2-3 relevant hashtags at the very end, separated from the post
- No emojis in the post body (rare exception: a single one if genuinely natural)

## Humanize (MANDATORY — run AFTER writing)

Apply the `/humanizer` skill to all posts before presenting. Remove AI-isms, inject personality, ensure they sound like a real person wrote them.

## Quality Checklist

Before delivering:
- [ ] Would this make someone stop scrolling and hit "see more"?
- [ ] Does the first line work as a standalone hook?
- [ ] Does it sound like a person thinking out loud, not a brand posting?
- [ ] Is there a real insight someone can take away?
- [ ] Would your target audience share this?
- [ ] Is the white space right? (Not a wall, not broetry)
- [ ] Does it match the voice DNA?
- [ ] No engagement bait, no humble-brag, no listicle energy?
- [ ] Has it been run through the humanizer?

## Engagement Learning

Check `/knowledge/engagement/engagement_log.json` for data on what works.
Patterns to optimize for:
- Which post types drive comments vs. shares vs. profile visits
- Which topics resonate with different audience segments
- Language reach and engagement differences
- Hook patterns that drive highest "see more" click-through

## Differentiation from X/Twitter

| Dimension | Twitter | LinkedIn |
|-----------|---------|----------|
| Length | 1-3 sentences | 150-300 words |
| Depth | Observation, punch | Observation + developed thinking |
| Tone | Sharp, fast, pithy | Sharp but more grounded, authoritative |
| Promotion | Almost never | Lightly, wrapped in insight |
| Formatting | Minimal | White space, occasional bold |
