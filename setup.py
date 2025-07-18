#!/usr/bin/env python3
"""
Setup script for Rental Listings Platform
"""

import subprocess
import sys
import os

def install_dependencies():
    """Install required Python packages"""
    print("📦 Installing Python dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ required. Current version: {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor} detected")
    return True

def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")
    directories = ['logs', 'data']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    print("✅ Directories created")

def run_application():
    """Run the Flask application"""
    print("🚀 Starting Rental Listings Platform...")
    print("📍 Server will be available at: http://localhost:5000")
    print("🛑 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        subprocess.run([sys.executable, "app.py"])
    except KeyboardInterrupt:
        print("\n👋 Stopping server...")
    except Exception as e:
        print(f"❌ Error running application: {e}")

def main():
    """Main setup function"""
    print("=" * 50)
    print("🏠 Rental Listings Platform Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Run: python app.py")
    print("2. Open: http://localhost:5000")
    print("3. Start scraping rental listings!")
    
    # Ask if user wants to run the app now
    response = input("\n❓ Would you like to start the application now? (y/n): ").lower().strip()
    if response in ['y', 'yes']:
        run_application()

if __name__ == "__main__":
    main()