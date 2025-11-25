# JIT Access Quest - Testing Guide

## Quick Test Instructions

### Step 1: Launch the Game
```bash
python3 src/main.py
```

### Step 2: Unlock All Levels (Cheat Code)
In the lobby, press these keys in sequence:
```
U → N → L → O → C → K
```

You should see: **"🔓 CHEAT ACTIVATED - All Levels Unlocked!"**

Press ESC to dismiss the message.

### Step 3: Enter a Production Account

Navigate to one of these doors and press UP to enter:
- **Production Data** (160224865296)
- **Production** (613056517323)  
- **Org** (437154727976)

### Step 4: Test the JIT Quest

Once in the level, you should see:

**Entities:**
- ✅ **Auditor** - Gray suited character with clipboard, patrolling back and forth
- ✅ **Admin Roles** - Characters with **gold crowns** on their heads
  - Green body = Already has JIT protection (purple shield visible)
  - Gold/yellow body = Needs JIT protection

**Quest Interaction:**
1. Walk your player character into an **unprotected admin role** (gold/yellow with crown)
2. The game will call the Sonrai API to apply JIT protection
3. You should see:
   - ✅ Success message: "JIT Protection Applied! [RoleName] now requires Just-In-Time approval"
   - Role turns green
   - Purple Sonrai shield appears on the role
   - Progress counter updates (e.g., "2/3 roles protected")

**Quest Completion:**
- Protect all admin roles → **"🎉 Audit Deficiency Prevented!"** message
- Leave level without protecting all → **"⚠️ Audit Failed!"** message

### Step 5: Verify API Integration

Check the console logs for:
```
🔍 Checking for admin/privileged permission sets in account [ID]...
✅ Creating JIT Access Quest with X permission sets (Y unprotected)
✅ JIT applied to [PermissionSetName]
```

## Expected Behavior

### Quest Appears When:
- ✅ Account is production (160224865296, 613056517323, or 437154727976)
- ✅ Account has admin/privileged permission sets
- ✅ At least one permission set does NOT have JIT protection

### Quest Does NOT Appear When:
- ⏭️ Account is not production (Sandbox, Stage, etc.)
- ⏭️ No admin/privileged permission sets exist
- ⏭️ All permission sets already have JIT protection

## Troubleshooting

### No Quest Appears
1. Check console logs for: `⏭️ Account [ID] is not a production account`
2. Verify you're in Production Data, Production, or Org account
3. Check if all roles already have JIT: `⏭️ All admin/privileged roles already have JIT`

### API Errors
1. Check `.env` file has valid Sonrai credentials
2. Look for error messages in console
3. Verify network connectivity to Sonrai API

### Visual Issues
- Auditor should have gray suit and clipboard
- Admin roles should have gold crowns
- Protected roles should show purple pulsing shields
- Permission set names should appear above characters

## Cheat Codes Reference

- **UNLOCK** (U-N-L-O-C-K) - Unlock all levels
- **SKIP** (S-K-I-P) - Skip current level and return to lobby

## Production Account IDs

For reference:
- **160224865296** - MyHealth - Production Data
- **613056517323** - MyHealth - Production
- **437154727976** - Sonrai MyHealth - Org

## Success Criteria

✅ Quest initializes in production accounts  
✅ Auditor patrols the level  
✅ Admin roles display with crowns  
✅ Player can interact with unprotected roles  
✅ API call applies JIT protection  
✅ Visual feedback (green color, purple shield)  
✅ Success message when all protected  
✅ Failure message when leaving early  
✅ Quest resets when returning to lobby  

---

**Ready to test!** Launch the game and use the UNLOCK cheat to access production accounts.
