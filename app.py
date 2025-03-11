from flask import Flask, request, render_template, redirect, url_for, session, flash
import bcrypt  # type: ignore
import os
import secrets
import smtplib
from email.mime.text import MIMEText
from flask_dance.contrib.google import make_google_blueprint, google  # type: ignore
from flask_dance.contrib.github import make_github_blueprint, github  # type: ignore
from flask_limiter import Limiter  # type: ignore
from flask_limiter.util import get_remote_address  # type: ignore
from flask_session import Session  # type: ignore
from dotenv import load_dotenv  # type: ignore
import atexit
from database.db_manager import db
from src.pipelines.prediction_pipeline import CustomData, PredictPipeline  # type: ignore
import random

# Load environment variables
load_dotenv()
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # Allow OAuth without HTTPS (Dev only)

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = os.getenv("SECRET_KEY", secrets.token_hex(16))

# Rate Limiter
limiter = Limiter(key_func=get_remote_address, storage_uri="memory://")
limiter.init_app(app)

# Session Configuration
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Google OAuth
google_bp = make_google_blueprint(
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    redirect_to="google_login_callback")
app.register_blueprint(google_bp, url_prefix="/login")

# GitHub OAuth
github_bp = make_github_blueprint(
    client_id=os.getenv("GITHUB_CLIENT_ID"),
    client_secret=os.getenv("GITHUB_CLIENT_SECRET"),
    redirect_to="github_login_callback")
app.register_blueprint(github_bp, url_prefix="/login")

# Helper Functions
def send_otp(email, otp):
    """Send OTP for password reset via email."""
    sender_email = os.getenv("EMAIL_SENDER")
    sender_password = os.getenv("EMAIL_PASSWORD")
    
    if not sender_email or not sender_password:
        print("Email credentials not configured in .env file")
        return False
        
    msg = MIMEText(f"Your OTP code for password reset is {otp}")
    msg['Subject'] = "Password Reset OTP"
    msg['From'] = sender_email
    msg['To'] = email
    
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, email, msg.as_string())
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def generate_otp():
    """Generate a 6-digit OTP."""
    return str(random.randint(100000, 999999))

def hash_password(password):
    """Hash user password."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password, hashed):
    """Verify hashed password."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

# Routes
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('home.html')

@app.route('/predict_datapoint', methods=['GET', 'POST'])
def predict_datapoint():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        data = CustomData(
            gender=request.form.get('gender'),
            race_ethnicity=request.form.get('ethnicity'),
            parental_level_of_education=request.form.get('parental_level_of_education'),
            lunch=request.form.get('lunch'),
            test_preparation_course=request.form.get('test_preparation_course'),
            reading_score=float(request.form.get('reading_score')),
            writing_score=float(request.form.get('writing_score'))
        )
        pred_df = data.get_data_as_data_frame()
        predict_pipeline = PredictPipeline()
        results = predict_pipeline.predict(pred_df)

        return render_template('home.html', results=results[0])
    
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = db.get_user_by_email(email)

        if user and check_password(password, user[1]):
            session['user_id'] = user[0]
            session['user_email'] = email
            flash("✅ Login successful!", "success")
            return redirect(url_for('index'))
        else:
            flash("❌ Invalid email or password.", "error")
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash("❌ Passwords do not match!", "error")
            return redirect(url_for('register'))

        # Check if user already exists
        existing_user = db.get_user_by_email(email)
        if existing_user:
            flash("❌ Email already registered. Please login.", "error")
            return redirect(url_for('login'))

        hashed_password = hash_password(password)

        if db.insert_user(username, email, hashed_password):
            flash("✅ Account created successfully! 🎉", "success")
            return redirect(url_for('login'))
        else:
            flash("❌ Registration failed. Try again!", "error")
    
    return render_template('register.html')

@app.route('/forgot-password', methods=['GET'])
def forgot_password():
    return render_template('forgot_password.html')

@app.route('/forgot-password/send-otp', methods=['POST'])
@limiter.limit("3 per minute")
def send_otp_route():
    email = request.form.get('email')
    user = db.get_user_by_email(email)

    if not user:
        flash("❌ Email not found! Please check your email.", "error")
        return redirect(url_for('forgot_password'))

    otp = generate_otp()
    if db.store_otp(email, otp) and send_otp(email, otp):
        flash("✅ OTP sent successfully! Check your email.", "success")
    else:
        flash("❌ Failed to send OTP. Please try again later.", "error")
    
    return redirect(url_for('forgot_password'))

@app.route('/forgot-password/verify-otp', methods=['POST'])
@limiter.limit("5 per minute")
def verify_otp():
    email = request.form.get('email')
    otp = request.form.get('otp')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_new_password')

    if new_password != confirm_password:
        flash("❌ Passwords do not match!", "error")
        return redirect(url_for('forgot_password'))

    if db.verify_otp(email, otp):
        hashed_password = hash_password(new_password)
        if db.update_password(email, hashed_password):
            flash("✅ Password reset successful! 🎉", "success")
            return redirect(url_for('login'))
        else:
            flash("❌ Password update failed. Try again!", "error")
    else:
        flash("❌ Invalid or expired OTP. Try again!", "error")
    
    return redirect(url_for('forgot_password'))

@app.route('/logout')
def logout():
    session.clear()
    flash("ℹ️ You have been logged out.", "info")
    return redirect(url_for('login'))

# OAuth Login Callbacks
@app.route('/google-login')
def google_login():
    if not google.authorized:
        return redirect(url_for('google.login'))
    
    resp = google.get('/oauth2/v1/userinfo')
    if resp.ok:
        user_info = resp.json()
        email = user_info['email']
        
        # Check if user exists
        user = db.get_user_by_email(email)
        if not user:
            # Create a new user with a random password
            random_password = secrets.token_hex(16)
            hashed_password = hash_password(random_password)
            username = user_info.get('name', email.split('@')[0])
            db.insert_user(username, email, hashed_password)
            
            # Get the newly created user
            user = db.get_user_by_email(email)
        
        if user:
            session['user_id'] = user[0]
            session['user_email'] = email
            flash("✅ Google login successful!", "success")
            return redirect(url_for('index'))
    
    flash("❌ Google login failed. Try again!", "error")
    return redirect(url_for('login'))

@app.route('/github-login')
def github_login():
    if not github.authorized:
        return redirect(url_for('github.login'))
    
    resp = github.get('/user')
    if resp.ok:
        user_info = resp.json()
        
        # GitHub doesn't always provide email, try to get it
        if 'email' in user_info and user_info['email']:
            email = user_info['email']
        else:
            # Get user emails from GitHub API
            emails_resp = github.get('/user/emails')
            if emails_resp.ok:
                emails = emails_resp.json()
                primary_email = next((email['email'] for email in emails if email['primary']), None)
                if primary_email:
                    email = primary_email
                else:
                    flash("❌ Could not retrieve your email from GitHub.", "error")
                    return redirect(url_for('login'))
            else:
                flash("❌ Could not retrieve your email from GitHub.", "error")
                return redirect(url_for('login'))
        
        # Check if user exists
        user = db.get_user_by_email(email)
        if not user:
            # Create a new user with a random password
            random_password = secrets.token_hex(16)
            hashed_password = hash_password(random_password)
            username = user_info.get('login', email.split('@')[0])
            db.insert_user(username, email, hashed_password)
            
            # Get the newly created user
            user = db.get_user_by_email(email)
        
        if user:
            session['user_id'] = user[0]
            session['user_email'] = email
            flash("✅ GitHub login successful!", "success")
            return redirect(url_for('index'))
    
    flash("❌ GitHub login failed. Try again!", "error")
    return redirect(url_for('login'))

# Route for Google OAuth callback
@app.route('/google-login-callback')
def google_login_callback():
    return google_login()

# Route for GitHub OAuth callback
@app.route('/github-login-callback')
def github_login_callback():
    return github_login()

# Close database connection on exit
atexit.register(db.close_connection)

if __name__ == "__main__":
    print("Running on: http://127.0.0.1:5000")
    app.run(debug=True, host='0.0.0.0')