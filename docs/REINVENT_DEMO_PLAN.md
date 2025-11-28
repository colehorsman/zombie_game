# AWS re:Invent Demo Plan
## Sonrai Zombie Blaster - Conference Edition

**Target Event:** AWS re:Invent 2025  
**Target Audience:** AWS Practitioners (Cloud Engineers, Architects, DevOps, Security)  
**Goal:** Memorable 5-minute demo that drives Sonrai booth traffic and demo requests  
**Timeline:** 1 week to implement

---

## 🎯 Audience Profile: AWS Practitioners

### Who They Are
- **Role:** Cloud Engineers, Solutions Architects, DevOps Engineers, Security Engineers
- **Experience:** 2-10 years in cloud/AWS
- **Pain Points:** IAM complexity, compliance audits, identity sprawl, third-party risk
- **Motivation:** Learn new tools, solve real problems, advance career
- **Attention Span:** 3-5 minutes at a booth

### What They Need to Learn
1. **What Sonrai does** - Cloud Permissions Firewall for identity and data protection
2. **Why it matters** - Unused identities = attack vectors, compliance failures
3. **How it works** - Real-time API integration, automated remediation
4. **Why choose Sonrai** - Intelligence, automation, ease of use

### What They DON'T Need
- ❌ Basic cloud concepts (they know AWS)
- ❌ Long tutorials (they're busy)
- ❌ Kid-friendly explanations (they're professionals)
- ❌ Certification paths (not the time/place)

---

## 🚀 Phase 1: re:Invent Ready (1 Week)

### Critical Features for Conference Demo

#### 1. **30-Second Hook** (MUST HAVE)

**The Pitch:**
> "Want to see your AWS organization as a video game? This is Sonrai Zombie Blaster - every zombie is a REAL unused identity from your AWS accounts. Watch what happens when I eliminate one..."

**The Demo:**
```
1. Show lobby with doors labeled with real AWS account names
2. Enter "Production" account
3. Point to zombie: "This is 'contractor-john' - hasn't logged in for 180 days"
4. Shoot zombie
5. Show API call animation: "ChangeQuarantineStatus → SUCCESS"
6. Show result: "Identity quarantined in your Sonrai tenant"
7. Boom - they get it in 30 seconds
```

**Implementation:**
- Add "Demo Mode" that shows API calls visually
- Slow-motion effect when eliminating first zombie
- Clear on-screen text explaining what's happening
- QR code appears: "Play with YOUR AWS data"

---

#### 2. **Live Data Integration** (MUST HAVE)

**The Magic Moment:**
> "This isn't a demo environment - these are YOUR actual unused identities. Want to see?"

**The Experience:**
```
BOOTH WORKFLOW:

1. Attendee approaches booth
2. Staff: "Want to play with your real AWS data?"
3. Attendee: "Sure!"
4. Staff: Scan QR code → Quick Sonrai trial signup
5. Game loads with THEIR AWS organization
6. They see THEIR account names on doors
7. They see THEIR unused identities as zombies
8. They eliminate one → It's ACTUALLY quarantined
9. Mind = Blown 🤯
```

**Implementation:**
- Quick onboarding flow (30 seconds)
- Pre-configured Sonrai trial accounts
- Real-time data sync
- Safety mode (can't quarantine critical identities)

---

#### 3. **Contextual Tooltips** (MUST HAVE)

**The Education:**
Every entity shows a tooltip on hover/approach:

```
ZOMBIE TOOLTIP:

┌─────────────────────────────────────────┐
│ 💀 UNUSED IDENTITY                      │
├─────────────────────────────────────────┤
│ Name: contractor-sarah                  │
│ Type: IAM User                          │
│ Last Login: 247 days ago                │
│ Permissions: S3 Full Access, EC2 Read   │
│                                         │
│ 🚨 RISK: High                           │
│ └─ Old credentials can be stolen        │
│ └─ Violates least privilege             │
│ └─ Compliance violation (SOC 2)         │
│                                         │
│ ✅ ACTION: Quarantine via Sonrai        │
│                                         │
│ [Eliminate] [Learn More]                │
└─────────────────────────────────────────┘

THIRD-PARTY TOOLTIP:

┌─────────────────────────────────────────┐
│ 🔗 THIRD-PARTY ACCESS                   │
├─────────────────────────────────────────┤
│ Name: Datadog                           │
│ Type: Monitoring Service                │
│ Access: Read CloudWatch, EC2            │
│ Last Used: 2 days ago                   │
│                                         │
│ ✅ STATUS: Active & Approved            │
│ └─ Legitimate monitoring tool           │
│ └─ Regular usage pattern                │
│                                         │
│ ⚠️ BEST PRACTICE:                       │
│ └─ Review quarterly                     │
│ └─ Rotate credentials annually          │
│                                         │
│ [Keep] [Block] [Learn More]             │
└─────────────────────────────────────────┘

PURPLE SHIELD TOOLTIP:

┌─────────────────────────────────────────┐
│ 🛡️ PROTECTED IDENTITY                   │
├─────────────────────────────────────────┤
│ Name: prod-app-service-role             │
│ Type: IAM Role                          │
│ Protection: JIT Access Enabled          │
│                                         │
│ ✅ WHY PROTECTED:                       │
│ └─ Active production service            │
│ └─ Just-In-Time access configured       │
│ └─ Exempted by security team            │
│                                         │
│ 💡 SONRAI FEATURE:                      │
│ This role requires approval for access. │
│ Temporary credentials expire after use. │
│                                         │
│ [View Policy] [Learn More]              │
└─────────────────────────────────────────┘
```

**Implementation:**
- Hover tooltips (mouse)
- Proximity tooltips (controller/keyboard)
- Toggle: "Show Details" ON/OFF
- Professional language (no kid stuff)

---

#### 4. **Stats Dashboard** (MUST HAVE)

**The Impact:**
After playing for 2-3 minutes, show them what they accomplished:

```
POST-GAME STATS:

┌─────────────────────────────────────────────────────┐
│  🎯 YOUR SECURITY IMPACT                            │
│  (Based on YOUR AWS Organization)                   │
├─────────────────────────────────────────────────────┤
│                                                     │
│  📊 IDENTITIES CLEANED                              │
│  ├─ 23 unused identities quarantined                │
│  ├─ Average age: 156 days unused                    │
│  ├─ Total permissions revoked: 47                   │
│  └─ 💡 23 potential attack vectors eliminated       │
│                                                     │
│  🔗 THIRD-PARTY RISK                                │
│  ├─ 3 risky third-parties blocked                   │
│  ├─ 5 approved third-parties kept                   │
│  └─ 💡 Attack surface reduced by 37%                │
│                                                     │
│  🛡️ COMPLIANCE IMPROVEMENT                          │
│  ├─ SOC 2: 12 violations resolved                   │
│  ├─ PCI DSS: 5 violations resolved                  │
│  ├─ ISO 27001: 8 violations resolved                │
│  └─ 💡 Audit-ready in 3 minutes of gameplay!        │
│                                                     │
│  ⏱️ TIME SAVED                                      │
│  ├─ Manual cleanup time: ~4 hours                   │
│  ├─ Sonrai automation: 3 minutes                    │
│  └─ 💡 80x faster with Sonrai!                      │
│                                                     │
│  💰 ESTIMATED RISK REDUCTION                        │
│  └─ $847K potential breach cost avoided             │
│     (based on IBM Cost of Data Breach Report)       │
│                                                     │
├─────────────────────────────────────────────────────┤
│                                                     │
│  🎯 NEXT STEPS                                      │
│                                                     │
│  ✅ Schedule a Sonrai Demo                          │
│     See the full platform in action                 │
│     [Book Demo] → QR Code                           │
│                                                     │
│  ✅ Start Free Trial                                │
│     Connect your AWS organization                   │
│     [Start Trial] → QR Code                         │
│                                                     │
│  ✅ Download Game                                   │
│     Play with your team back at the office          │
│     [Download] → QR Code                            │
│                                                     │
│  ✅ Share Your Score                                │
│     Challenge your colleagues                       │
│     [Share on LinkedIn] [Tweet]                     │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**Implementation:**
- Real calculations based on their data
- Industry benchmarks (IBM, Verizon DBIR)
- Clear CTAs with QR codes
- Social sharing built-in

---

#### 5. **"Aha!" Moments** (MUST HAVE)

**The Memorable Moments:**

**Moment 1: "That's MY Data!"**
```
When they first see their AWS account names on doors:
"Wait... that's our Production account!"
→ Instant connection to their real environment
```

**Moment 2: "Holy Sh*t, That's Real!"**
```
When they eliminate a zombie and see the API call:
"You just quarantined that identity in our Sonrai tenant!"
→ Understanding that this isn't a simulation
```

**Moment 3: "We Have HOW Many?!"**
```
When they see the zombie count:
"247 unused identities?! I had no idea..."
→ Visibility into their actual security posture
```

**Moment 4: "This Would Take Me Hours!"**
```
When they see the stats dashboard:
"Manual cleanup: 4 hours. Sonrai: 3 minutes."
→ Value proposition clicks
```

**Moment 5: "I Need to Show My Team!"**
```
When they finish:
"Can I download this? My CISO needs to see this."
→ Lead generation achieved
```

---

### Implementation Priority (1 Week Sprint)

#### Day 1-2: Core Demo Features
- [ ] Demo Mode toggle (shows API calls visually)
- [ ] Slow-motion first elimination
- [ ] On-screen explanatory text
- [ ] QR code generation system

#### Day 3-4: Tooltips & Context
- [ ] Hover/proximity tooltips for all entities
- [ ] Professional language (AWS practitioner level)
- [ ] Risk indicators (High/Medium/Low)
- [ ] Compliance violation callouts

#### Day 5-6: Stats Dashboard
- [ ] Post-game stats screen
- [ ] Real calculations from player data
- [ ] Industry benchmarks
- [ ] CTA buttons with QR codes

#### Day 7: Polish & Testing
- [ ] Booth workflow testing
- [ ] Quick onboarding flow
- [ ] Social sharing features
- [ ] Bug fixes and performance

---

## 🎪 Booth Experience Design

### Physical Setup

```
SONRAI BOOTH LAYOUT:

┌─────────────────────────────────────────────┐
│                                             │
│  [Large Screen - Game Display]             │
│  65" 4K Display showing gameplay            │
│                                             │
│  [Controller Station]                       │
│  8BitDo controller on pedestal              │
│                                             │
│  [QR Code Stands]                           │
│  "Play with YOUR AWS data"                  │
│  "Schedule a demo"                          │
│  "Download the game"                        │
│                                             │
│  [Leaderboard Display]                      │
│  "Top Scores Today"                         │
│  1. Sarah M. - 247 identities cleaned       │
│  2. John D. - 198 identities cleaned        │
│  3. Emily R. - 156 identities cleaned       │
│                                             │
│  [Sonrai Staff]                             │
│  2-3 staff members to assist                │
│                                             │
└─────────────────────────────────────────────┘
```

### Booth Staff Script

**Opening:**
> "Hey! Want to see your AWS organization as a video game? Every zombie is a real unused identity from your accounts. Takes 3 minutes - want to try?"

**During Play:**
> "See that zombie? That's 'contractor-john' - hasn't logged in for 180 days but still has S3 access. Watch what happens when you eliminate it... [shoots] ...boom! That identity just got quarantined in your Sonrai tenant. This is real, not a demo."

**After Play:**
> "You just cleaned up 23 unused identities in 3 minutes. Manually, that would take 4 hours. Want to see how Sonrai can do this across your entire AWS organization? Let's schedule a demo."

**Objection Handling:**
- "Is this safe?" → "Yes, we have safety mode enabled. Can't quarantine critical identities."
- "How much does it cost?" → "Let's talk pricing after you see the full platform. Here's a demo link."
- "We already have IAM tools." → "Great! Sonrai integrates with those. Let me show you what makes us different..."

---

## 📊 Success Metrics for re:Invent

### Engagement Metrics
- **Plays per day:** Target 100+ (10 per hour × 10 hours)
- **Average play time:** Target 3-5 minutes
- **Completion rate:** Target 80%+ (finish at least one level)

### Lead Generation
- **Demo requests:** Target 30+ scheduled demos
- **Trial signups:** Target 50+ free trials started
- **Game downloads:** Target 100+ downloads for office use

### Brand Impact
- **Social shares:** Target 50+ LinkedIn/Twitter posts
- **Booth traffic:** Top 10% most visited booths
- **Word of mouth:** "You have to see the Sonrai booth!"

### Measurement
- Built-in analytics tracking
- QR code scan tracking
- Post-event survey
- Sales team follow-up conversion rate

---

## 🎮 Demo Mode Features

### Visual Enhancements for Conference

#### 1. **API Call Visualization**

```
WHEN PLAYER ELIMINATES ZOMBIE:

┌─────────────────────────────────────────┐
│  🎯 ELIMINATING ZOMBIE...               │
├─────────────────────────────────────────┤
│                                         │
│  Identity: contractor-john              │
│  Status: Unused (180 days)              │
│                                         │
│  ⚡ CALLING SONRAI API...               │
│                                         │
│  POST /graphql                          │
│  mutation ChangeQuarantineStatus {      │
│    identities: ["contractor-john"]     │
│    action: "ADD"                        │
│  }                                      │
│                                         │
│  ⏳ Processing...                       │
│  ✅ SUCCESS!                            │
│                                         │
│  Result:                                │
│  └─ Identity quarantined                │
│  └─ All permissions revoked             │
│  └─ Access blocked                      │
│                                         │
│  [Continue]                             │
└─────────────────────────────────────────┘
```

#### 2. **Slow-Motion First Kill**

```
FIRST ZOMBIE ELIMINATION:

1. Player shoots zombie
2. Time slows to 25% speed
3. Projectile travels in slow-mo
4. Hit detection highlighted
5. Zoom in on zombie
6. API call overlay appears
7. Success animation
8. Time returns to normal
9. "You just quarantined a real identity!" message
```

#### 3. **Live Stats Ticker**

```
TOP OF SCREEN (Always Visible):

┌─────────────────────────────────────────┐
│ 🎯 Session Stats                        │
│ Identities Cleaned: 23                  │
│ Risk Reduced: 37%                       │
│ Time Saved: 4 hours                     │
│ Compliance Violations Fixed: 12         │
└─────────────────────────────────────────┘
```

---

## 🎯 Competitive Element

### Leaderboard System

**Daily Leaderboard:**
```
┌─────────────────────────────────────────┐
│  🏆 TODAY'S TOP SECURITY CHAMPIONS      │
├─────────────────────────────────────────┤
│  1. Sarah M. (AWS)                      │
│     247 identities • 4:32 time          │
│                                         │
│  2. John D. (Netflix)                   │
│     198 identities • 3:45 time          │
│                                         │
│  3. Emily R. (Airbnb)                   │
│     156 identities • 5:12 time          │
│                                         │
│  4. Mike T. (Stripe)                    │
│     142 identities • 4:01 time          │
│                                         │
│  5. Lisa K. (Uber)                      │
│     128 identities • 3:58 time          │
│                                         │
│  YOUR RANK: #12                         │
│  Beat #11 by cleaning 15 more!          │
│                                         │
│  [Play Again] [Share Score]             │
└─────────────────────────────────────────┘
```

**Features:**
- Real-time updates
- Company names (with permission)
- Friendly competition
- Social sharing
- Prize for #1 (Sonrai swag, free trial extension, etc.)

---

## 📱 QR Code Strategy

### QR Code Placement

**QR Code 1: "Play with YOUR Data"**
- Leads to: Quick Sonrai trial signup
- Placement: Booth entrance, game screen
- CTA: "See YOUR AWS organization as a game"

**QR Code 2: "Schedule Demo"**
- Leads to: Calendly booking page
- Placement: Stats dashboard, booth exit
- CTA: "See the full Sonrai platform"

**QR Code 3: "Download Game"**
- Leads to: GitHub releases page
- Placement: Stats dashboard, booth signage
- CTA: "Play with your team at the office"

**QR Code 4: "Share Score"**
- Leads to: Pre-filled LinkedIn/Twitter post
- Placement: Stats dashboard
- CTA: "Challenge your colleagues"

### Pre-filled Social Post

```
LINKEDIN POST TEMPLATE:

Just played @Sonrai Security's Zombie Blaster at #reInvent!

🎮 Cleaned up 23 unused AWS identities in 3 minutes
🛡️ Reduced attack surface by 37%
⚡ 80x faster than manual cleanup

Every zombie was a REAL unused identity from my AWS org. 
Mind = blown 🤯

If you're at re:Invent, check out booth #1234!

#CloudSecurity #AWS #IAM #GameOn
```

---

## 🎓 Educational Content for AWS Practitioners

### In-Game Tips (Rotating)

```
LOADING SCREEN TIPS:

💡 "Did you know? 60% of AWS organizations have 100+ 
   unused identities. You're not alone!"

💡 "Unused identities are the #1 cause of cloud breaches. 
   Clean them up = close attack vectors."

💡 "Purple shields = JIT access. Temporary credentials 
   that expire after use. Best practice!"

💡 "Third-party access isn't bad - it's unreviewed access 
   that's risky. Audit quarterly."

💡 "Sonrai's Cloud Permissions Firewall automates what 
   you're doing manually. 80x faster."

💡 "SOC 2 auditors LOVE clean identity hygiene. This game 
   shows you what they're looking for."

💡 "Every zombie you eliminate = one less credential for 
   hackers to steal. Simple math."

💡 "JIT access = least privilege + time-boxing. Admins 
   can still do their jobs, but access expires."
```

### Booth Handouts

**One-Pager:**
```
┌─────────────────────────────────────────┐
│  SONRAI ZOMBIE BLASTER                  │
│  Cloud Security Education Through Play  │
├─────────────────────────────────────────┤
│                                         │
│  WHAT YOU JUST PLAYED:                  │
│  • Real AWS identities as zombies       │
│  • Actual Sonrai API calls              │
│  • Your organization's security posture │
│                                         │
│  WHAT YOU LEARNED:                      │
│  • Unused identities = attack vectors   │
│  • Third-party risk management          │
│  • JIT access best practices            │
│  • Compliance requirements              │
│                                         │
│  WHAT SONRAI DOES:                      │
│  • Cloud Permissions Firewall           │
│  • Automated identity cleanup           │
│  • Real-time threat detection           │
│  • Compliance automation                │
│                                         │
│  NEXT STEPS:                            │
│  □ Schedule demo: [QR Code]             │
│  □ Start free trial: [QR Code]          │
│  □ Download game: [QR Code]             │
│                                         │
└─────────────────────────────────────────┘
```

---

## ⚡ Quick Wins (Can Implement in 1-2 Days)

### Minimal Viable Demo (MVD)

If time is extremely tight, focus on these 3 things:

1. **Tooltips on Hover** (4 hours)
   - Show identity details when hovering over zombies
   - Show risk level and last login date
   - Show "This is real data from your AWS org"

2. **Stats Dashboard** (6 hours)
   - Post-game screen showing what they accomplished
   - Real numbers from their session
   - QR codes for next steps

3. **Demo Mode Toggle** (2 hours)
   - Settings option: "Conference Demo Mode"
   - Shows API calls visually
   - Adds explanatory text

**Total: 12 hours of dev work = 1.5 days**

This alone would make the demo 10x more effective than current state.

---

## 🎯 Success Criteria for re:Invent

### Must Achieve
- ✅ 50+ people play the game
- ✅ 20+ demo requests scheduled
- ✅ 30+ trial signups
- ✅ Booth is in top 20% for traffic

### Stretch Goals
- 🎯 100+ people play
- 🎯 40+ demo requests
- 🎯 50+ trial signups
- 🎯 Booth is in top 10% for traffic
- 🎯 Social media buzz (50+ posts)

### How to Measure
- Built-in game analytics
- QR code scan tracking
- Booth staff tally counter
- Post-event survey
- Sales team follow-up

---

## 📋 Pre-Event Checklist

### 1 Week Before
- [ ] Implement tooltips
- [ ] Implement stats dashboard
- [ ] Implement demo mode
- [ ] Test with real AWS data
- [ ] Create QR codes
- [ ] Print booth materials

### 3 Days Before
- [ ] Final testing
- [ ] Staff training
- [ ] Backup plan (offline mode)
- [ ] Swag/prizes ready
- [ ] Social media posts scheduled

### Day Of
- [ ] Hardware setup (screen, controller)
- [ ] Network connectivity test
- [ ] Game running smoothly
- [ ] QR codes displayed
- [ ] Staff briefed
- [ ] Analytics tracking enabled

---

## 🚀 Post-Event Follow-Up

### Immediate (Day After)
- Send thank-you emails to all players
- Share leaderboard results
- Post highlight reel on social media

### Week After
- Sales team follows up on demo requests
- Send game download links to interested parties
- Publish blog post: "What We Learned at re:Invent"

### Month After
- Analyze conversion rates
- Gather feedback for improvements
- Plan for next conference

---

## 💡 Key Takeaway

**For re:Invent, focus on:**
1. **Speed** - 3-5 minute experience
2. **Impact** - "Aha!" moments that stick
3. **Action** - Clear next steps (demo, trial, download)

**The goal isn't to teach everything about cloud security.**  
**The goal is to make Sonrai memorable and drive follow-up conversations.**

**"That booth with the zombie game" → "Let's schedule a Sonrai demo"**

---

**Ready for re:Invent! 🎮🛡️🚀**
