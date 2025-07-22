#!/usr/bin/env python3
"""
OCR Receipt Processor System Startup Script
This script starts both the FastAPI backend and Streamlit dashboard
"""

import os
import sys
import time
import subprocess
import signal
import psutil
import requests
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.core.config import settings

def kill_processes():
    """Kill any existing OCR processes."""
    print("🔄 Killing existing processes...")
    
    # Kill processes by name
    processes_to_kill = [
        "python ocr_upload.py",
        "streamlit run ocr_dashboard.py",
        "uvicorn",
        "streamlit"
    ]
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
            for target in processes_to_kill:
                if target in cmdline:
                    print(f"🔄 Killing process {proc.info['pid']}: {cmdline}")
                    proc.terminate()
                    proc.wait(timeout=5)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
            pass
    
    # Kill processes on specific ports
    for port in [settings.API_PORT, settings.DASHBOARD_PORT]:
        try:
            subprocess.run(f"lsof -ti:{port} | xargs kill -9", shell=True, capture_output=True)
        except:
            pass
    
    time.sleep(2)
    print("✅ Processes killed")

def check_port(port):
    """Check if port is available."""
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        return result == 0
    except:
        return False

def start_backend():
    """Start the FastAPI backend."""
    print("🚀 Starting FastAPI backend...")
    
    if check_port(settings.API_PORT):
        print(f"❌ Port {settings.API_PORT} is already in use")
        return False
    
    try:
        # Start backend in background
        backend_process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "app.api.main:app", 
             "--host", settings.API_HOST, "--port", str(settings.API_PORT)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for backend to start
        time.sleep(5)
        
        if backend_process.poll() is None:
            print(f"✅ Backend started successfully on http://{settings.API_HOST}:{settings.API_PORT}")
            return True
        else:
            print("❌ Backend failed to start")
            return False
            
    except Exception as e:
        print(f"❌ Error starting backend: {e}")
        return False

def start_dashboard():
    """Start the Streamlit dashboard."""
    print("🚀 Starting Streamlit dashboard...")
    
    if check_port(settings.DASHBOARD_PORT):
        print(f"❌ Port {settings.DASHBOARD_PORT} is already in use")
        return False
    
    try:
        # Start Streamlit in background
        dashboard_process = subprocess.Popen(
            [sys.executable, "-m", "streamlit", "run", "app/dashboard/main.py", 
             "--server.port", str(settings.DASHBOARD_PORT), "--server.headless", "true"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for dashboard to start
        time.sleep(8)
        
        if dashboard_process.poll() is None:
            print(f"✅ Dashboard started successfully on http://{settings.DASHBOARD_HOST}:{settings.DASHBOARD_PORT}")
            return True
        else:
            print("❌ Dashboard failed to start")
            return False
            
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")
        return False

def test_system():
    """Test if both services are working."""
    print("🧪 Testing system...")
    
    # Test backend
    try:
        response = requests.get(f"http://{settings.API_HOST}:{settings.API_PORT}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend API is responding")
        else:
            print("❌ Backend API not responding properly")
            return False
    except:
        print("❌ Backend API not accessible")
        return False
    
    # Test dashboard
    try:
        response = requests.get(f"http://{settings.DASHBOARD_HOST}:{settings.DASHBOARD_PORT}/", timeout=5)
        if response.status_code == 200:
            print("✅ Streamlit dashboard is responding")
        else:
            print("❌ Streamlit dashboard not responding properly")
            return False
    except:
        print("❌ Streamlit dashboard not accessible")
        return False
    
    return True

def check_dependencies():
    """Check if all required dependencies are installed."""
    print("🔍 Checking dependencies...")
    
    required_modules = [
        'fastapi', 'uvicorn', 'streamlit', 'pytesseract', 
        'PIL', 'pdf2image', 'sqlalchemy', 'pandas'
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print(f"❌ Missing dependencies: {', '.join(missing_modules)}")
        print("Please install missing dependencies with: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies are installed")
    return True

def main():
    """Main startup function."""
    print("🎯 OCR Receipt Processor System Startup")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Check if database exists
    if not os.path.exists("data/receipts.db"):
        print("📊 Database not found. Running setup...")
        try:
            subprocess.run([sys.executable, "scripts/setup_database.py"], check=True)
        except subprocess.CalledProcessError:
            print("❌ Database setup failed")
            return
    
    # Kill existing processes
    kill_processes()
    
    # Start backend
    backend_ok = start_backend()
    if not backend_ok:
        print("❌ Failed to start backend. Exiting.")
        return
    
    # Start dashboard
    dashboard_ok = start_dashboard()
    if not dashboard_ok:
        print("❌ Failed to start dashboard. Exiting.")
        return
    
    # Test system
    if test_system():
        print("\n🎉 SYSTEM STARTED SUCCESSFULLY!")
        print("=" * 50)
        print("🌐 Access Points:")
        print(f"   Backend API: http://{settings.API_HOST}:{settings.API_PORT}")
        print(f"   API Docs:    http://{settings.API_HOST}:{settings.API_PORT}/docs")
        print(f"   Dashboard:   http://{settings.DASHBOARD_HOST}:{settings.DASHBOARD_PORT}")
        print("\n📊 Available Features:")
        print("   • Upload receipts (images/PDFs)")
        print("   • Advanced search (6 algorithms)")
        print("   • Advanced sorting (4 algorithms)")
        print("   • Statistical aggregations")
        print("   • Export functionality")
        print("   • Real-time analytics")
        print("\n🔄 To stop the system, press Ctrl+C")
        
        try:
            # Keep the script running
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutting down system...")
            kill_processes()
            print("✅ System stopped")
    else:
        print("❌ System test failed")

if __name__ == "__main__":
    main() 