# Quick Start Guide

Get Sonrai Zombie Blaster running in under 2 minutes.

## Prerequisites

- Python 3.11 or higher ([download](https://www.python.org/downloads/))
- Sonrai Security account with API access
- 4 GB RAM minimum

## Installation

### 1. Clone Repository

```bash
git clone <repository-url>
cd zombie_game
```

### 2. Create Virtual Environment

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

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Sonrai API

```bash
cp .env.example .env
nano .env  # or your preferred editor
```

Add your Sonrai credentials:
```env
SONRAI_API_URL=https://YOUR_ORG-graphql-server.sonraisecurity.com/graphql
SONRAI_ORG_ID=your_org_id_here
SONRAI_API_TOKEN=your_api_token_here
```

**Where to find credentials:**
1. Log into Sonrai Security
2. Go to Settings → API Tokens
3. Create token with `read:data` and `read:platform` scopes

### 5. Run the Game

```bash
python3 src/main.py
```

## Controls

**Lobby (Top-Down):**
- Arrow Keys / WASD - Move
- Space - Fire
- Walk into doors - Enter levels

**Platformer (Side-Scrolling):**
- Left/Right (← → / A/D) - Move
- Up / W - Jump
- Space - Fire

**Universal:**
- F11 / F / CMD+F - Toggle fullscreen
- ESC - Pause
- Enter - Dismiss messages

## Troubleshooting

### "SONRAI_API_TOKEN is required"
- Verify `.env` file exists
- Check credentials are correct
- No spaces around `=` signs

### "Failed to authenticate"
- Confirm API token is valid
- Verify organization ID
- Test in Sonrai GraphQL explorer

### "ModuleNotFoundError: pygame"
- Activate virtual environment
- Reinstall: `pip install -r requirements.txt`

### No zombies found
- Verify AWS account has unused identities
- Check account filter in `.env`

## Next Steps

- Read [Game Mechanics](../reference/MECHANICS.md)
- Check [Cheat Codes](../CHEAT_CODES.md) for testing
- Explore [Architecture](../architecture/ARCHITECTURE.md)

## Support

- [Troubleshooting Guide](../reference/TROUBLESHOOTING.md)
- [GitHub Issues](../../issues)
- [Discussions](../../discussions)
