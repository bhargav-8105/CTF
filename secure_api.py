from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import jwt, datetime, hashlib
from functools import wraps

app = Flask(__name__)
app.secret_key = "A_Very_Secret_Key_For_Sessions"  # for session management
SECRET_KEY = "A_Strong_SECRET_Key!"

users = {}

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = session.get('token')
        if not token:
            return redirect(url_for('login_view'))
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            session.pop('token', None)
            return redirect(url_for('login_view'))
        except Exception:
            session.pop('token', None)
            return redirect(url_for('login_view'))
        return f(payload, *args, **kwargs)
    return decorated

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register_view():
    message = ""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if not username or not password:
            message = "Username and password required"
        elif username in users:
            message = "User already exists"
        else:
            users[username] = hash_password(password)
            return redirect(url_for('login_view'))
    return render_template('register.html', message=message)

@app.route('/login', methods=['GET', 'POST'])
def login_view():
    message = ""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        stored = users.get(username)
        if not stored or hash_password(password) != stored:
            message = "Invalid credentials"
        else:
            payload = {
                'username': username,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
            }
            token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
            session['token'] = token
            return redirect(url_for('profile_view'))
    return render_template('login.html', message=message)

@app.route('/profile')
@token_required
def profile_view(payload):
    return render_template('profile.html', username=payload['username'])

@app.route('/logout')
def logout():
    session.pop('token', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
