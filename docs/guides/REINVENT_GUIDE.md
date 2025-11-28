# AWS re:Invent Demo Guide
## Sonrai Zombie Blaster - Conference Edition

**Event:** AWS re:Invent (December 1-2, 2025)
**Target Audience:** AWS Practitioners (Cloud Engineers, Architects, DevOps, Security)
**Goal:** Memorable demo that drives Sonrai booth traffic and leads
**Status:** Ready for deployment

---

## Table of Contents

<details>
<summary><b>📋 Quick Reference</b></summary>

- [Executive Summary](#executive-summary)
- [Booth Setup](#booth-setup)
- [Demo Flow](#demo-flow)
- [Staff Script](#staff-script)
- [Success Metrics](#success-metrics)

</details>

<details>
<summary><b>🎯 Strategy & Planning</b></summary>

- [Audience Profile](#audience-profile)
- [The Pitch](#the-pitch)
- [Key Features](#key-features)
- [Aha Moments](#aha-moments)

</details>

<details>
<summary><b>🎪 Booth Experience</b></summary>

- [Physical Setup](#physical-setup)
- [Workflow](#workflow)
- [QR Codes](#qr-codes)
- [Leaderboard](#leaderboard)

</details>

<details>
<summary><b>📊 Measurement & Follow-up</b></summary>

- [Analytics](#analytics)
- [Lead Capture](#lead-capture)
- [Post-Event](#post-event)

</details>

---

## Executive Summary

### The Strategy

**Problem:** Conference attendees have 3-5 minutes at a booth. Need to quickly communicate what Sonrai does, why it matters, and drive action.

**Solution:** Transform gameplay into educational experience with:
1. **Contextual tooltips** - Educate without interrupting
2. **Stats dashboard** - Show real-world impact
3. **Live data** - Use their actual AWS organization

**Impact:**
**Before:** "That was a fun zombie game"
**After:** "I just quarantined 23 real identities in 3 minutes. We need Sonrai."

### ROI Projection

**Investment:** ~$13K (dev, booth setup, staff)
**Expected Return:** $550K pipeline (30 demos + 50 trials)
**ROI:** 42x

---

## Audience Profile

### Who They Are
- **Roles:** Cloud Engineers, Solutions Architects, DevOps, Security Engineers
- **Experience:** 2-10 years in cloud/AWS
- **Pain Points:** IAM complexity, compliance audits, identity sprawl, third-party risk
- **Attention Span:** 3-5 minutes at booth

### What They Need
1. What Sonrai does (Cloud Permissions Firewall)
2. Why it matters (unused identities = attack vectors)
3. How it works (real-time API, automated remediation)
4. What to do next (demo, trial, download)

### What They DON'T Need
- ❌ Basic cloud concepts (they know AWS)
- ❌ Long tutorials (they're busy)
- ❌ Kid-friendly explanations (they're professionals)

---

## The Pitch

### 30-Second Hook

> "Want to see your AWS organization as a video game? This is Sonrai Zombie Blaster - every zombie is a REAL unused identity from your AWS accounts. Watch what happens when I eliminate one..."

### The Demo Flow

```
1. Show lobby with real AWS account names
2. Enter "Production" account
3. Point to zombie: "contractor-john - 180 days unused"
4. Shoot zombie
5. Show API call: "ChangeQuarantineStatus → SUCCESS"
6. Result: "Identity quarantined in your Sonrai tenant"
7. Boom - they get it in 30 seconds
```

---

## Key Features

### 1. Contextual Tooltips

**What:** Hover over any entity to see details
**Why:** Educates without interrupting gameplay

**Example - Zombie:**
```
💀 UNUSED IDENTITY
Name: contractor-sarah
Type: IAM User
Last Login: 247 days ago
Permissions: S3 Full Access, EC2 Read

🚨 RISK: High
└─ Old credentials can be stolen
└─ Violates least privilege
└─ Compliance violation (SOC 2)

✅ ACTION: Quarantine via Sonrai
```

**Example - Protected Identity:**
```
🛡️ PROTECTED IDENTITY
Name: prod-app-service-role
Protection: JIT Access Enabled

✅ WHY PROTECTED:
└─ Active production service
└─ Just-In-Time access configured
└─ Exempted by security team

💡 SONRAI FEATURE:
Requires approval for access.
Temporary credentials expire after use.
```

### 2. Stats Dashboard

**What:** Post-game screen showing real-world impact
**Why:** Connects gameplay to business value

**Example:**
```
🎯 YOUR SECURITY IMPACT

📊 IDENTITIES CLEANED
├─ 23 unused identities quarantined
└─ 💡 23 potential attack vectors eliminated

⏱️ TIME SAVED
├─ Manual cleanup: ~4 hours
├─ Sonrai automation: 3 minutes
└─ 💡 80x faster with Sonrai!

🛡️ COMPLIANCE
├─ 12 violations resolved
└─ 💡 Audit-ready in minutes!

💰 ESTIMATED RISK REDUCTION
└─ $847K potential breach cost avoided

📱 NEXT STEPS:
[Schedule Demo] [Start Trial] [Download]
```

### 3. Live Data Integration

**What:** Use attendee's actual AWS organization
**Why:** Makes it personal and real

**Workflow:**
1. Attendee scans QR code
2. Quick Sonrai trial signup (30 seconds)
3. Game loads with THEIR AWS data
4. They see THEIR account names
5. They eliminate THEIR unused identities
6. Mind = Blown 🤯

---

## Aha Moments

### The 5 Key Moments

1. **"That's MY Data!"**
   When they see their AWS account names on doors

2. **"Holy Sh*t, That's Real!"**
   When they see actual API calls happening

3. **"We Have HOW Many?!"**
   When they see their zombie count (247 unused identities)

4. **"This Would Take Me Hours!"**
   When they see time savings (4 hours → 3 minutes)

5. **"I Need to Show My Team!"**
   When they finish and want to share

---

## Booth Setup

### Physical Layout

```
SONRAI BOOTH:

┌─────────────────────────────────────┐
│  [Large Screen - 65" 4K Display]   │
│  Gameplay visible from distance     │
│                                     │
│  [Controller Station]               │
│  8BitDo controller on pedestal      │
│                                     │
│  [QR Code Stands]                   │
│  • Play with YOUR data              │
│  • Schedule demo                    │
│  • Download game                    │
│                                     │
│  [Leaderboard Display]              │
│  Top scores today                   │
│                                     │
│  [Sonrai Staff - 2-3 people]        │
│                                     │
└─────────────────────────────────────┘
```

### Equipment Checklist

- [ ] 65" 4K display
- [ ] 8BitDo Bluetooth controller
- [ ] Laptop/gaming PC
- [ ] QR code stands (4)
- [ ] Leaderboard display
- [ ] Backup controller
- [ ] Network connectivity
- [ ] Power strips
- [ ] Sonrai swag/prizes

---

## Demo Flow

### The Complete Experience (3-5 minutes)

**1. Attract (30 seconds)**
- Staff: "Want to see YOUR AWS organization as a game?"
- Attendee approaches
- Show gameplay on screen

**2. Onboard (30 seconds)**
- Scan QR code for trial signup
- Game loads with their data
- Brief controls explanation

**3. Play (2-3 minutes)**
- Navigate lobby
- Enter account
- Eliminate zombies
- See tooltips
- Experience API calls

**4. Impact (1 minute)**
- Stats dashboard appears
- Show what they accomplished
- Real numbers, real impact

**5. Convert (30 seconds)**
- QR codes for next steps
- Schedule demo
- Start trial
- Download game

---

## Staff Script

### Opening

> "Hey! Want to see your AWS organization as a video game? Every zombie is a real unused identity from your accounts. Takes 3 minutes - want to try?"

### During Play

> "See that zombie? That's 'contractor-john' - hasn't logged in for 180 days but still has S3 access. Watch what happens when you eliminate it... [shoots] ...boom! That identity just got quarantined in your Sonrai tenant. This is real, not a demo."

### After Play

> "You just cleaned up 23 unused identities in 3 minutes. Manually, that would take 4 hours. Want to see how Sonrai can do this across your entire AWS organization? Let's schedule a demo."

### Objection Handling

**"Is this safe?"**
→ "Yes, safety mode enabled. Can't quarantine critical identities."

**"How much does it cost?"**
→ "Let's talk pricing after you see the full platform. Here's a demo link."

**"We already have IAM tools."**
→ "Great! Sonrai integrates with those. Let me show you what makes us different..."

---

## QR Codes

### QR Code Strategy

**QR Code 1: "Play with YOUR Data"**
- Destination: Quick Sonrai trial signup
- Placement: Booth entrance, game screen
- CTA: "See YOUR AWS organization as a game"

**QR Code 2: "Schedule Demo"**
- Destination: Calendly booking page
- Placement: Stats dashboard, booth exit
- CTA: "See the full Sonrai platform"

**QR Code 3: "Download Game"**
- Destination: GitHub releases page
- Placement: Stats dashboard, booth signage
- CTA: "Play with your team at the office"

**QR Code 4: "Share Score"**
- Destination: Pre-filled LinkedIn/Twitter post
- Placement: Stats dashboard
- CTA: "Challenge your colleagues"

### Pre-filled Social Post

```
Just played @Sonrai Security's Zombie Blaster at #reInvent!

🎮 Cleaned up 23 unused AWS identities in 3 minutes
🛡️ Reduced attack surface by 37%
⚡ 80x faster than manual cleanup

Every zombie was a REAL unused identity from my AWS org.
Mind = blown 🤯

If you're at re:Invent, check out booth #1234!

#CloudSecurity #AWS #IAM
```

---

## Leaderboard

### Daily Competition

```
🏆 TODAY'S TOP SECURITY CHAMPIONS

1. Sarah M. (AWS)
   247 identities • 4:32 time

2. John D. (Netflix)
   198 identities • 3:45 time

3. Emily R. (Airbnb)
   156 identities • 5:12 time

YOUR RANK: #12
Beat #11 by cleaning 15 more!

[Play Again] [Share Score]
```

**Features:**
- Real-time updates
- Company names (with permission)
- Friendly competition
- Prize for #1 (Sonrai swag)

---

## Success Metrics

### Engagement Targets
- **Plays per day:** 100+ (10/hour × 10 hours)
- **Average play time:** 3-5 minutes
- **Completion rate:** 80%+ finish one level

### Lead Generation Targets
- **Demo requests:** 30+ scheduled
- **Trial signups:** 50+ started
- **Game downloads:** 100+ for office use

### Brand Impact Targets
- **Social shares:** 50+ LinkedIn/Twitter posts
- **Booth traffic:** Top 10% most visited
- **Word of mouth:** "You have to see the Sonrai booth!"

### Measurement Methods
- Built-in game analytics
- QR code scan tracking
- Booth staff tally counter
- Post-event survey
- Sales team follow-up conversion

---

## Pre-Event Checklist

### 1 Week Before
- [ ] Game features complete
- [ ] Test with real AWS data
- [ ] Create QR codes
- [ ] Print booth materials
- [ ] Train staff
- [ ] Backup plan ready

### 3 Days Before
- [ ] Final testing
- [ ] Staff training session
- [ ] Swag/prizes ready
- [ ] Social media posts scheduled
- [ ] Booth layout confirmed

### Day Of
- [ ] Hardware setup
- [ ] Network connectivity test
- [ ] Game running smoothly
- [ ] QR codes displayed
- [ ] Staff briefed
- [ ] Analytics enabled

---

## Post-Event Follow-Up

### Immediate (Day After)
- Send thank-you emails to all players
- Share leaderboard results
- Post highlight reel on social media

### Week After
- Sales team follows up on demo requests
- Send game download links
- Publish blog post: "What We Learned at re:Invent"

### Month After
- Analyze conversion rates
- Gather feedback for improvements
- Plan for next conference

---

## Technical Setup

### Game Configuration

```bash
# .env settings for re:Invent
DEMO_MODE=true
SHOW_TOOLTIPS=true
SHOW_API_CALLS=true
SHOW_STATS_DASHBOARD=true
ENABLE_LEADERBOARD=true
```

### Running the Demo

```bash
# Start game in demo mode
python src/main.py --demo-mode

# Test with sample data
python src/main.py --demo-mode --sample-data

# Enable analytics
python src/main.py --demo-mode --analytics
```

---

## Key Takeaways

### For re:Invent, Focus On:

1. **Speed** - 3-5 minute experience
2. **Impact** - "Aha!" moments that stick
3. **Action** - Clear next steps (demo, trial, download)

### The Goal

**Not:** Teach everything about cloud security
**But:** Make Sonrai memorable and drive follow-up conversations

**"That booth with the zombie game" → "Let's schedule a Sonrai demo"**

---

## Contact & Support

**Booth Staff Lead:** [Name]
**Technical Support:** [Name]
**Emergency Contact:** [Phone]

**Documentation:**
- Full demo plan: This document
- Technical setup: DEPLOYMENT.md
- Troubleshooting: TROUBLESHOOTING.md

---

**Ready for re:Invent! 🎮🛡️🚀**

**Last Updated:** November 28, 2024
**Next Review:** After re:Invent (December 3, 2025)
