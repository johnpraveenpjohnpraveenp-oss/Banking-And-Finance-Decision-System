# 🏦 SmartBank AI – Banking & Finance Smart Decision System

An end-to-end Machine Learning web platform for automated loan eligibility evaluation, fraud risk scoring, and interactive financial calculations. Built using **Python**, **Flask**, **Scikit-Learn (Random Forest)**, and modern UI design.

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0.2-green?logo=flask)
![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.4-orange?logo=scikit-learn)
![License](https://img.shields.io/badge/License-MIT-purple)

---

## 🌟 Key Features

- 🧠 **Machine Learning Loan Approval**: Predicts loan eligibility instantly using an ensemble **Random Forest Classifier** trained on financial parameters.
- 🛡️ **Rule-Based Fraud Detection System**: Multi-parameter credit risk engine identifying suspicious loan requests, abnormal Debt-to-Income (DTI) ratios, and credit anomalies.
- 🧮 **Interactive EMI Calculator**: Real-time principal, interest, and monthly EMI breakdown.
- 🔐 **Secure Role-Based Authentication**: Hashed password user login/signup with separate `Admin` and `User` privilege levels.
- 📊 **Comprehensive Admin Dashboard**: Live model metrics (*Accuracy*, *Precision*, *Recall*, *F1-Score*), system usage statistics, and prediction audit logs.
- 📄 **Print & PDF Export Ready**: Official formatted approval / rejection result breakdown cards.

---

## 📈 ML Model Performance

| Metric | Score |
|---|---|
| **Accuracy** | **90.0%** |
| **Precision** | **91.0%** |
| **Recall** | **96.3%** |
| **F1-Score** | **93.6%** |
| **Algorithm** | **Random Forest Classifier** (150 Decision Trees) |

---

## 📁 Repository Structure

```
Banking-And-Finance-Decision-System/
├── app.py                  # Main Flask application & API routes
├── train_model.py          # Synthetic dataset generation & ML pipeline training script
├── model.pkl               # Serialized ML Pipeline & performance metrics
├── requirements.txt        # Production dependencies
├── Procfile                # Heroku / Render WSGI entry point
├── render.yaml             # Render deployment configuration
├── run.bat                 # Windows quick launcher
├── static/
│   ├── css/style.css       # Design system & dark gradient UI
│   └── js/script.js        # Dynamic UI counters & animations
└── templates/              # Jinja2 HTML templates
    ├── base.html
    ├── index.html
    ├── login.html
    ├── signup.html
    ├── predict.html
    ├── result.html
    ├── emi_calculator.html
    ├── fraud_checker.html
    ├── history.html
    ├── dashboard.html
    ├── about.html
    └── contact.html
```

---

## 🚀 Local Installation & Quick Start

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/johnpraveenpjohnpraveenp-oss/Banking-And-Finance-Decision-System.git
   cd Banking-And-Finance-Decision-System
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Train the ML Model** *(Optional – pre-trained `model.pkl` is included)*:
   ```bash
   python train_model.py
   ```

4. **Run the Flask Web Application**:
   ```bash
   python app.py
   ```
   *or double-click `run.bat` on Windows.*

5. **Open in Browser**:
   Navigate to **`http://127.0.0.1:5000`**

---

## 🔑 Demo Credentials

- **Admin Login**: `admin` / `admin123`
- **User Registration**: Create any custom user account via the `/signup` page.

---

## ☁️ Live Cloud Deployment (Render / Railway)

### Deploy on Render (Recommended Free Hosting):
1. Create a free account on [Render.com](https://render.com).
2. Click **New +** $\rightarrow$ **Web Service**.
3. Connect your GitHub repository `johnpraveenpjohnpraveenp-oss/Banking-And-Finance-Decision-System`.
4. Render will auto-detect `render.yaml` or set:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
5. Click **Create Web Service** — your ML system will be live!

---

## 📜 License

This project is open-source under the **MIT License**.
