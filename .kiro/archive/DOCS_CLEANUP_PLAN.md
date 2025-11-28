# Documentation Cleanup Plan

## 📊 Current State Analysis

### Root docs/ Files (16 files, 4,500+ lines)

**Keep (Core Documentation):**
- ✅ `README.md` (187 lines) - Documentation hub
- ✅ `BACKLOG.md` (252 lines) - Project roadmap
- ✅ `ARCHITECTURE.md` (171 lines) - System design
- ✅ `GLOSSARY.md` (294 lines) - Security terms
- ✅ `CHEAT_CODES.md` (43 lines) - Admin commands
- ✅ `POWERUPS.md` (163 lines) - Game mechanics

**Consolidate (Redundant/Overlapping):**
- 🔄 `ARCADE_MODE.md` (211 lines) → Move to `guides/ARCADE_MODE.md`
- 🔄 `EDUCATIONAL_ANALYSIS_SUMMARY.md` (228 lines) → Merge into `EDUCATIONAL_ENHANCEMENT_RECOMMENDATIONS.md`
- 🔄 `EDUCATIONAL_ENHANCEMENT_RECOMMENDATIONS.md` (784 lines) → Move to `reference/EDUCATIONAL_STRATEGY.md`
- 🔄 `REINVENT_EXECUTIVE_SUMMARY.md` (203 lines) → Merge into `REINVENT_DEMO_PLAN.md`
- 🔄 `REINVENT_IMPLEMENTATION_GUIDE.md` (584 lines) → Merge into `REINVENT_DEMO_PLAN.md`
- 🔄 `REINVENT_DEMO_PLAN.md` (713 lines) → Keep as consolidated re:Invent doc

**Move to Appropriate Folders:**
- 📁 `jit-quest-api-plan.md` (222 lines) → Move to `sonrai-api/jit-quest-plan.md`
- 📁 `service-protection-quest-summary.md` (361 lines) → Move to `reference/SERVICE_PROTECTION_QUEST.md`

**Archive/Remove:**
- 🗑️ `mcp_diagnosis_for_sonrai.md` (144 lines) → Delete (outdated troubleshooting)
- 🗑️ `DOCUMENTATION_STANDARDS.md` (393 lines) → Delete (duplicates `.kiro/steering/documentation-agent.md`)

---

## 🎯 Proposed Structure

### After Cleanup:

```
docs/
├── README.md                           # Documentation hub (keep)
├── BACKLOG.md                          # Project roadmap (keep)
├── ARCHITECTURE.md                     # System design (keep)
├── GLOSSARY.md                         # Security terms (keep)
├── CHEAT_CODES.md                      # Admin commands (keep)
├── POWERUPS.md                         # Game mechanics (keep)
├── REINVENT_DEMO_PLAN.md              # Consolidated re:Invent guide (keep)
│
├── guides/                             # How-to guides
│   ├── ARCADE_MODE.md                 # Moved from root
│   └── ... (existing guides)
│
├── reference/                          # Reference documentation
│   ├── EDUCATIONAL_STRATEGY.md        # Consolidated educational docs
│   ├── SERVICE_PROTECTION_QUEST.md    # Moved from root
│   └── ... (existing reference)
│
└── sonrai-api/                         # API documentation
    ├── jit-quest-plan.md              # Moved from root
    └── ... (existing API docs)
```

---

## 📋 Action Plan

### Step 1: Consolidate re:Invent Docs
**Merge 3 files into 1:**
- Combine `REINVENT_EXECUTIVE_SUMMARY.md` + `REINVENT_IMPLEMENTATION_GUIDE.md` + `REINVENT_DEMO_PLAN.md`
- Result: Single comprehensive `REINVENT_DEMO_PLAN.md`
- Delete the 2 redundant files

### Step 2: Consolidate Educational Docs
**Merge 2 files into 1:**
- Combine `EDUCATIONAL_ANALYSIS_SUMMARY.md` + `EDUCATIONAL_ENHANCEMENT_RECOMMENDATIONS.md`
- Result: `reference/EDUCATIONAL_STRATEGY.md`
- Delete the 2 redundant files

### Step 3: Move Files to Appropriate Folders
- Move `ARCADE_MODE.md` → `guides/ARCADE_MODE.md`
- Move `jit-quest-api-plan.md` → `sonrai-api/jit-quest-plan.md`
- Move `service-protection-quest-summary.md` → `reference/SERVICE_PROTECTION_QUEST.md`

### Step 4: Delete Obsolete Files
- Delete `mcp_diagnosis_for_sonrai.md` (outdated)
- Delete `DOCUMENTATION_STANDARDS.md` (duplicates steering file)

---

## 📊 Impact

### Before Cleanup:
- **16 files** in root docs/
- **4,500+ lines** of documentation
- **Redundant content** across multiple files
- **Unclear organization** (what goes where?)

### After Cleanup:
- **7 files** in root docs/ (core docs only)
- **~2,000 lines** in root (56% reduction)
- **No redundancy** (each doc has clear purpose)
- **Clear organization** (guides/, reference/, sonrai-api/)

### Benefits:
✅ Easier to find documentation
✅ No duplicate/conflicting information
✅ Clearer structure for new contributors
✅ Better for Kiroween judges (less noise)
✅ Maintains all valuable content

---

## 🚀 Execution

### Consolidate re:Invent Docs (Priority 1)

**Create:** `docs/REINVENT_DEMO_PLAN.md` (consolidated)

**Structure:**
```markdown
# AWS re:Invent Demo Plan - Complete Guide

## Executive Summary
[Content from REINVENT_EXECUTIVE_SUMMARY.md]

## Demo Strategy
[Content from REINVENT_DEMO_PLAN.md]

## Implementation Guide
[Content from REINVENT_IMPLEMENTATION_GUIDE.md]

## Timeline & Checklist
[Combined from all 3 files]
```

**Delete:**
- `docs/REINVENT_EXECUTIVE_SUMMARY.md`
- `docs/REINVENT_IMPLEMENTATION_GUIDE.md`

---

### Consolidate Educational Docs (Priority 2)

**Create:** `docs/reference/EDUCATIONAL_STRATEGY.md`

**Structure:**
```markdown
# Educational Strategy - Making Cloud Security Accessible

## Current State Analysis
[Content from EDUCATIONAL_ANALYSIS_SUMMARY.md]

## Enhancement Recommendations
[Content from EDUCATIONAL_ENHANCEMENT_RECOMMENDATIONS.md]

## Implementation Roadmap
[Combined from both files]
```

**Delete:**
- `docs/EDUCATIONAL_ANALYSIS_SUMMARY.md`
- `docs/EDUCATIONAL_ENHANCEMENT_RECOMMENDATIONS.md`

---

### Move Files (Priority 3)

**Execute:**
```bash
# Move arcade mode guide
mv docs/ARCADE_MODE.md docs/guides/ARCADE_MODE.md

# Move JIT quest plan
mv docs/jit-quest-api-plan.md docs/sonrai-api/jit-quest-plan.md

# Move service protection quest
mv docs/service-protection-quest-summary.md docs/reference/SERVICE_PROTECTION_QUEST.md
```

**Update links in:**
- `docs/README.md` (documentation hub)
- Root `README.md` (if referenced)

---

### Delete Obsolete Files (Priority 4)

**Delete:**
```bash
# Outdated troubleshooting
rm docs/mcp_diagnosis_for_sonrai.md

# Duplicates .kiro/steering/documentation-agent.md
rm docs/DOCUMENTATION_STANDARDS.md
```

---

## ✅ Verification Checklist

After cleanup:
- [ ] All links in `docs/README.md` work
- [ ] All links in root `README.md` work
- [ ] No broken references in other docs
- [ ] All valuable content preserved
- [ ] Clear organization (guides/, reference/, sonrai-api/)
- [ ] Root docs/ has only core files
- [ ] Git commit with clear message

---

## 📝 Commit Message

```
docs: consolidate and reorganize documentation structure [with Kiro]

Kiro analyzed 16 root-level docs files and consolidated them into
a clearer structure with no redundancy.

Changes:
- Consolidated 3 re:Invent docs into 1 comprehensive guide
- Merged 2 educational docs into reference/EDUCATIONAL_STRATEGY.md
- Moved ARCADE_MODE.md to guides/
- Moved jit-quest-api-plan.md to sonrai-api/
- Moved service-protection-quest-summary.md to reference/
- Deleted mcp_diagnosis_for_sonrai.md (outdated)
- Deleted DOCUMENTATION_STANDARDS.md (duplicates steering file)

Impact:
- Root docs/ reduced from 16 to 7 files (56% reduction)
- No duplicate/conflicting information
- Clearer organization for contributors and judges
- All valuable content preserved

Co-authored-by: Kiro AI <kiro@kiro.ai>
```

---

## 🎯 Priority for Kiroween

**Do Now (Before Video):**
- ✅ Consolidate re:Invent docs (judges might look at these)
- ✅ Delete obsolete files (reduce noise)

**Do Later (After Submission):**
- ⏰ Move files to appropriate folders
- ⏰ Consolidate educational docs

**Reason:** Focus on video/screenshots first. Clean docs are nice but not critical for winning.

---

*This cleanup makes the documentation more professional and easier to navigate for Kiroween judges.*
