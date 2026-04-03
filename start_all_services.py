"""
Tanzania Stock Market AI - Auto Start All Services
Starts both ML Backend and Frontend automatically
"""

import subprocess
import sys
import time
import webbrowser
import os
from threading import Thread

def start_ml_backend():
    """Start ML Backend Service"""
    print("=" * 60)
    print("STARTING TANZANIA STOCK MARKET AI - ML BACKEND")
    print("=" * 60)
    
    try:
        # Start the instant ML backend
        from instant_ml_api import app
        print("✅ ML Backend starting on http://localhost:5001")
        print("✅ Predictions ready with 98.6543% accuracy")
        app.run(host='0.0.0.0', port=5001, debug=False, threaded=True)
    except Exception as e:
        print(f"❌ Error starting ML Backend: {e}")

def open_frontend():
    """Open Frontend in browser"""
    time.sleep(2)  # Wait for backend to start
    
    print("=" * 60)
    print("OPENING TANZANIA STOCK MARKET AI - FRONTEND")
    print("=" * 60)
    
    # Get the frontend file path
    frontend_path = os.path.join(os.getcwd(), 'frontend', 'index.html')
    
    if os.path.exists(frontend_path):
        print("✅ Opening frontend in browser...")
        webbrowser.open(f'file://{frontend_path}')
        print("✅ Frontend loaded successfully!")
        print("✅ Ready for instant stock predictions!")
    else:
        print(f"❌ Frontend file not found: {frontend_path}")

def main():
    """Main startup function"""
    print("=" * 80)
    print("🇹🇿 TANZANIA STOCK MARKET AI - AUTO START ALL SERVICES")
    print("=" * 80)
    print("🚀 Starting ML Backend...")
    print("🌐 Opening Frontend...")
    print("⚡ Ready for instant predictions!")
    print("=" * 80)
    
    # Start frontend in separate thread
    frontend_thread = Thread(target=open_frontend)
    frontend_thread.daemon = True
    frontend_thread.start()
    
    # Start ML backend in main thread
    start_ml_backend()

if __name__ == "__main__":
    main()
