# re:Invent Implementation Guide
## 1-Week Sprint to Conference-Ready Demo

**Timeline:** 7 days  
**Target:** AWS re:Invent booth demo  
**Priority:** High-impact features that make Sonrai memorable

---

## 🎯 Implementation Strategy

### The 80/20 Rule
Focus on 20% of features that deliver 80% of impact:
1. **Tooltips** - Educate without interrupting gameplay
2. **Stats Dashboard** - Show real-world impact
3. **Demo Mode** - Make API calls visible

These 3 features transform the demo from "fun game" to "memorable learning experience."

---

## 📅 7-Day Sprint Plan

### Day 1-2: Tooltips System (12 hours)

**Goal:** Show context for every entity

**Implementation:**

```python
# src/tooltip.py

class Tooltip:
    """Display contextual information for game entities."""
    
    def __init__(self, screen, font):
        self.screen = screen
        self.font = font
        self.active_tooltip = None
        self.tooltip_timer = 0.0
        
    def show_zombie_tooltip(self, zombie, mouse_pos):
        """Show tooltip for zombie entity."""
        # Calculate days since last login
        days_unused = zombie.days_unused if hasattr(zombie, 'days_unused') else 180
        
        # Determine risk level
        if days_unused < 30:
            risk = "LOW"
            risk_color = (100, 200, 100)
        elif days_unused < 90:
            risk = "MEDIUM"
            risk_color = (200, 200, 100)
        elif days_unused < 180:
            risk = "HIGH"
            risk_color = (255, 165, 0)
        else:
            risk = "CRITICAL"
            risk_color = (255, 50, 50)
        
        tooltip_text = [
            f"💀 UNUSED IDENTITY",
            f"",
            f"Name: {zombie.identity_name}",
            f"Type: IAM User",
            f"Last Login: {days_unused} days ago",
            f"",
            f"🚨 RISK: {risk}",
            f"└─ Old credentials can be stolen",
            f"└─ Violates least privilege",
            f"",
            f"✅ ACTION: Quarantine via Sonrai",
        ]
        
        self._render_tooltip(tooltip_text, mouse_pos, risk_color)
    
    def show_third_party_tooltip(self, third_party, mouse_pos):
        """Show tooltip for third-party entity."""
        tooltip_text = [
            f"🔗 THIRD-PARTY ACCESS",
            f"",
            f"Name: {third_party.name}",
            f"Type: External Service",
            f"Last Used: 2 days ago",
            f"",
            f"✅ STATUS: Active & Approved",
            f"└─ Legitimate monitoring tool",
            f"",
            f"⚠️ BEST PRACTICE:",
            f"└─ Review quarterly",
        ]
        
        self._render_tooltip(tooltip_text, mouse_pos, (100, 200, 255))
    
    def show_protected_tooltip(self, entity, mouse_pos):
        """Show tooltip for protected entity."""
        tooltip_text = [
            f"🛡️ PROTECTED IDENTITY",
            f"",
            f"Name: {entity.identity_name}",
            f"Protection: JIT Access Enabled",
            f"",
            f"✅ WHY PROTECTED:",
            f"└─ Active production service",
            f"└─ Just-In-Time access configured",
            f"",
            f"💡 SONRAI FEATURE:",
            f"Requires approval for access.",
            f"Temporary credentials expire.",
        ]
        
        self._render_tooltip(tooltip_text, mouse_pos, (180, 100, 255))
    
    def _render_tooltip(self, lines, position, border_color):
        """Render tooltip box with text."""
        padding = 10
        line_height = 20
        
        # Calculate dimensions
        max_width = max(self.font.size(line)[0] for line in lines)
        width = max_width + padding * 2
        height = len(lines) * line_height + padding * 2
        
        # Position (avoid screen edges)
        x = min(position[0] + 20, self.screen.get_width() - width - 10)
        y = min(position[1] + 20, self.screen.get_height() - height - 10)
        
        # Draw background
        bg_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        bg_surface.fill((20, 20, 30, 240))  # Semi-transparent dark
        self.screen.blit(bg_surface, (x, y))
        
        # Draw border
        pygame.draw.rect(self.screen, border_color, (x, y, width, height), 2)
        
        # Draw text
        for i, line in enumerate(lines):
            text_surface = self.font.render(line, True, (255, 255, 255))
            self.screen.blit(text_surface, (x + padding, y + padding + i * line_height))
```

**Integration in game_engine.py:**

```python
# In GameEngine.__init__
self.tooltip_system = Tooltip(self.screen, pygame.font.Font(None, 16))

# In GameEngine.update()
def update(self, delta_time):
    # ... existing code ...
    
    # Update tooltips based on mouse position
    mouse_pos = pygame.mouse.get_pos()
    
    # Check if hovering over zombie
    for zombie in self.zombies:
        if zombie.get_bounds().collidepoint(mouse_pos):
            self.tooltip_system.show_zombie_tooltip(zombie, mouse_pos)
            break
    
    # Check if hovering over third-party
    if self.game_map:
        for third_party in self.game_map.third_parties:
            if third_party.get_bounds().collidepoint(mouse_pos):
                self.tooltip_system.show_third_party_tooltip(third_party, mouse_pos)
                break
```

**Testing:**
- Hover over zombies → See identity details
- Hover over third-parties → See service info
- Hover over purple shields → See protection reason

---

### Day 3-4: Stats Dashboard (12 hours)

**Goal:** Show real-world impact after gameplay

**Implementation:**

```python
# src/stats_dashboard.py

class StatsDashboard:
    """Display post-game statistics and impact."""
    
    def __init__(self, screen, font):
        self.screen = screen
        self.font = font
        self.title_font = pygame.font.Font(None, 48)
        self.subtitle_font = pygame.font.Font(None, 24)
    
    def show(self, game_state):
        """Display comprehensive stats dashboard."""
        # Calculate stats
        identities_cleaned = game_state.zombies_quarantined
        third_parties_blocked = game_state.third_parties_blocked
        
        # Calculate time saved (assume 10 min per identity manually)
        time_saved_minutes = identities_cleaned * 10
        time_saved_hours = time_saved_minutes / 60
        
        # Calculate risk reduction
        attack_surface_reduction = min(100, (identities_cleaned / game_state.total_zombies) * 100)
        
        # Calculate compliance violations fixed
        compliance_violations = identities_cleaned // 2  # Rough estimate
        
        # Calculate estimated cost avoidance (IBM: $4.45M avg breach cost)
        # Assume each unused identity = 0.5% breach risk
        risk_reduction_dollars = (identities_cleaned * 0.005) * 4_450_000
        
        # Render dashboard
        self._render_dashboard(
            identities_cleaned,
            third_parties_blocked,
            time_saved_hours,
            attack_surface_reduction,
            compliance_violations,
            risk_reduction_dollars
        )
    
    def _render_dashboard(self, identities, third_parties, time_saved, 
                          attack_reduction, compliance, cost_avoided):
        """Render the stats dashboard."""
        # Background
        bg = pygame.Surface((800, 600), pygame.SRCALPHA)
        bg.fill((20, 20, 30, 250))
        x = (self.screen.get_width() - 800) // 2
        y = (self.screen.get_height() - 600) // 2
        self.screen.blit(bg, (x, y))
        
        # Border
        pygame.draw.rect(self.screen, (100, 200, 255), (x, y, 800, 600), 3)
        
        # Title
        title = self.title_font.render("🎯 YOUR SECURITY IMPACT", True, (100, 200, 255))
        self.screen.blit(title, (x + 50, y + 30))
        
        # Stats sections
        y_offset = y + 100
        
        # Identities cleaned
        self._render_stat_section(
            x + 50, y_offset,
            "📊 IDENTITIES CLEANED",
            [
                f"{identities} unused identities quarantined",
                f"💡 {identities} potential attack vectors eliminated"
            ]
        )
        y_offset += 80
        
        # Third-party risk
        if third_parties > 0:
            self._render_stat_section(
                x + 50, y_offset,
                "🔗 THIRD-PARTY RISK",
                [
                    f"{third_parties} risky third-parties blocked",
                    f"💡 Attack surface reduced by {attack_reduction:.0f}%"
                ]
            )
            y_offset += 80
        
        # Time saved
        self._render_stat_section(
            x + 50, y_offset,
            "⏱️ TIME SAVED",
            [
                f"Manual cleanup time: ~{time_saved:.1f} hours",
                f"Sonrai automation: 3 minutes",
                f"💡 {time_saved * 20:.0f}x faster with Sonrai!"
            ]
        )
        y_offset += 100
        
        # Compliance
        if compliance > 0:
            self._render_stat_section(
                x + 50, y_offset,
                "🛡️ COMPLIANCE",
                [
                    f"{compliance} violations resolved",
                    f"💡 Audit-ready in minutes!"
                ]
            )
            y_offset += 80
        
        # Cost avoidance
        self._render_stat_section(
            x + 50, y_offset,
            "💰 ESTIMATED RISK REDUCTION",
            [
                f"${cost_avoided/1000:.0f}K potential breach cost avoided",
                f"(based on IBM Cost of Data Breach Report)"
            ]
        )
        
        # CTAs at bottom
        self._render_ctas(x, y + 550)
    
    def _render_stat_section(self, x, y, title, lines):
        """Render a stat section."""
        # Title
        title_surface = self.subtitle_font.render(title, True, (255, 200, 100))
        self.screen.blit(title_surface, (x, y))
        
        # Lines
        for i, line in enumerate(lines):
            line_surface = self.font.render(line, True, (255, 255, 255))
            self.screen.blit(line_surface, (x + 20, y + 30 + i * 25))
    
    def _render_ctas(self, x, y):
        """Render call-to-action buttons."""
        cta_text = self.font.render(
            "📱 Scan QR codes for: Demo | Trial | Download | Share",
            True, (100, 200, 255)
        )
        self.screen.blit(cta_text, (x + 50, y))
```

**Integration:**

```python
# In GameEngine
def _return_to_lobby(self, mark_completed=False):
    # ... existing code ...
    
    # Show stats dashboard if player cleaned up identities
    if self.game_state.zombies_quarantined > 0:
        self.stats_dashboard.show(self.game_state)
        self.game_state.status = GameStatus.PAUSED
        self.game_state.congratulations_message = "STATS_DASHBOARD"
```

---

### Day 5-6: Demo Mode (8 hours)

**Goal:** Make API calls visible and educational

**Implementation:**

```python
# src/demo_mode.py

class DemoMode:
    """Conference demo mode with visual API calls."""
    
    def __init__(self, screen, font):
        self.screen = screen
        self.font = font
        self.enabled = False
        self.api_call_queue = []
        self.current_api_call = None
        self.api_call_timer = 0.0
    
    def show_api_call(self, identity_name, action="quarantine"):
        """Show API call visualization."""
        api_call = {
            'identity': identity_name,
            'action': action,
            'status': 'calling',
            'timer': 0.0
        }
        self.current_api_call = api_call
    
    def update(self, delta_time):
        """Update API call animation."""
        if not self.current_api_call:
            return
        
        self.current_api_call['timer'] += delta_time
        
        # Progress through states
        if self.current_api_call['timer'] > 2.0:
            self.current_api_call['status'] = 'success'
        elif self.current_api_call['timer'] > 1.0:
            self.current_api_call['status'] = 'processing'
        
        # Clear after 3 seconds
        if self.current_api_call['timer'] > 3.0:
            self.current_api_call = None
    
    def render(self):
        """Render API call overlay."""
        if not self.enabled or not self.current_api_call:
            return
        
        # Semi-transparent overlay
        overlay = pygame.Surface((600, 400), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        
        x = (self.screen.get_width() - 600) // 2
        y = (self.screen.get_height() - 400) // 2
        
        self.screen.blit(overlay, (x, y))
        
        # Border
        pygame.draw.rect(self.screen, (100, 200, 255), (x, y, 600, 400), 3)
        
        # Content based on status
        call = self.current_api_call
        y_offset = y + 50
        
        # Title
        title = self.font.render("⚡ CALLING SONRAI API...", True, (100, 200, 255))
        self.screen.blit(title, (x + 50, y_offset))
        y_offset += 50
        
        # Identity
        identity_text = self.font.render(
            f"Identity: {call['identity']}", 
            True, (255, 255, 255)
        )
        self.screen.blit(identity_text, (x + 50, y_offset))
        y_offset += 40
        
        # API call
        api_lines = [
            "POST /graphql",
            "mutation ChangeQuarantineStatus {",
            f"  identities: [\"{call['identity']}\"]",
            "  action: \"ADD\"",
            "}"
        ]
        
        for line in api_lines:
            line_surface = self.font.render(line, True, (200, 200, 200))
            self.screen.blit(line_surface, (x + 50, y_offset))
            y_offset += 25
        
        y_offset += 20
        
        # Status
        if call['status'] == 'calling':
            status_text = "⏳ Calling API..."
            status_color = (255, 200, 100)
        elif call['status'] == 'processing':
            status_text = "⏳ Processing..."
            status_color = (255, 200, 100)
        else:  # success
            status_text = "✅ SUCCESS!"
            status_color = (100, 255, 100)
        
        status_surface = self.font.render(status_text, True, status_color)
        self.screen.blit(status_surface, (x + 50, y_offset))
        y_offset += 40
        
        # Result
        if call['status'] == 'success':
            result_lines = [
                "Result:",
                "└─ Identity quarantined",
                "└─ All permissions revoked",
                "└─ Access blocked"
            ]
            for line in result_lines:
                line_surface = self.font.render(line, True, (100, 255, 100))
                self.screen.blit(line_surface, (x + 50, y_offset))
                y_offset += 25
```

**Integration:**

```python
# In GameEngine.__init__
self.demo_mode = DemoMode(self.screen, pygame.font.Font(None, 20))
self.demo_mode.enabled = True  # Enable for conference

# When zombie is eliminated
def _eliminate_zombie(self, zombie):
    # Show API call in demo mode
    if self.demo_mode.enabled:
        self.demo_mode.show_api_call(zombie.identity_name)
    
    # ... existing elimination code ...

# In render loop
def render(self):
    # ... existing rendering ...
    
    # Render demo mode overlay
    if self.demo_mode.enabled:
        self.demo_mode.render()
```

---

### Day 7: Polish & Testing (8 hours)

**Checklist:**
- [ ] Test all tooltips (zombie, third-party, protected)
- [ ] Test stats dashboard with various scenarios
- [ ] Test demo mode API visualization
- [ ] Performance testing (60 FPS maintained)
- [ ] Booth workflow dry run
- [ ] QR code generation
- [ ] Backup plan (offline mode)
- [ ] Staff training materials

---

## 🚀 Quick Start Commands

```bash
# Enable demo mode
# In .env file:
DEMO_MODE=true
SHOW_TOOLTIPS=true
SHOW_API_CALLS=true

# Run game in demo mode
python src/main.py --demo-mode

# Test with sample data
python src/main.py --demo-mode --sample-data
```

---

## 📊 Testing Checklist

### Functionality
- [ ] Tooltips appear on hover
- [ ] Tooltips show correct information
- [ ] Stats dashboard calculates correctly
- [ ] Demo mode shows API calls
- [ ] QR codes are scannable
- [ ] Game runs at 60 FPS

### User Experience
- [ ] 3-5 minute play session
- [ ] Clear "aha!" moments
- [ ] Easy to understand
- [ ] Memorable takeaways
- [ ] Clear next steps

### Booth Workflow
- [ ] Quick onboarding (30 seconds)
- [ ] Smooth gameplay
- [ ] Stats dashboard impactful
- [ ] QR codes drive action
- [ ] Staff can explain easily

---

## 🎯 Success Metrics

**Must Have:**
- ✅ Tooltips working
- ✅ Stats dashboard showing
- ✅ Demo mode enabled

**Nice to Have:**
- 🎯 Leaderboard system
- 🎯 Social sharing
- 🎯 Slow-motion first kill
- 🎯 Live stats ticker

**Can Skip:**
- ⏸️ Tutorial system (too long for booth)
- ⏸️ Certification mode (not relevant)
- ⏸️ Parent dashboard (wrong audience)

---

## 💡 Pro Tips

1. **Keep it Simple** - Don't over-engineer. 3 features done well > 10 features half-done.

2. **Test with Real Data** - Use actual AWS organizations to verify calculations.

3. **Practice the Pitch** - Staff should be able to explain in 30 seconds.

4. **Have a Backup** - Offline mode if network fails.

5. **Measure Everything** - Analytics on plays, QR scans, demo requests.

---

**Ready to ship! 🚀**
