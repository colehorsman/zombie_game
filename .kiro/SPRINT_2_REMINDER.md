# 🚀 Sprint 2 Kickoff Reminder

**Scheduled Start**: 10:00 AM CST (Central Time)
**Date**: 2025-11-28

---

## ⏰ Setting Up Your Reminder

### Option 1: macOS Calendar/Reminders
1. Open Calendar or Reminders app
2. Create event: "Sprint 2 Kickoff - Zombie Blaster"
3. Set time: 10:00 AM CST
4. Set alert: 10 minutes before
5. Add note: "Open Kiro and say 'Start Sprint 2'"

### Option 2: System Cron Job (Advanced)
```bash
# Edit crontab
crontab -e

# Add this line (10 AM CST = 16:00 UTC, adjust for your timezone)
0 10 * * * osascript -e 'display notification "Time to start Sprint 2!" with title "Zombie Blaster"'
```

### Option 3: Simple Alarm
- Set phone/computer alarm for 10:00 AM
- Label: "Sprint 2 - Zombie Blaster"

---

## 📋 When 10:00 AM Arrives

### Say to Kiro:
```
"Start Sprint 2"
```

or

```
"Begin Sprint 2 planning"
```

or

```
"Let's kick off Sprint 2"
```

---

## 🎯 What Kiro Will Do

1. **Sprint Planning Ceremony** (30 min)
   - Review Sprint 2 plan
   - Create GitHub issues for all 4 stories
   - Set up feature branches
   - Confirm priorities

2. **Begin Implementation**
   - Start with FEAT-005 (Retro raygun visual)
   - Follow day-by-day plan
   - Track progress in GitHub

3. **Status Updates**
   - Provide progress updates throughout day
   - Update GitHub issues
   - Commit work regularly

---

## 📚 Reference Documents

Before starting, review:
- [Sprint 2 Plan](.kiro/specs/sprint-2-plan.md)
- [Sprint 1 Status](.kiro/specs/sprint-1-status.md)
- [Product Backlog](../docs/BACKLOG.md)

---

## ☕ Morning Checklist (Before 10 AM)

- [ ] Test Sprint 1 features (use gameplay-testing-guide.md)
- [ ] Document any bugs found
- [ ] Commit any fixes
- [ ] Review Sprint 2 plan
- [ ] Prepare development environment
- [ ] Have coffee ready ☕

---

## 🎮 Today's Focus (Before 10 AM)

**Gameplay Testing** - Validate Sprint 1 features:
- Test player damage system
- Test health UI
- Test zombie respawn on damage
- Test death/restart
- Check performance (60 FPS)
- Document feedback

See: [Gameplay Testing Guide](.kiro/specs/gameplay-testing-guide.md)

---

**Sprint 2 Goal**: "Visual Polish & Arcade Enhancements"

**Stories**:
1. FEAT-005: Retro raygun weapon visual (M)
2. FEAT-031: Arcade elimination penalty (S)
3. FEAT-032: Health power-ups (M)
4. BUG-006: Third party error fix (S)

**Estimated Duration**: 1-2 days

---

🚀 **See you at 10:00 AM CST!**
