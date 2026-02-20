# Wildlife Detection & Monitoring System

A professional Flask-based web application for detecting wild animals, analyzing wounds, and monitoring behavior patterns using AI-powered technology.

## Features

- **YOLO Detection** - State-of-the-art animal detection using YOLO algorithm
- **Wound Detection** - Advanced image analysis to identify injuries
- **Behavior Analysis** - Intelligent pattern recognition for animal activities
- **Email Notifications** - Instant email alerts with prediction results
- **Analytics Dashboard** - Comprehensive charts and visualizations
- **Secure Authentication** - Protected user accounts with encrypted passwords

## Setup Instructions

### 1. Environment Configuration

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

Edit `.env` and configure:
- `SESSION_SECRET` - Your secret key for Flask sessions
- MySQL credentials (`MYSQL_HOST`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DB`)
- SMTP credentials for email notifications

### 2. Database Setup

**For MySQL (XAMPP):**
1. Start XAMPP and run MySQL
2. Create database: `CREATE DATABASE animal_detection;`
3. Update `.env` with your MySQL credentials

**For PostgreSQL:**
1. Set `DB_TYPE=postgresql` in `.env`
2. Configure `DATABASE_URL` if needed

### 3. Run the Application

```bash
python app.py
```

The application will:
- Create database tables automatically
- Start on `http://0.0.0.0:5000`

### 4. Usage

1. Register a new account
2. Login with your credentials
3. Upload wildlife images
4. View detection results
5. Check analytics dashboard

## Email Configuration

For Gmail SMTP:
1. Enable 2-factor authentication
2. Generate an app password
3. Use app password in `SMTP_PASSWORD`

## Technology Stack

- **Backend:** Flask, SQLAlchemy, Flask-Login
- **Database:** MySQL / PostgreSQL
- **Frontend:** Bootstrap 5, Chart.js
- **Image Processing:** OpenCV, Pillow
- **Detection:** YOLO (ready for integration)

## Project Structure

```
.
├── app.py                 # Main application
├── detection.py           # Detection logic
├── templates/            # HTML templates
├── static/              
│   ├── css/             # Stylesheets
│   └── uploads/         # User uploads
├── .env                 # Environment config
└── requirements.txt     # Dependencies
```

## Note

The current detection system uses simulation for demonstration. To enable actual YOLO detection, integrate the ultralytics library and trained models in `detection.py`.
