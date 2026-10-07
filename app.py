import os
import json
import joblib
import numpy as np
import pandas as pd
from datetime import datetime
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from flask import (Flask, render_template, request, redirect, url_for,
                   flash, jsonify, session)

# ─── App Setup ───────────────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = 'smartbank_ai_secret_2026_xK9mQ'

BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
USERS_FILE  = os.path.join(BASE_DIR, 'users.json')
HISTORY_FILE= os.path.join(BASE_DIR, 'history.json')

# ─── JSON Helpers ────────────────────────────────────────────────────────────
def load_users():
    if not os.path.exists(USERS_FILE):
        default = {
            "admin": {
                "password": generate_password_hash("admin123"),
                "name": "Admin User",
                "email": "admin@smartbank.ai",
                "role": "admin",
                "created_at": datetime.now().isoformat()
            }
        }
        save_users(default)
        return default
    with open(USERS_FILE, 'r') as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def load_history():
    if not os.path.exists(HISTORY_FILE):
        return []
    with open(HISTORY_FILE, 'r') as f:
        return json.load(f)

def save_history(history):
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)

def append_history(record):
    history = load_history()
    history.insert(0, record)
    save_history(history[:500])

# ─── Helper: always get metrics safely ───────────────────────────────────────
def get_metrics():
    global model_data
    return model_data.get('metrics', {}) if model_data else {}

# ─── Auth Decorators ──────────────────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'username' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'username' not in session:
            flash('Please log in.', 'warning')
            return redirect(url_for('login'))
        users = load_users()
        u = users.get(session['username'], {})
        if u.get('role') != 'admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated

# ─── ML Model ────────────────────────────────────────────────────────────────
model_data = None

def load_ml_model():
    global model_data
    model_path = os.path.join(BASE_DIR, 'model.pkl')
    if not os.path.exists(model_path):
        print("model.pkl not found - training now ...")
        import train_model
        train_model.train_and_evaluate()
    try:
        model_data = joblib.load(model_path)
        print("[+] ML Model loaded successfully.")
    except Exception as e:
        print(f"Error loading model: {e}")
        model_data = None

load_ml_model()

# ─── Fraud Detection ──────────────────────────────────────────────────────────
def detect_fraud(age, income, credit_score, loan_amount, loan_term, existing_loans):
    flags = []
    risk_score = 0

    if credit_score < 400:
        flags.append("Critically low credit score (< 400)")
        risk_score += 35
    elif credit_score < 500:
        flags.append("Very low credit score (< 500)")
        risk_score += 20

    dti = (loan_amount / income) * 100 if income > 0 else 9999
    if dti > 400:
        flags.append("Extreme Debt-to-Income ratio (>400%)")
        risk_score += 30

    if loan_amount > income * 5:
        flags.append("Loan amount exceeds 5x annual income")
        risk_score += 25

    if existing_loans >= 4:
        flags.append(f"High number of existing loans ({existing_loans})")
        risk_score += 20

    if age < 20 and loan_amount > 50000:
        flags.append("Unusually high loan for very young applicant")
        risk_score += 15

    if loan_term > 360:
        flags.append("Loan term exceeds 30 years")
        risk_score += 10

    score = min(risk_score, 100)
    if score >= 50:
        level = "High"
    elif score >= 25:
        level = "Medium"
    else:
        level = "Low"

    return {"level": level, "score": score, "flags": flags}

# ─── EMI Calculator ──────────────────────────────────────────────────────────
def calculate_emi(principal, annual_rate_pct, months):
    if annual_rate_pct <= 0 or months <= 0:
        return round(principal / months, 2) if months > 0 else 0
    r = (annual_rate_pct / 100) / 12
    emi = principal * r * (1 + r) ** months / ((1 + r) ** months - 1)
    return round(emi, 2)

# ─── Auth Routes ─────────────────────────────────────────────────────────────
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('home'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip().lower()
        password = request.form.get('password', '')
        users = load_users()
        user  = users.get(username)
        if user and check_password_hash(user['password'], password):
            session['username'] = username
            session['name']     = user['name']
            session['role']     = user.get('role', 'user')
            flash(f"Welcome back, {user['name']}!", 'success')
            return redirect(url_for('home'))
        flash('Invalid username or password.', 'danger')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if 'username' in session:
        return redirect(url_for('home'))
    if request.method == 'POST':
        name     = request.form.get('name', '').strip()
        username = request.form.get('username', '').strip().lower()
        email    = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm  = request.form.get('confirm_password', '')

        if not all([name, username, email, password]):
            flash('All fields are required.', 'danger')
            return render_template('signup.html')
        if password != confirm:
            flash('Passwords do not match.', 'danger')
            return render_template('signup.html')
        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return render_template('signup.html')

        users = load_users()
        if username in users:
            flash('Username already exists. Please choose another.', 'danger')
            return render_template('signup.html')

        users[username] = {
            'password': generate_password_hash(password),
            'name': name,
            'email': email,
            'role': 'user',
            'created_at': datetime.now().isoformat()
        }
        save_users(users)
        flash('Account created! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/logout')
def logout():
    name = session.get('name', 'User')
    session.clear()
    flash(f'Goodbye, {name}! You have been logged out.', 'info')
    return redirect(url_for('login'))

# ─── Main Routes ─────────────────────────────────────────────────────────────
@app.route('/')
@login_required
def home():
    metrics = get_metrics()
    history = load_history()
    user_history = [h for h in history if h.get('username') == session['username']]
    recent = user_history[:5]
    stats = {
        'total':    len(user_history),
        'approved': sum(1 for h in user_history if h.get('result') == 'Approved'),
        'rejected': sum(1 for h in user_history if h.get('result') == 'Rejected'),
    }
    return render_template('index.html', metrics=metrics, recent=recent, stats=stats)


@app.route('/predict', methods=['GET', 'POST'])
@login_required
def predict():
    metrics = get_metrics()

    if request.method == 'GET':
        return render_template('predict.html', metrics=metrics)

    # ── POST: run prediction ─────────────────────────────────────────────────
    try:
        if model_data is None or 'pipeline' not in model_data:
            flash("ML model not loaded. Please contact admin.", "danger")
            return render_template('predict.html', metrics=metrics)

        age               = float(request.form.get('age', 0))
        income            = float(request.form.get('income', 0))
        credit_score      = float(request.form.get('credit_score', 0))
        loan_amount       = float(request.form.get('loan_amount', 0))
        loan_term         = float(request.form.get('loan_term', 0))
        employment_status = request.form.get('employment_status', '').strip()
        existing_loans    = int(request.form.get('existing_loans', 0))
        education         = request.form.get('education', '').strip()
        self_employed     = request.form.get('self_employed', '').strip()
        dependents        = int(request.form.get('dependents', 0))
        interest_rate     = float(request.form.get('interest_rate', 8.5))

        # Validation
        errors = []
        if age < 18 or age > 100:               errors.append("Age must be 18-100.")
        if income <= 0:                          errors.append("Annual income must be > 0.")
        if credit_score < 300 or credit_score > 850: errors.append("Credit score must be 300-850.")
        if loan_amount <= 0:                     errors.append("Loan amount must be > 0.")
        if loan_term <= 0:                       errors.append("Loan term must be > 0.")
        for e in errors:
            flash(e, 'warning')
        if errors:
            return render_template('predict.html', metrics=metrics)

        input_df = pd.DataFrame([{
            'Age': age, 'AnnualIncome': income, 'CreditScore': credit_score,
            'LoanAmount': loan_amount, 'LoanTerm': loan_term,
            'EmploymentStatus': employment_status, 'ExistingLoans': existing_loans,
            'Education': education, 'SelfEmployed': self_employed, 'Dependents': dependents
        }])

        pipeline      = model_data['pipeline']
        prediction    = pipeline.predict(input_df)[0]
        probs         = pipeline.predict_proba(input_df)[0]
        approval_prob = round(float(probs[1]) * 100, 1)
        reject_prob   = round(float(probs[0]) * 100, 1)
        is_approved   = bool(prediction == 1)

        dti_ratio = round((loan_amount / income) * 100, 1)
        emi       = calculate_emi(loan_amount, interest_rate, int(loan_term))
        total_pay = round(emi * loan_term, 2)
        total_int = round(total_pay - loan_amount, 2)

        if credit_score >= 750:   credit_rating = "Excellent"
        elif credit_score >= 700: credit_rating = "Very Good"
        elif credit_score >= 640: credit_rating = "Fair"
        else:                     credit_rating = "Poor / High Risk"

        explanations = []
        if is_approved:
            if credit_score >= 680:
                explanations.append(f"Strong Credit Score ({int(credit_score)}) shows solid creditworthiness.")
            if dti_ratio <= 150:
                explanations.append(f"Favorable DTI ratio ({dti_ratio}%) demonstrates repayment capacity.")
            if employment_status in ['Employed', 'Self-Employed']:
                explanations.append(f"Stable employment ({employment_status}) lowers default risk.")
            if education == 'Graduate':
                explanations.append("Graduate education positively impacts credit stability.")
            if not explanations:
                explanations.append("Overall financial metrics meet approval criteria.")
        else:
            if credit_score < 640:
                explanations.append(f"Low Credit Score ({int(credit_score)}) poses significant default risk.")
            if dti_ratio > 250:
                explanations.append(f"High Loan-to-Income ratio ({dti_ratio}%) exceeds safe lending limits.")
            if employment_status == 'Unemployed':
                explanations.append("Unemployed status lacks verifiable income for loan servicing.")
            if existing_loans >= 3:
                explanations.append(f"Multiple existing loans ({existing_loans}) elevate total debt exposure.")
            if not explanations:
                explanations.append("Combined risk parameters exceeded automated approval thresholds.")

        fraud = detect_fraud(age, income, credit_score, loan_amount, loan_term, existing_loans)

        user_data = {
            'age': int(age),
            'income':            f"Rs.{income:,.0f}",
            'credit_score':      int(credit_score),
            'loan_amount':       f"Rs.{loan_amount:,.0f}",
            'loan_term':         f"{int(loan_term)} Months",
            'employment_status': employment_status,
            'existing_loans':    existing_loans,
            'education':         education,
            'self_employed':     self_employed,
            'dependents':        dependents,
            'dti_ratio':         f"{dti_ratio}%",
            'credit_rating':     credit_rating,
            'interest_rate':     f"{interest_rate}%",
            'emi':               f"Rs.{emi:,.2f}",
            'total_payment':     f"Rs.{total_pay:,.2f}",
            'total_interest':    f"Rs.{total_int:,.2f}",
        }

        record = {
            'id':           int(datetime.now().timestamp() * 1000),
            'username':     session['username'],
            'name':         session['name'],
            'timestamp':    datetime.now().strftime('%d %b %Y, %H:%M'),
            'result':       'Approved' if is_approved else 'Rejected',
            'approval_prob': approval_prob,
            'credit_score': int(credit_score),
            'loan_amount':  loan_amount,
            'income':       income,
            'fraud_level':  fraud['level'],
        }
        append_history(record)

        return render_template(
            'result.html',
            is_approved=is_approved,
            approval_prob=approval_prob,
            rejection_prob=reject_prob,
            explanations=explanations,
            user_data=user_data,
            metrics=metrics,
            fraud=fraud,
        )

    except Exception as e:
        print(f"Prediction error: {e}")
        import traceback; traceback.print_exc()
        flash(f"Error processing prediction: {str(e)}", "danger")
        return render_template('predict.html', metrics=metrics)


@app.route('/emi-calculator', methods=['GET', 'POST'])
@login_required
def emi_calculator():
    result = None
    if request.method == 'POST':
        try:
            principal   = float(request.form.get('principal', 0))
            annual_rate = float(request.form.get('annual_rate', 0))
            months      = int(request.form.get('months', 0))
            if principal > 0 and months > 0:
                emi       = calculate_emi(principal, annual_rate, months)
                total_pay = round(emi * months, 2)
                total_int = round(total_pay - principal, 2)
                result = {
                    'emi':           emi,
                    'total_payment': total_pay,
                    'total_interest':total_int,
                    'principal':     principal,
                    'annual_rate':   annual_rate,
                    'months':        months,
                }
        except Exception as e:
            flash(f"Calculation error: {e}", "danger")
    return render_template('emi_calculator.html', result=result)


@app.route('/fraud-checker', methods=['GET', 'POST'])
@login_required
def fraud_checker():
    fraud     = None
    form_data = {}
    if request.method == 'POST':
        try:
            age            = float(request.form.get('age', 30))
            income         = float(request.form.get('income', 500000))
            credit_score   = float(request.form.get('credit_score', 650))
            loan_amount    = float(request.form.get('loan_amount', 1000000))
            loan_term      = float(request.form.get('loan_term', 36))
            existing_loans = int(request.form.get('existing_loans', 0))
            fraud     = detect_fraud(age, income, credit_score, loan_amount, loan_term, existing_loans)
            form_data = {
                'age': age, 'income': income, 'credit_score': credit_score,
                'loan_amount': loan_amount, 'loan_term': loan_term, 'existing_loans': existing_loans,
            }
        except Exception as e:
            flash(f"Error: {e}", "danger")
    return render_template('fraud_checker.html', fraud=fraud, form_data=form_data)


@app.route('/history')
@login_required
def history():
    all_history  = load_history()
    user_history = [h for h in all_history if h.get('username') == session['username']]
    return render_template('history.html', history=user_history)


@app.route('/dashboard')
@admin_required
def dashboard():
    all_history = load_history()
    users       = load_users()
    metrics     = get_metrics()

    total      = len(all_history)
    approved   = sum(1 for h in all_history if h.get('result') == 'Approved')
    rejected   = total - approved
    high_fraud = sum(1 for h in all_history if h.get('fraud_level') == 'High')

    return render_template(
        'dashboard.html',
        all_history=all_history[:50],
        users=users,
        metrics=metrics,
        stats={
            'total':       total,
            'approved':    approved,
            'rejected':    rejected,
            'high_fraud':  high_fraud,
            'total_users': len(users),
        }
    )


@app.route('/about')
@login_required
def about():
    return render_template('about.html', metrics=get_metrics())


@app.route('/contact', methods=['GET', 'POST'])
@login_required
def contact():
    if request.method == 'POST':
        name  = request.form.get('name', '')
        email = request.form.get('email', '')
        flash(f"Thank you {name}! Your message was received. We will contact you at {email} soon.", 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html')


# ─── API ─────────────────────────────────────────────────────────────────────
@app.route('/api/model-info')
def model_info():
    if model_data:
        return jsonify({'status': 'active', 'metrics': get_metrics()})
    return jsonify({'status': 'error', 'message': 'Model not loaded'}), 500


@app.route('/api/stats')
@login_required
def api_stats():
    history = load_history()
    user_h  = [h for h in history if h.get('username') == session['username']]
    return jsonify({
        'total':    len(user_h),
        'approved': sum(1 for h in user_h if h.get('result') == 'Approved'),
        'rejected': sum(1 for h in user_h if h.get('result') == 'Rejected'),
    })


# ─── Entry Point ─────────────────────────────────────────────────────────────
if __name__ == '__main__':
    print("[*] SmartBank AI starting on http://127.0.0.1:5000 ...")
    app.run(host='127.0.0.1', port=5000, debug=True)
