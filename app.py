from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user
from auth import User
from db_utils import fetch_logs

app = Flask(__name__)
app.secret_key = 'your_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(username):
    return User(username)

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.validate(username, password):
            user = User(username)
            login_user(user)
            return redirect(url_for('dashboard'))
        flash("Invalid credentials")
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    logs = fetch_logs()
    return render_template('dashboard.html', logs=logs)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)

