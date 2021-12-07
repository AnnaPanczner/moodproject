import firebase_admin as fba
from firebase_admin import auth
from flask import Flask, render_template, request, url_for, redirect, jsonify
import pyrebase
import json
import secrets

app = Flask(__name__, template_folder='./templates',static_folder='./static')
app.config['SESSION_TYPE'] = 'filesystem'
secret = secrets.token_urlsafe(32)
app.secret_key = secret
cred = fba.credentials.Certificate('firebaseadmin.json')
firebase = fba.initialize_app(cred)
pb = pyrebase.initialize_app(json.load(open('firebaseconfig.json')))

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET','POST'])
def login():
    return render_template('login.html')

#Api route to sign up a new user
@app.route('/loginsignup', methods=['GET','POST'])
def signup():
    email = request.form.get('email')
    password = request.form.get('password')
    if email is None or password is None:
        return jsonify(status="fail", response="no email or password provided")
    try:
        user = auth.create_user(email=email, password=password)
        try:
            user = pb.auth().sign_in_with_email_and_password(email, password)
            token = user['idToken']
            return jsonify(status="created", response=token)
        except:
            return jsonify(status="success", response="Error logging in.")
    except Exception as e:
        if "EMAIL_EXISTS" in str(e):
            try:
                user = pb.auth().sign_in_with_email_and_password(email, password)
                token = user['idToken']
                return jsonify(status="exists", response=token)
            except:
                return jsonify(status="exists", response="Error logging in.")
        return jsonify(status="fail", response=str(e))

if __name__ == '__main__':
    app.run() #run app (for testing, on localhost)