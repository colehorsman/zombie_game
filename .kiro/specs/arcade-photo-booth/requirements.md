# Arcade Photo Booth - Requirements

## Overview

A retro arcade-themed photo booth experience that captures player selfies and gameplay screenshots at the end of Arcade Mode's 60-second challenge. Designed for maximum shareability and memorable booth experiences at AWS re:Invent 2025.

## Problem Statement

Conference booth experiences are forgettable. Attendees play games, get swag, and move on. We need a **shareable, viral moment** that:
1. Creates a lasting memory of the Sonrai booth
2. Drives social media engagement (#SonraiZombieBlaster)
3. Captures leads through QR code interactions
4. Reinforces the retro gaming brand identity

## Target Event

**AWS re:Invent 2025**
- Location: Las Vegas, NV
- Booth: Sonrai Security (Booth # TBD)
- Expected foot traffic: 50,000+ attendees
- Target interactions: 500+ photo booth captures

---

## User Stories

### US-1: Selfie Opt-In at Arcade Start
**As a** player starting Arcade Mode
**I want** to choose whether to include my selfie in the final photo
**So that** I have control over my privacy

**Acceptance Criteria:**
- [ ] Prompt appears before Arcade Mode countdown begins
- [ ] Clear options: "📸 Include Selfie? [A] Yes [B] No"
- [ ] Selection stored for end-of-game photo generation
- [ ] Default is "No" (privacy-first)
- [ ] 5-second timeout defaults to "No" if no input
- [ ] Controller A/B buttons and keyboard Y/N work

### US-2: Automatic Photo Capture on Arcade End
**As a** player who just completed the 60-second challenge
**I want** my photo automatically captured
**So that** I don't have to press extra buttons

**Acceptance Criteria:**
- [ ] Photo captured automatically when timer hits 0
- [ ] Webcam snapshot taken (if opted in)
- [ ] Gameplay screenshot captured at final moment
- [ ] Brief "📸 CAPTURED!" flash effect
- [ ] No additional button press required

### US-3: 8-Bit Pixelated Selfie Filter
**As a** player who opted into selfie
**I want** my photo to look like an 8-bit game character
**So that** it matches the retro aesthetic and looks cool

**Acceptance Criteria:**
- [ ] Selfie reduced to 16-color retro palette
- [ ] Pixelation effect (downsample to ~64x64, then scale up)
- [ ] Colors match game's purple/green/orange theme
- [ ] Filter applied in real-time or post-capture
- [ ] Result looks intentionally retro, not broken

### US-4: Retro Arcade Frame Composite
**As a** player viewing my photo booth result
**I want** a professionally designed retro arcade frame
**So that** it looks shareable and memorable

**Acceptance Criteria:**
- [ ] Arcade cabinet-style border with pixel art
- [ ] Two photo windows: selfie (left) + gameplay (right)
- [ ] If no selfie opted in, gameplay fills larger area
- [ ] CRT scanline overlay effect
- [ ] "INSERT COIN" footer element
- [ ] Star decorations around score
- [ ] Block/pixel typography throughout

### US-5: Score and Stats Display
**As a** player viewing my photo
**I want** to see my zombie elimination count prominently
**So that** I can brag about my score

**Acceptance Criteria:**
- [ ] Large, prominent zombie count: "★ ★ ★ 47 ZOMBIES ELIMINATED ★ ★ ★"
- [ ] "60 SECOND CHALLENGE" subtitle
- [ ] Retro pixel font styling
- [ ] Score centered and highly visible
- [ ] Optional: combo multiplier or other stats

### US-6: Sonrai Branding and Event Info
**As a** Sonrai marketing team member
**I want** clear branding on every photo
**So that** shared photos drive brand awareness

**Acceptance Criteria:**
- [ ] Sonrai logo (purple/black stacked version)
- [ ] "AWS re:Invent 2025" text
- [ ] Booth number (configurable)
- [ ] Hashtag: #SonraiZombieBlaster
- [ ] Website: sonraisecurity.com
- [ ] QR code linking to game download or demo signup

### US-7: Photo Save and Export
**As a** player who wants my photo
**I want** easy access to my photo booth image
**So that** I can share it on social media

**Acceptance Criteria:**
- [ ] Photo saved to `.kiro/evidence/booth_photos/`
- [ ] Filename: `BOOTH_YYYYMMDD_HHMMSS.png`
- [ ] High resolution (1080p minimum for social sharing)
- [ ] QR code on screen to download/share (optional)
- [ ] Optional: Email capture for photo delivery

### US-8: Webcam Configuration
**As a** booth operator
**I want** to configure which camera to use
**So that** I can use the built-in or external camera

**Acceptance Criteria:**
- [ ] Environment variable: `PHOTO_BOOTH_CAMERA_INDEX=0`
- [ ] Auto-detect available cameras
- [ ] Fallback to gameplay-only if no camera
- [ ] Support for USB webcams
- [ ] Camera preview during opt-in prompt (optional)

---

## Non-Functional Requirements

### Performance
- Photo composite generation: < 2 seconds
- Webcam capture latency: < 500ms
- No frame rate impact during gameplay
- Smooth transition to results screen

### Visual Quality
- Output resolution: 1920x1080 minimum
- PNG format for lossless quality
- Consistent color palette across all elements
- Professional, polished appearance

### Privacy
- Selfie opt-in required (not opt-out)
- No photos stored without consent
- Clear indication when camera is active
- Photos stored locally only (no cloud upload)

### Reliability
- Graceful fallback if camera unavailable
- Works without internet connection
- Handles camera permission denials
- Recovers from capture failures

### Configurability
- Booth number configurable via .env
- Event name configurable via .env
- QR code URL configurable via .env
- Camera index configurable via .env

---

## Configuration Options

```bash
# .env additions for Photo Booth
PHOTO_BOOTH_ENABLED=true
PHOTO_BOOTH_CAMERA_INDEX=0
PHOTO_BOOTH_EVENT_NAME="AWS re:Invent 2025"
PHOTO_BOOTH_BOOTH_NUMBER="435"
PHOTO_BOOTH_QR_URL="https://sonraisecurity.com/zombie-blaster"
PHOTO_BOOTH_HASHTAG="#SonraiZombieBlaster"
```

---

## Out of Scope (Future Enhancements)

- Email delivery of photos
- SMS delivery of photos
- Cloud storage/gallery
- Leaderboard integration
- Video recording (GIF) of gameplay
- Multiple player photos
- Photo printing integration
- Social media direct posting
- Face detection/framing
- AR filters/effects

---

## Success Metrics

### Engagement
- 80%+ of Arcade Mode players opt-in to selfie
- 50%+ of photos shared on social media
- 100+ #SonraiZombieBlaster posts during re:Invent

### Technical
- 99%+ photo capture success rate
- < 2 second composite generation
- Zero crashes from photo booth feature

### Marketing
- Measurable increase in booth traffic
- QR code scans tracked
- Demo signup conversion from QR codes

---

## Dependencies

- OpenCV (`cv2`) for webcam capture
- Pillow (`PIL`) for image compositing
- Existing EvidenceCapture system
- Arcade Mode completion event
- Pre-designed frame assets

---

## Assets Required

### Design Assets (to be created)
1. **Arcade frame PNG** - Transparent overlay with retro cabinet design
2. **Scanline overlay PNG** - CRT effect texture
3. **Pixel font** - For score and text rendering
4. **Star decorations** - Score embellishments
5. **QR code template** - Branded QR code frame

### Existing Assets (available)
- Sonrai logo (`assets/sonrai_logo.png`)
- Sonrai stacked logo (`assets/Sonrai logo_stacked_purple-black.png`)
- Game color palette (purple theme)

---

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Camera not available | Medium | Graceful fallback to gameplay-only photo |
| Poor lighting at booth | Medium | 8-bit filter hides quality issues |
| Privacy concerns | High | Opt-in only, clear consent, local storage |
| Slow composite generation | Low | Pre-load assets, optimize image processing |
| Camera permissions denied | Medium | Clear instructions, fallback mode |

---

## Timeline Estimate

**Total Effort:** 16-24 hours

- Requirements & Design: 2-3 hours ✅
- Frame asset design: 4-6 hours
- Webcam integration: 3-4 hours
- 8-bit filter implementation: 2-3 hours
- Composite generation: 3-4 hours
- Testing & polish: 2-4 hours

**Target Completion:** Before re:Invent 2025

---

## Approval

- [ ] Product Manager: Approved
- [ ] UX/Design Agent: Approved
- [ ] Architecture Agent: Approved
- [ ] Marketing Team: Approved

---

*This feature will make Sonrai's booth THE must-visit destination at re:Invent 2025!* 🎮📸🧟
