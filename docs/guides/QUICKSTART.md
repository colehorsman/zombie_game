# 🎮 60-Second Quickstart

Get the game running in under 2 minutes!

## Prerequisites

- **Python 3.11+** ([download here](https://www.python.org/downloads/))
- **Sonrai Security account** with API access

## Setup Steps

### 1. Clone the Repository (10 sec)

```bash
git clone <repository-url>
cd zombie_game
```

**Branch selection:**
- `v2` - Hybrid mode (lobby + platformer) - **RECOMMENDED**
- `v1` - Original top-down lobby only
- `levels` - Platformer-only mode

```bash
# Switch to your preferred branch (optional)
git checkout v2
```

### 2. Create Virtual Environment (15 sec)

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

You should see `(venv)` in your terminal prompt.

### 3. Install Dependencies (30 sec)

```bash
pip install -r requirements.txt
```

### 4. Configure Sonrai API Credentials (30 sec)

```bash
# Copy the example config
cp .env.example .env

# Edit with your credentials
nano .env  # or vim, code, etc.
```

**Update these values in `.env`:**
```env
SONRAI_API_URL=https://YOUR_ORG-graphql-server.sonraisecurity.com/graphql
SONRAI_ORG_ID=your_org_id_here
SONRAI_API_TOKEN=your_api_token_here
```

**Where to find your credentials:**
1. Log into Sonrai Security
2. Go to **Settings** → **API Tokens**
3. Create token with `read:data` and `read:platform` scopes
4. Copy your token, org ID, and GraphQL URL

### 5. Run the Game! (immediate)

```bash
python3 src/main.py
```

**Optional:** Start in fullscreen mode:
```bash
# In .env, set:
FULLSCREEN=true
```

## Controls

### Lobby Mode (Top-Down)
- **Arrow Keys / WASD** - Move in 8 directions
- **Space** - Fire ray gun
- **Walk into doors** - Enter account levels

### Platformer Mode (Side-Scrolling)
- **Arrow Keys (← →) / A/D** - Move left/right
- **Up Arrow / W** - Jump
- **Space** - Fire ray gun

### Universal
- **F11 / F / CMD+F** - Toggle fullscreen
- **ESC** - Pause/Save/Quit
- **Enter** - Dismiss messages

### 🎮 Controller Support
- Works with Bluetooth and wired controllers (8BitDo tested)
- **A button** - Fire
- **B button** - Jump (platformer only)
- **D-pad/Stick** - Movement
- **Start** - Pause

## Features

✅ **Fullscreen support** with aspect ratio preservation
✅ **Controller support** (Bluetooth/wired)
✅ **Auto-save** - Progress preserved on exit
✅ **Multiple gameplay modes** - Lobby, platformer, boss battles
✅ **Real Sonrai API integration** - Quarantine unused identities

## Troubleshooting

### "SONRAI_API_TOKEN is required"
- Make sure you copied `.env.example` to `.env`
- Verify your `.env` file has valid credentials
- No spaces around `=` signs

### "Failed to authenticate"
- Check your API token is still valid
- Confirm your organization ID is correct
- Test in Sonrai GraphQL explorer first

### "ModuleNotFoundError: No module named 'pygame'"
- Activate virtual environment: `source venv/bin/activate`
- Reinstall: `pip install -r requirements.txt`

### Game window issues
- Update pygame: `pip install --upgrade pygame`
- Linux: Install SDL2: `sudo apt install libsdl2-dev`

### No zombies found
- Verify your AWS account has unused identities
- Check `AWS_ACCOUNT` filter in `.env`
- Adjust `DAYS_SINCE_LAST_LOGIN` in `.env`

## Next Steps

- Read [README.md](README.md) for detailed documentation
- Check [CHEAT_CODES.md](CHEAT_CODES.md) for testing shortcuts
- See [docs/sonrai-api/](docs/sonrai-api/) for API integration details

**Total setup time: ~1-2 minutes** ⚡

Need help? [Open an issue](../../issues) or check the full README.
