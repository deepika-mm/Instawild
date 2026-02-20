from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import json

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SESSION_SECRET', 'your-secret-key-here')
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# ----- Hardcoded XAMPP / MySQL configuration (embedded per user request) -----
# Note: Storing credentials in code is insecure; this was done per user instruction.
MYSQL_HOST = 'localhost'
MYSQL_USER = 'root'
MYSQL_PASSWORD = ''
MYSQL_DB = 'animal_detections'

# Ensure pymysql is available and create DB if needed
try:
    import pymysql
except Exception as e:
    raise RuntimeError("`pymysql` is required for MySQL support. Install with: pip install pymysql") from e

try:
    conn = pymysql.connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, charset='utf8mb4')
    conn.autocommit(True)
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{MYSQL_DB}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
    cursor.close()
    conn.close()
except Exception as e:
    raise RuntimeError(f"Could not create or connect to MySQL database `{MYSQL_DB}` on host `{MYSQL_HOST}`. Error: {e}") from e

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}?charset=utf8mb4'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    predictions = db.relationship('Prediction', backref='user', lazy=True)

class Prediction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    image_path = db.Column(db.String(255), nullable=False)
    animal_detected = db.Column(db.String(100))
    wound_detected = db.Column(db.Boolean, default=False)
    behavior = db.Column(db.String(100))
    confidence = db.Column(db.Float)
    prediction_data = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def send_email(to_email, subject, body):
    # ----- Hardcoded SMTP credentials (embedded per user request) -----
    # Note: Hardcoding credentials is insecure but requested by the user.
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    smtp_user = 'sainadhpanda4@gmail.com'
    smtp_password = 'fjgm wtjh ocmw fbdm'

    if not smtp_user or not smtp_password:
        print("SMTP credentials not configured")
        return False

    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))

    # Try TLS (STARTTLS) first, then fall back to SSL if necessary
    try:
        server = smtplib.SMTP(smtp_server, smtp_port, timeout=10)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e_tls:
        print(f"TLS SMTP send failed: {e_tls}. Trying SSL fallback...")
        try:
            # Common SSL port is 465
            ssl_port = 465
            server = smtplib.SMTP_SSL(smtp_server, ssl_port, timeout=10)
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
            server.quit()
            return True
        except Exception as e_ssl:
            print(f"SSL SMTP send failed: {e_ssl}")
            return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    predictions = Prediction.query.filter_by(user_id=current_user.id).order_by(Prediction.created_at.desc()).all()
    return render_template('dashboard.html', predictions=predictions)

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected', 'danger')
            return redirect(request.url)
        
        file = request.files['file']
        
        if file.filename == '':
            flash('No file selected', 'danger')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_{filename}"
            # Save file to uploads folder and store relative path with forward slashes
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(save_path)

            # For serving via url_for('static', filename=...), store path relative to 'static'
            image_rel_path = os.path.join('uploads', filename).replace('\\', '/')

            from detection import detect_animal
            result = detect_animal(save_path)
            
            # Normalize animal label: remove leading 'Unknown (... )' if present
            animal_label = result.get('animal', 'Unknown')
            if isinstance(animal_label, str) and animal_label.startswith('Unknown (') and animal_label.endswith(')'):
                # extract what's inside parentheses
                animal_label = animal_label[len('Unknown ('):-1]

            prediction = Prediction(
                user_id=current_user.id,
                image_path=image_rel_path,
                animal_detected=animal_label,
                wound_detected=bool(result.get('wound_detected', False)),
                behavior=result.get('behavior', 'Normal'),
                confidence=float(result.get('confidence', 0.0)),
                prediction_data=json.dumps(result)
            )
            db.session.add(prediction)
            db.session.commit()
            
            email_body = f"""
            <html>
            <body>
                <h2>Animal Detection Results</h2>
                <p><strong>Animal Detected:</strong> {result.get('animal', 'Unknown')}</p>
                <p><strong>Wound Detected:</strong> {'Yes' if result.get('wound_detected') else 'No'}</p>
                <p><strong>Behavior:</strong> {result.get('behavior', 'Normal')}</p>
                <p><strong>Confidence:</strong> {result.get('confidence', 0.0):.2f}%</p>
                <p>Thank you for using our Animal Detection System!</p>
            </body>
            </html>
            """
            
            email_sent = send_email(current_user.email, 'Animal Detection Results', email_body)

            # Determine if SMTP was configured so we only show a warning when user expected email delivery
            smtp_user = os.getenv('SMTP_USER', '')
            smtp_password = os.getenv('SMTP_PASSWORD', '')

            if email_sent:
                flash('Image processed successfully! Check your email for results.', 'success')
            else:
                # If SMTP credentials are present but sending failed, show a warning; otherwise just show success.
                if smtp_user and smtp_password:
                    flash('Image processed successfully! Email delivery failed (check SMTP settings).', 'warning')
                else:
                    flash('Image processed successfully!', 'success')
            return redirect(url_for('result', prediction_id=prediction.id))
    
    return render_template('upload.html')

@app.route('/result/<int:prediction_id>')
@login_required
def result(prediction_id):
    prediction = Prediction.query.get_or_404(prediction_id)
    if prediction.user_id != current_user.id:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('dashboard'))
    
    return render_template('result.html', prediction=prediction)

@app.route('/analytics')
@login_required
def analytics():
    predictions = Prediction.query.filter_by(user_id=current_user.id).all()
    
    animal_counts = {}
    wound_count = 0
    behavior_counts = {}
    
    for pred in predictions:
        if pred.animal_detected:
            animal_counts[pred.animal_detected] = animal_counts.get(pred.animal_detected, 0) + 1
        if pred.wound_detected:
            wound_count += 1
        if pred.behavior:
            behavior_counts[pred.behavior] = behavior_counts.get(pred.behavior, 0) + 1
    
    analytics_data = {
        'animal_counts': animal_counts,
        'wound_count': wound_count,
        'total_predictions': len(predictions),
        'behavior_counts': behavior_counts
    }
    
    return render_template('analytics.html', analytics_data=analytics_data)

@app.route('/api/analytics-data')
@login_required
def api_analytics_data():
    predictions = Prediction.query.filter_by(user_id=current_user.id).all()
    
    animal_counts = {}
    wound_count = 0
    behavior_counts = {}
    
    for pred in predictions:
        if pred.animal_detected:
            animal_counts[pred.animal_detected] = animal_counts.get(pred.animal_detected, 0) + 1
        if pred.wound_detected:
            wound_count += 1
        if pred.behavior:
            behavior_counts[pred.behavior] = behavior_counts.get(pred.behavior, 0) + 1
    
    return jsonify({
        'animals': list(animal_counts.keys()),
        'animal_counts': list(animal_counts.values()),
        'behaviors': list(behavior_counts.keys()),
        'behavior_counts': list(behavior_counts.values()),
        'wound_count': wound_count,
        'total': len(predictions)
    })

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
