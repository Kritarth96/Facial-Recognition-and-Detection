# 🚀 Face Recognition System - Complete Setup & Run Guide

## 📋 Prerequisites

### Required Software
1. **Python 3.8+** - [Download from python.org](https://www.python.org/downloads/)
2. **MySQL Server** - [Download from mysql.com](https://dev.mysql.com/downloads/mysql/)
3. **Git** (optional) - [Download from git-scm.com](https://git-scm.com/downloads)
4. **Node.js** (optional, for TypeScript development) - [Download from nodejs.org](https://nodejs.org/)

### Hardware Requirements
- **Camera**: USB webcam or built-in camera
- **RAM**: Minimum 4GB (8GB recommended)
- **Storage**: At least 2GB free space

## 🔧 Installation Steps

### Step 1: Clone or Download the Project
```bash
# If using Git
git clone <repository-url>
cd face_recognition_app

# Or download and extract the ZIP file
```

### Step 2: Set Up Python Environment (Recommended)
```bash
# Create virtual environment
python -m venv face_recognition_env

# Activate virtual environment
# Windows:
face_recognition_env\Scripts\activate
# Linux/Mac:
source face_recognition_env/bin/activate
```

### Step 3: Install Python Dependencies
```bash
# Install all required packages
pip install -r requirements.txt

# If you encounter issues with dlib on Windows:
pip install cmake
pip install dlib
```

### Step 4: Set Up MySQL Database
1. **Start MySQL Server**
2. **Connect to MySQL**:
   ```sql
   mysql -u root -p
   ```
3. **Create Database**:
   ```sql
   CREATE DATABASE capstone;
   USE capstone;
   ```
4. **Create Login Table**:
   ```sql
   CREATE TABLE logins (
       loginids VARCHAR(50) PRIMARY KEY,
       passwords VARCHAR(255) NOT NULL
   );
   ```
5. **Create Admin User**:
   ```python
   # Run this Python script to create hashed password
   import bcrypt
   password = "your_admin_password"
   hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
   print(hashed.decode('utf-8'))
   ```
   ```sql
   INSERT INTO logins VALUES ('admin', 'your_hashed_password_here');
   ```

### Step 5: Configure Database Connection
Edit `app.py` and update the database configuration:
```python
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'your_mysql_password',
    'database': 'capstone'
}
```

### Step 6: Create Required Directories
```bash
mkdir -p static/faces
mkdir -p static/temp
```

### Step 7: Set Up TypeScript (Optional)
```bash
# Install Node.js dependencies
npm install

# Build TypeScript
npm run build

# For development with auto-reload
npm run watch
```

## 🏃‍♂️ Running the Server

### Method 1: Development Mode (Recommended)
```bash
# Navigate to the project directory
cd face_recognition_app

# Activate virtual environment (if using)
# Windows:
face_recognition_env\Scripts\activate
# Linux/Mac:
source face_recognition_env/bin/activate

# Run the development server
python app.py
```

### Method 2: Production Mode
```bash
# For production deployment
python -c "
from app import app
from waitress import serve
serve(app, host='0.0.0.0', port=8080)
"
```

### Method 3: Using the Setup Scripts
```bash
# Windows
setup.bat

# Linux/Mac
chmod +x setup.sh
./setup.sh
```

## 🌐 Accessing the Application

### URLs
- **Modern Dashboard**: http://localhost:8080/dashboard
- **Classic Interface**: http://localhost:8080/
- **Login Page**: http://localhost:8080/login

### Default Login
- **Username**: admin
- **Password**: (the password you set in the database)

## 📱 Using the Modern Dashboard

### Features Overview
1. **Collapsible Sidebar**: Click the hamburger menu to toggle
2. **Image Database**: 
   - Click category headers to expand/collapse
   - Use search to find specific faces
   - Click "Expand All" to show all categories
3. **Camera Feed**: Start/stop live recognition
4. **Upload New Faces**: Drag & drop or click to upload
5. **Analytics**: View recognition statistics

### Navigation Tips
- **Keyboard Shortcuts**:
  - `Ctrl + F`: Open search
  - `Esc`: Close modals
- **Mobile**: Sidebar auto-collapses on small screens
- **Touch**: All controls are touch-friendly

## 🔧 Configuration Options

### Camera Settings
Edit in `app.py`:
```python
KNOWN_FACE_WIDTH_CM = 15.0  # Average face width
FOCAL_LENGTH = 600  # Calibrate for your camera
```

### File Paths
```python
SAVE_DIR = r"C:\Users\krita\CapStone\face_recognition_app\static\faces"
```

### CSS Customization
Edit `static/styles/dashboard.css`:
```css
:root {
    --primary-color: #2563eb;      /* Change brand color */
    --sidebar-width: 320px;        /* Adjust sidebar width */
    /* ... more variables ... */
}
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Camera Not Working
```bash
# Check camera permissions
# Windows: Settings > Privacy > Camera
# Linux: Check /dev/video0 permissions
# Mac: System Preferences > Security & Privacy > Camera
```

#### 2. Face Recognition Not Accurate
- Ensure good lighting
- Upload multiple photos per person
- Use high-quality images (minimum 200x200 pixels)

#### 3. Database Connection Issues
```python
# Test database connection
import mysql.connector
try:
    conn = mysql.connector.connect(**db_config)
    print("✅ Database connected successfully")
    conn.close()
except Exception as e:
    print(f"❌ Database error: {e}")
```

#### 4. Module Import Errors
```bash
# Reinstall specific packages
pip install --upgrade opencv-python
pip install --upgrade face-recognition

# For Windows dlib issues:
pip install --upgrade cmake
pip install dlib
```

#### 5. TypeScript Compilation Errors
```bash
# Clean and rebuild
npm run clean
npm install
npm run build
```

### Performance Optimization

#### 1. Reduce Face Database Size
- Keep face images under 500KB
- Use JPG format for smaller file sizes
- Resize images to 300x300 pixels maximum

#### 2. Camera Feed Optimization
```python
# In app.py, adjust frame processing
def gen_frames(recognize_faces=True, detect_people=False):
    # Reduce frame size for faster processing
    frame = cv2.resize(frame, (640, 480))
```

#### 3. Memory Management
```bash
# Monitor memory usage
# Task Manager (Windows) or htop (Linux)
# Close unnecessary applications
```

## 📊 File Structure Overview

```
face_recognition_app/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── package.json                    # Node.js dependencies
├── tsconfig.json                   # TypeScript configuration
├── setup.bat / setup.sh           # Setup scripts
├── README.md                       # Documentation
├── templates/
│   ├── modern_dashboard.html       # Modern UI template
│   ├── index.html                  # Classic UI template
│   └── login.html                  # Login page
├── static/
│   ├── styles/
│   │   └── dashboard.css           # Modern UI styles
│   ├── js/
│   │   ├── dashboard_clean.js      # Production JavaScript
│   │   └── script.js               # Classic UI scripts
│   ├── faces/                      # Face images directory
│   └── placeholder-face.svg        # Placeholder image
├── src/
│   └── typescript/
│       └── dashboard.ts            # TypeScript source
└── demo.html                       # Standalone demo
```

## 🔒 Security Considerations

### 1. Change Default Passwords
- Create strong admin password
- Use bcrypt for password hashing

### 2. Network Security
```python
# For production, use HTTPS
# Add SSL certificates
# Use environment variables for secrets
```

### 3. File Upload Security
- Validate file types
- Limit file sizes
- Scan for malware (in production)

## 📈 Next Steps

### 1. Add More Features
- Real-time notifications
- Advanced analytics
- User management
- API authentication

### 2. Deploy to Production
- Use nginx as reverse proxy
- Set up SSL certificates
- Configure database backups
- Set up monitoring

### 3. Scale the Application
- Use Redis for caching
- Implement load balancing
- Add database replication
- Use cloud storage for images

## 📞 Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the console output for error messages
3. Ensure all dependencies are installed correctly
4. Verify database connection and camera permissions

## 🎉 Success Checklist

- [ ] Python and MySQL installed
- [ ] Virtual environment created and activated
- [ ] All dependencies installed successfully
- [ ] Database created with admin user
- [ ] Face images directory exists
- [ ] Server starts without errors
- [ ] Can access login page
- [ ] Can log in successfully
- [ ] Modern dashboard loads correctly
- [ ] Camera feed works
- [ ] Can upload face images
- [ ] Face recognition working

**🎯 You're ready to use the Face Recognition System!**
