# Quick Fix: Unable to Login After Deployment

## Problem
You see: **"Please enter a correct username and password"**

This happens because:
- Deployment created a fresh database with users
- But password in `create_division_users.py` was incorrect
- Old deployed apps have users with wrong passwords

## Solution: Trigger Manual Redeploy (FREE TIER COMPATIBLE)

### Step 1: Go to Render Dashboard
https://dashboard.render.com

### Step 2: Click on `nwo-portal` service

### Step 3: Click **"Manual Deploy"**

### Step 4: Select **"Deploy latest commit"** and click Deploy

This will:
1. Pull the latest code (with password fixes)
2. Run migrations
3. Run `create_division_users` (creates new users with correct passwords)
4. Run `fix_user_passwords` (fixes ALL existing users to correct passwords)
5. Start the app

### Step 5: Wait for deployment to complete
Watch the logs. You should see:
```
[timestamp] Running Django migrations
[timestamp] Migrations completed successfully
[timestamp] Creating default division users
[timestamp] Default division users created successfully
[timestamp] Fixing user passwords to match deployment defaults...
[timestamp] User passwords fixed successfully
```

### Step 6: Try Logging In
Use these credentials:

| Division | Username | Password |
|----------|----------|----------|
| NWO CENTRAL | nwo_central | Nwo@Central@2026! |
| NWO PALARIVATTOM | nwo_palarivattom | Nwo@Palarivattom@2026! |
| **NWO KOCHI** | **nwo_kochi** | **Nwo@Kochi2026!** (NO @ between Kochi and 2026) |
| NWO TRIPUNITHARA | nwo_tripunithara | Nwo@Tripunithura@2026! |
| NWO ANGAMALY | nwo_angamaly | Nwo@Angamaly@2026! |
| NWO THODUPUZHA | nwo_thodupuzha | Nwo@Thodupuzha@2026! |
| NWO ALUVA | nwo_aluva | Nwo@Aluva@2026! |
| NWO MOOVATTUPUZHA | nwo_moovattupuzha | Nwo@Moovattupuzha@2026! |
| NWO ADIMALY | nwo_adimaly | Nwo@Adimaly@2026! |
| NWO KATTAPPANA | nwo_kattappana | Nwo@Kattappana@2026! |

---

## What Was Fixed

**Code Changes Made:**
1. ✅ Fixed password in `inventory/management/commands/create_division_users.py`
   - NWO KOCHI: `Nwo@Kochi@2026!` → `Nwo@Kochi2026!`

2. ✅ Created `inventory/management/commands/fix_user_passwords.py`
   - Automatically fixes all user passwords on deployment

3. ✅ Updated `start.sh`
   - Now runs password fix during every deployment

---

## Still Having Issues?

**If login still fails after manual deploy:**

1. **Check the logs** in Render dashboard - look for errors
2. **Wait 30 seconds** - sometimes it takes a moment
3. **Try a different division** account (e.g., `nwo_central`)
4. **Refresh browser** (Ctrl+Shift+R)

---

## For Developers

To prevent this in the future:
- Passwords are now synced across:
  - `create_division_users.py` - Creates users
  - `views.py` - Default password function
  - `fix_user_passwords.py` - Fixes mismatches
- They all use the same password values
