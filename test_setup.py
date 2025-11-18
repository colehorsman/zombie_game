#!/usr/bin/env python3
"""Quick test to verify the game setup is correct."""

import sys

def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")
    
    try:
        import pygame
        print("✓ pygame")
    except ImportError:
        print("✗ pygame - run: pip install pygame")
        return False
    
    try:
        import requests
        print("✓ requests")
    except ImportError:
        print("✗ requests - run: pip install requests")
        return False
    
    try:
        from dotenv import load_dotenv
        print("✓ python-dotenv")
    except ImportError:
        print("✗ python-dotenv - run: pip install python-dotenv")
        return False
    
    try:
        import pytest
        print("✓ pytest")
    except ImportError:
        print("✗ pytest - run: pip install pytest")
        return False
    
    try:
        import hypothesis
        print("✓ hypothesis")
    except ImportError:
        print("✗ hypothesis - run: pip install hypothesis")
        return False
    
    return True

def test_src_modules():
    """Test that game modules can be imported."""
    print("\nTesting game modules...")
    
    try:
        sys.path.insert(0, 'src')
        
        import models
        print("✓ models")
        
        import sonrai_client
        print("✓ sonrai_client")
        
        import player
        print("✓ player")
        
        import zombie
        print("✓ zombie")
        
        import projectile
        print("✓ projectile")
        
        import collision
        print("✓ collision")
        
        import renderer
        print("✓ renderer")
        
        import game_engine
        print("✓ game_engine")
        
        import main
        print("✓ main")
        
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 50)
    print("Sonrai Zombie Blaster - Setup Test")
    print("=" * 50)
    
    if not test_imports():
        print("\n❌ Some dependencies are missing. Please run:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    
    if not test_src_modules():
        print("\n❌ Some game modules failed to import.")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("✅ All tests passed! Setup is correct.")
    print("=" * 50)
    print("\nNext steps:")
    print("1. Copy .env.example to .env")
    print("2. Add your Sonrai API credentials to .env")
    print("3. Run: python src/main.py")

if __name__ == "__main__":
    main()
