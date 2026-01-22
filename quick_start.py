#!/usr/bin/env python3
"""
Quick Start Script for Face Recognition System
Run this to quickly test the system without full setup
"""

import os
import sys
import subprocess
import bcrypt

def create_test_user():
    """Create a test admin user for quick testing"""
    password = "admin123"
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    print(f"Test user credentials:")
    print(f"Username: admin")
    print(f"Password: {password}")
    print(f"Hashed password: {hashed.decode('utf-8')}")
    print("\nAdd this to your MySQL database:")
    print(f"INSERT INTO logins VALUES ('admin', '{hashed.decode('utf-8')}');")

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'flask', 'opencv-python', 'face-recognition', 
        'mysql-connector-python', 'bcrypt', 'waitress'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\nInstall them with:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    print("✅ All required packages are installed!")
    return True

def create_directories():
    """Create required directories"""
    directories = [
        'static/faces',
        'static/temp',
        'templates'
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"📁 Created directory: {directory}")

def main():
    print("🚀 Face Recognition System - Quick Start")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Create test user
    create_test_user()
    
    print("\n" + "=" * 50)
    print("✅ Quick setup complete!")
    print("\n🎯 Next steps:")
    print("1. Set up MySQL database (see SETUP_GUIDE.md)")
    print("2. Add the test user to your database")
    print("3. Run: python app.py")
    print("4. Visit: http://localhost:8080/dashboard")
    print("\n📚 For full setup instructions, see SETUP_GUIDE.md")

if __name__ == "__main__":
    main()
