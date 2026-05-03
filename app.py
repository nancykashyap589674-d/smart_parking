from flask import Flask, render_template, request, redirect, url_for, session, flash
import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
# import mysql.connector   # ❌ DISABLED
import qrcode
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# -------------------------------
# MYSQL CONNECTION (DISABLED)
# -------------------------------
# db = mysql.connector.connect(
#     host="localhost",
#     user="root",
#     password="2004",
#     database="smart_parking",
# )
# cursor = db.cursor(dictionary=True)

# -------------------------------
# EMAIL CONFIGURATION
# -------------------------------
SENDER_EMAIL = "nancykashyap589674@gmail.com"
SENDER_PASSWORD = "jzbthevzcjvjehsa"

# -------------------------------
# GENERATE QR
# -------------------------------
def generate_qr(email):
    filename = f"{email}.png"
    path = os.path.join("static", "qrcodes", filename)

    data = request.host_url + "parking_entry?email=" + email + "&slot=ALL"

    qr = qrcode.make(data)
    qr.save(path)

    return filename

# -------------------------------
# HOME PAGE
# -------------------------------
@app.route('/')
def home():
    return render_template('choose_login.html')

# -------------------------------
# ADMIN LOGIN
# -------------------------------
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == "admin" and password == "1234":
            session['admin'] = True
            flash("Login successful", "success")
            return redirect('/')
        else:
            flash("Invalid username or password", "error")
            return redirect('/admin_login')

    return render_template('admin_login.html')

# -------------------------------
# LOGIN WITH EMAIL + OTP
# -------------------------------
@app.route('/login_email', methods=['GET', 'POST'])
def login_email():
    if request.method == 'POST':
        email = request.form['email']

        otp = random.randint(100000, 999999)
        session['otp'] = otp
        session['temp_email'] = email

        try:
            msg = MIMEMultipart()
            msg['From'] = SENDER_EMAIL
            msg['To'] = email
            msg['Subject'] = "Smart Parking System - OTP"

            body = f"Your OTP is: {otp}"
            msg.attach(MIMEText(body, 'plain'))

            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, email, msg.as_string())
            server.quit()

            flash("OTP sent successfully!")
        except Exception as e:
            flash(f"Error: {str(e)}")

        return redirect(url_for('verify_otp'))

    return render_template('login_email.html')

# -------------------------------
# VERIFY OTP
# -------------------------------
@app.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    if request.method == 'POST':
        entered_otp = request.form['otp']
        saved_otp = str(session.get('otp'))

        if entered_otp == saved_otp:
            session['user'] = session.get('temp_email')
            return redirect(url_for('home'))  # redirect to home instead
        else:
            flash("Invalid OTP")

    return render_template('verify_otp.html')

# -------------------------------
# LOGOUT
# -------------------------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_email'))

# -------------------------------
# RUN
# -------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
