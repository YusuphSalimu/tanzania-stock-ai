#!/usr/bin/env python3
"""
Tanzania Stock Market AI - Quick Start Script
Run this script to start the application
"""

import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    return True

def check_dependencies():
    """Check if required dependencies are installed"""
    print("📦 Checking dependencies...")
    
    required_packages = [
        'flask', 'pandas', 'numpy', 'scikit-learn',
        'tensorflow', 'xgboost', 'requests', 'beautifulsoup4'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("💡 Run: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies are installed")
    return True

def initialize_data():
    """Initialize the dataset"""
    print("📊 Initializing dataset...")
    
    try:
        from utils.data_loader import DSEDataLoader
        loader = DSEDataLoader()
        df = loader.load_data()
        
        if df.empty:
            print("🔄 Creating sample dataset...")
            df = loader.create_sample_dataset()
        
        print(f"✅ Dataset ready: {len(df)} records")
        return True
    except Exception as e:
        print(f"❌ Data initialization failed: {e}")
        return False

def start_backend():
    """Start the Flask backend"""
    print("🚀 Starting Flask backend...")
    
    try:
        # Import Flask app
        from backend.app import app
        
        # Start Flask in a separate process
        import threading
        
        def run_flask():
            app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)
        
        flask_thread = threading.Thread(target=run_flask, daemon=True)
        flask_thread.start()
        
        # Wait for Flask to start
        time.sleep(3)
        
        print("✅ Backend started on http://localhost:5000")
        return True
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return False

def open_frontend():
    """Open the frontend in browser"""
    print("🌐 Opening frontend...")
    
    frontend_path = Path(__file__).parent / "frontend" / "index.html"
    
    if frontend_path.exists():
        file_url = f"file:///{frontend_path.absolute()}"
        webbrowser.open(file_url)
        print(f"✅ Frontend opened: {file_url}")
        return True
    else:
        print("❌ Frontend file not found")
        return False

def show_instructions():
    """Show usage instructions"""
    print("\n" + "="*60)
    print("🇹🇿 TANZANIA STOCK MARKET AI - INSTRUCTIONS")
    print("="*60)
    print("\n📱 Frontend: http://localhost:5000 (or opened in browser)")
    print("🔧 Backend API: http://localhost:5000/api")
    print("\n📊 Available Endpoints:")
    print("  • GET /api/stocks - List all stocks")
    print("  • GET /api/stocks/{symbol}/data - Stock data")
    print("  • GET /api/stocks/{symbol}/predict - AI prediction")
    print("  • GET /api/market/summary - Market overview")
    print("\n💡 Tips:")
    print("  • Start with CRDB, NMB, or TBL for testing")
    print("  • Allow models to train for better accuracy")
    print("  • Check the Jupyter notebook for analysis")
    print("\n🛑 Press Ctrl+C to stop the server")
    print("="*60)

def main():
    """Main function"""
    print("🇹🇿 Tanzania Stock Market AI - Quick Start")
    print("="*50)
    
    # Check Python version
    if not check_python_version():
        return 1
    
    # Check dependencies
    if not check_dependencies():
        return 1
    
    # Initialize data
    if not initialize_data():
        return 1
    
    # Start backend
    if not start_backend():
        return 1
    
    # Open frontend
    open_frontend()
    
    # Show instructions
    show_instructions()
    
    try:
        # Keep the script running
        print("\n⏳ Server is running... Press Ctrl+C to stop")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Server stopped. Goodbye!")
        return 0

if __name__ == "__main__":
    sys.exit(main())
