# Sonrai Zombie Blaster

A retro-style video game that visualizes and gamifies the process of identifying and remediating unused AWS identities through the Sonrai API. Blast zombies representing real unused identities and watch your cloud security posture improve!

## Features

- 🎮 Simple retro graphics inspired by Chrome's offline dinosaur game
- 🔫 Mega Man-style character with ray gun
- 🧟 Each zombie represents a real unused AWS identity from Sonrai
- 🔒 Eliminating zombies triggers real quarantine actions via Sonrai API
- 💜 Protected entities with purple shields (Sonrai + exempted identities)
- 💥 Damage system with health points (zombies: 3 HP, third parties: 10 HP)
- 📈 Score tracking with damage multiplier (increases every 10 eliminations)
- 📊 Real-time progress tracking and statistics
- 🎯 Third-party access visualization and blocking
- 💬 Retro Game Boy-style congratulations messages

## Screenshots

*Coming soon! Screenshots of gameplay, protected entities with purple shields, damage system, and more.*

<!-- Placeholder for screenshots - to be added -->
<!--
![Main Gameplay](assets/screenshots/gameplay.png)
*Main gameplay showing player shooting zombies with UI elements*

![Congratulations Message](assets/screenshots/congratulations.png)
*Retro Game Boy-style congratulations message when eliminating a zombie*

![Protected Entities](assets/screenshots/protected_entities.png)
*Purple shields indicating protected Sonrai and exempted entities*

![Damage System](assets/screenshots/damage_system.png)
*Health bars and damage numbers in action*
-->

## Requirements

### System Requirements
- **OS**: macOS, Linux, or Windows
- **Python**: 3.11 or higher
- **Display**: 800x600 minimum resolution

### Sonrai Requirements
- Active Sonrai Security account
- API access token (see Configuration section)
- Organization ID
- GraphQL API URL

### Python Dependencies
- pygame 2.5+
- python-dotenv
- requests

## Installation Runbook

Follow these steps to set up the game on your machine:

### Step 1: Extract the Project

If you received a zip file:
```bash
unzip zombie_game.zip
cd zombie_game
```

If you're cloning from git:
```bash
git clone <repository-url>
cd zombie_game
```

### Step 2: Verify Python Version

Check that you have Python 3.11 or higher:
```bash
python3 --version
```

If you need to install Python 3.11+:
- **macOS**: `brew install python@3.11`
- **Linux**: `sudo apt install python3.11` (or use your package manager)
- **Windows**: Download from [python.org](https://www.python.org/downloads/)

### Step 3: Create Virtual Environment

Create and activate a Python virtual environment:

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

### Step 4: Install Dependencies

Install all required Python packages:
```bash
pip install -r requirements.txt
```

### Step 5: Configure Sonrai API Credentials

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Get your Sonrai API credentials:
   - Log into your Sonrai Security account
   - Navigate to **Settings** → **API Tokens**
   - Create a new API token with `read:data` and `read:platform` scopes
   - Copy your token, org ID, and GraphQL URL

3. Edit `.env` with your credentials:
```bash
# Open in your preferred editor
nano .env
# or
vim .env
# or
code .env  # VS Code
```

4. Update these values:
```
SONRAI_API_URL=https://YOUR_ORG-graphql-server.sonraisecurity.com/graphql
SONRAI_ORG_ID=your_org_id_here
SONRAI_API_TOKEN=your_api_token_here
```

**Note**: Keep your `.env` file private! It contains sensitive credentials.

### Step 6: Verify Installation

Test that everything is set up correctly:
```bash
python3 src/main.py
```

If successful, you should see the game window open!

## Configuration

The `.env` file controls both API access and game settings:

```env
# Sonrai API Configuration (REQUIRED)
SONRAI_API_URL=https://YOUR_ORG-graphql-server.sonraisecurity.com/graphql
SONRAI_ORG_ID=your_org_id_here
SONRAI_API_TOKEN=your_api_token_here

# Game Configuration (OPTIONAL - defaults shown)
GAME_WIDTH=800
GAME_HEIGHT=600
TARGET_FPS=60
```

## Troubleshooting

### "SONRAI_API_TOKEN is required in .env file"
- Make sure you copied `.env.example` to `.env`
- Verify your `.env` file has valid credentials
- Check that there are no extra spaces around the `=` signs

### "Failed to authenticate with Sonrai API"
- Verify your API token is still valid (check expiration date)
- Confirm your organization ID is correct
- Test your token using the Sonrai GraphQL explorer

### "ModuleNotFoundError: No module named 'pygame'"
- Make sure your virtual environment is activated (`source venv/bin/activate`)
- Re-run `pip install -r requirements.txt`

### Game window doesn't open / black screen
- Check that your display resolution is at least 800x600
- Try updating pygame: `pip install --upgrade pygame`
- On Linux, you may need to install SDL libraries: `sudo apt install libsdl2-dev`

### "No zombies found" / Empty game
- Verify your AWS account has unused identities
- Check the `AWS_ACCOUNT` filter in your `.env` file
- Try adjusting `DAYS_SINCE_LAST_LOGIN` in `.env`

## Usage

Run the game:
```bash
python src/main.py
```

## Controls

- **Arrow Keys (← →) or A/D**: Move left/right
- **Space**: Fire ray gun
- **Enter**: Dismiss congratulations message and continue
- **ESC**: Quit game

The player character will automatically stop when you release the movement keys.

## How It Works

1. The game fetches unused AWS identities from your Sonrai account
2. Each zombie in the game represents one unused identity
3. When you eliminate a zombie (3 hits), the game sends a quarantine request to Sonrai
4. Successfully quarantined identities are permanently removed from the game
5. Third-party entities patrol the map and can be blocked (10 hits)
6. Protected entities (exemptions + Sonrai) display purple shields and are invulnerable
7. Your goal: eliminate all zombies and improve your cloud security!

## Sonrai API Integration

This game integrates with the Sonrai Security platform using GraphQL queries and mutations.

**Full API Documentation**: [docs/sonrai-api/README.md](docs/sonrai-api/README.md)

Quick links:
- [Unused Identities Query](docs/sonrai-api/queries/unused-identities.md) - Fetch zombies
- [Quarantine Mutation](docs/sonrai-api/queries/quarantine-identity.md) - Eliminate zombies
- [Third Party Query](docs/sonrai-api/queries/third-party-access.md) - Fetch 3rd parties
- [Exemptions Query](docs/sonrai-api/queries/exempted-identities.md) - Protected entities
- [Quick Reference](docs/sonrai-api/QUICK_REFERENCE.md) - All API calls at a glance

See [Integration Guide](docs/sonrai-api/INTEGRATION_GUIDE.md) for detailed integration information.

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run property-based tests only
pytest -k property
```

### Project Structure

```
sonrai-zombie-blaster/
├── src/
│   ├── main.py              # Entry point
│   ├── game_engine.py       # Core game loop
│   ├── sonrai_client.py     # API integration
│   ├── renderer.py          # Graphics rendering
│   ├── models.py            # Data models
│   ├── player.py            # Player character
│   ├── zombie.py            # Zombie entities
│   ├── projectile.py        # Projectiles
│   └── collision.py         # Collision detection
├── tests/                   # Test files
├── .env                     # Configuration (not in git)
├── .env.example             # Example configuration
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## License

[Your License Here]

## Credits

Built with Python and Pygame. Integrates with Sonrai Security's Cloud Permissions Firewall.
