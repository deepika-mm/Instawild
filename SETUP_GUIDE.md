# Wildlife Detection System - Setup Guide

## Quick Start

The application is ready to use! Simply run:

```bash
python app.py
```

The application will automatically:
1. Create the SQLite database (`instance/wildlife_detection.db`)
2. Initialize all required tables (User and Prediction)
3. Start the Flask server on `http://0.0.0.0:5000`

## Features Overview

### 1. User Authentication
- **Register**: Create a new account with username, email, and password
- **Login**: Secure login with password hashing
- **Session Management**: Protected routes with Flask-Login

### 2. Animal Detection
- Upload wildlife images (JPG, PNG, GIF)
- AI-powered detection (simulated YOLO)
- Identifies:
  - Animal species
  - Wound presence
  - Behavior patterns
  - Confidence scores

### 3. Email Notifications
- Automatic email sent after each analysis
- Contains full detection results
- Configure SMTP settings in `.env` file

### 4. Analytics Dashboard
- Visual charts showing:
  - Animal distribution (pie chart)
  - Behavior patterns (bar chart)
  - Health status (doughnut chart)
- Real-time statistics
- Prediction history

## Database Configuration

### Default (SQLite)
No configuration needed! The app uses SQLite by default:
- Database file: `instance/wildlife_detection.db`
- Automatic initialization
- Perfect for development and testing

### MySQL (Optional)
To use MySQL (e.g., with XAMPP):

1. Create database:
```sql
CREATE DATABASE animal_detection;
```

2. Update `.env`:
```
DB_TYPE=mysql
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DB=animal_detection
```

### PostgreSQL (Optional)
For PostgreSQL on Replit:

```
DB_TYPE=postgresql
DATABASE_URL=your_postgresql_url
```

## Email Configuration

### Gmail SMTP (Recommended)
1. Enable 2-factor authentication on your Google account
2. Generate an app password:
   - Go to Google Account → Security → 2-Step Verification → App passwords
   - Select "Mail" and your device
   - Copy the generated 16-character password

3. Update `.env`:
```
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-16-char-app-password
```

### Other SMTP Providers
Update these values in `.env`:
- `SMTP_SERVER` - Your SMTP server address
- `SMTP_PORT` - SMTP port (usually 587 for TLS)
- `SMTP_USER` - Your email address
- `SMTP_PASSWORD` - Your email password or app password

## Using the Application

### Step 1: Register an Account
1. Click "Get Started" or "Register" on the homepage
2. Fill in username, email, and password
3. Click "Register"

### Step 2: Login
1. Enter your username and password
2. Click "Login"

### Step 3: Upload an Image
1. Go to "Upload Image" from the navigation
2. Select a wildlife image from your computer
3. Click "Analyze Image"
4. View results on the results page
5. Check your email for detailed report

### Step 4: View Analytics
1. Navigate to "Analytics" from the menu
2. See visual charts of your detection history
3. Review statistics and patterns

### Step 5: Check Dashboard
1. Visit "Dashboard" to see all your predictions
2. Filter by date, animal type, or wound status
3. Click "View" to see detailed results for any prediction

## File Upload Limits

- **Maximum file size**: 16 MB
- **Supported formats**: PNG, JPG, JPEG, GIF
- **Storage location**: `static/uploads/`

## YOLO Integration (Future Enhancement)

Currently, the detection system uses simulation for demonstration. To integrate real YOLO:

1. Install ultralytics:
```bash
pip install ultralytics
```

2. Update `detection.py`:
```python
from ultralytics import YOLO

model = YOLO('yolov8n.pt')  # Load model

def detect_animal(image_path):
    results = model(image_path)
    # Process results...
```

3. Train custom models for:
   - Animal species classification
   - Wound detection
   - Behavior analysis

## Security Notes

- Passwords are hashed using Werkzeug's security functions
- Session secret should be changed in production
- File uploads are validated for allowed extensions
- SQL injection protection via SQLAlchemy ORM
- XSS protection via Jinja2 auto-escaping

## Troubleshooting

### Database Issues
- If tables are missing, delete `instance/wildlife_detection.db` and restart
- Check file permissions on `instance/` folder

### Email Not Sending
- Verify SMTP credentials in `.env`
- Check Gmail app password is correct
- Ensure "Less secure app access" is enabled (if not using app passwords)
- Check firewall/network settings

### File Upload Errors
- Ensure `static/uploads/` directory exists
- Check file size (must be under 16MB)
- Verify file format is supported
- Check disk space

## Support

For issues or questions:
1. Check the logs for error messages
2. Verify environment variables in `.env`
3. Ensure all dependencies are installed
4. Review the README.md for additional information
