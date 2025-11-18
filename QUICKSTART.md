# Quick Start Guide

## Installation

1. **Install Python 3.11+**
   ```bash
   python3 --version  # Should be 3.11 or higher
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify installation**
   ```bash
   python test_setup.py
   ```

## Configuration

1. **Copy the example environment file**
   ```bash
   cp .env.example .env
   ```

2. **Edit .env with your Sonrai API credentials**
   ```bash
   # Open .env in your editor and add:
   SONRAI_API_URL=https://api.sonraisecurity.com
   SONRAI_API_KEY=your_actual_api_key
   SONRAI_API_SECRET=your_actual_api_secret
   ```

## Running the Game

```bash
python src/main.py
```

## Game Controls

- **← → or A/D**: Move left/right
- **Space**: Fire ray gun
- **Enter**: Dismiss congratulations message
- **ESC**: Quit

## Gameplay

1. The game fetches unused AWS identities from your Sonrai account
2. Each zombie represents one unused identity (test-user-1 through test-user-500)
3. Shoot zombies to eliminate them
4. When you hit a zombie, the game pauses and shows a congratulations message
5. Press ENTER to quarantine the identity via the Sonrai API
6. Continue until all zombies are eliminated!

## Troubleshooting

### "Configuration Error"
- Make sure you've created a .env file with your API credentials
- Check that all three variables are set: SONRAI_API_URL, SONRAI_API_KEY, SONRAI_API_SECRET

### "API Connection Error"
- Verify your API credentials are correct
- Check your network connection
- Ensure the Sonrai API URL is correct

### "Pygame Initialization Error"
- Update your graphics drivers
- Try reinstalling pygame: `pip install --upgrade pygame`

### Game runs slowly
- The game is designed to handle 1000 zombies efficiently
- If performance is poor, check your system resources
- The spatial grid collision detection should keep it smooth

## Development

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_collision.py
```

### Project Structure
```
src/
├── main.py           # Entry point
├── game_engine.py    # Core game loop
├── sonrai_client.py  # API integration
├── renderer.py       # Graphics
├── models.py         # Data models
├── player.py         # Player character
├── zombie.py         # Zombie entities
├── projectile.py     # Projectiles
└── collision.py      # Collision detection
```

## Next Steps

- The core game is fully functional
- Optional: Add property-based tests (marked with * in tasks.md)
- Optional: Add unit tests for edge cases
- Optional: Enhance graphics or add sound effects
- Optional: Add more game features (power-ups, different zombie types, etc.)

Enjoy blasting those zombies and securing your cloud! 🎮🔒
