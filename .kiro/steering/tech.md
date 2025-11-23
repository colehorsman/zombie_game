# Technology Stack

## Core Technologies

- **Language**: Python 3.11+
- **Game Engine**: Pygame 2.5+
- **API Integration**: Sonrai Security GraphQL API

## Dependencies

```
pygame>=2.5.0          # Game engine and rendering
requests>=2.31.0       # HTTP client for API calls
python-dotenv>=1.0.0   # Environment variable management
pytest>=7.4.0          # Testing framework
hypothesis>=6.0.0      # Property-based testing
```

## Configuration

Environment variables are managed via `.env` file:
- `SONRAI_API_URL` - Sonrai GraphQL endpoint (required)
- `SONRAI_ORG_ID` - Organization ID (required)
- `SONRAI_API_TOKEN` - API authentication token (required)
- `GAME_WIDTH` - Base rendering resolution width (default: 1280)
- `GAME_HEIGHT` - Base rendering resolution height (default: 720)
- `FULLSCREEN` - Fullscreen mode toggle (default: false)
- `TARGET_FPS` - Target frame rate (default: 60)
- `MAX_ZOMBIES` - Maximum zombies to load (default: 1000)

## Common Commands

### Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Sonrai credentials
```

### Running
```bash
# Start the game
python src/main.py

# Run with specific Python version
python3 src/main.py
```

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run property-based tests only
pytest -k property
```

### Development
```bash
# Controller testing
python test_controller.py
python quick_controller_test.py
python verify_dpad.py

# D-pad specific testing
python dpad_test.py
```

## Platform Support

- **macOS**: Primary development platform
- **Linux**: Supported (may require SDL libraries: `sudo apt install libsdl2-dev`)
- **Windows**: Supported
