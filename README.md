# Sonrai Zombie Blaster

A retro-style video game that visualizes and gamifies the process of identifying and remediating unused AWS identities through the Sonrai API. Blast zombies representing real unused identities and watch your cloud security posture improve!

## Features

- 🎮 Simple retro graphics inspired by Chrome's offline dinosaur game
- 🔫 Mega Man-style character with ray gun
- 🧟 Each zombie represents a real unused AWS identity from Sonrai
- 🔒 Eliminating zombies triggers real quarantine actions via Sonrai API
- 📊 Real-time progress tracking
- 🎯 Single looping level - eliminate all 1000 zombies!
- 💬 Retro Game Boy-style congratulations messages

## Requirements

- Python 3.11 or higher
- Sonrai Security API credentials
- Pygame 2.5+

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd sonrai-zombie-blaster
```

2. Create a virtual environment:
```bash
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure your Sonrai API credentials:
```bash
cp .env.example .env
# Edit .env and add your Sonrai API credentials
```

## Configuration

Edit the `.env` file with your Sonrai API credentials:

```
SONRAI_API_URL=https://api.sonraisecurity.com
SONRAI_API_KEY=your_api_key_here
SONRAI_API_SECRET=your_api_secret_here
GAME_WIDTH=800
GAME_HEIGHT=600
TARGET_FPS=60
```

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
2. Each zombie in the game represents one unused identity (test-user-1 through test-user-500)
3. When you eliminate a zombie, the game sends a quarantine request to Sonrai
4. Successfully quarantined identities are permanently removed from the game
5. Your goal: eliminate all zombies and improve your cloud security!

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
