from functools import wraps
import firebase_admin as fba
from firebase_admin import db
from firebase_admin import auth
from flask import Flask, render_template, request, jsonify
import pyrebase
import json
import secrets
from datetime import date

app = Flask(__name__, template_folder='./templates',static_folder='./static')
app.config['SESSION_TYPE'] = 'filesystem'
secret = secrets.token_urlsafe(32)
app.secret_key = secret
cred = fba.credentials.Certificate('firebaseadmin.json')
firebase = fba.initialize_app(cred)
pb = pyrebase.initialize_app(json.load(open('firebaseconfig.json')))

def authenticate(f):
    @wraps(f)
    def wrap(*args,**kwargs):
        if not request.headers.get('authorization'):
            return({'message': 'No token provided. Check request header.'},400)
        try:
            auth.verify_id_token(request.headers['authorization'])
        except:
            return({'message':'Invalid token provided. Check login session.'},400)
        return f(*args, **kwargs)
    return wrap

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET','POST'])
def login():
    return render_template('login.html')

#Api route to sign up a new user
@app.route('/loginsignup', methods=['GET','POST'])
def loginsignup():
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

@app.route('/mood', methods=['GET', 'POST'])
@authenticate
def mood():
    email = ""
    ref = db.reference(url="https://mood-c9d58-default-rtdb.firebaseio.com/")
    returnHTML = "<p>"

    if request.method == 'POST':
        email = request.form.get('email')
        rating = request.form.get('rating')
        d = date.today()

        ref.push().set({
            'email': email,
            'year': d.year,
            'month': str('{:02d}'.format(d.month)),
            'day': str('{:02d}'.format(d.day)),
            'rating': rating
        })
    elif request.method == 'GET':
        email = request.args.get('email')

    rawJSON = ref.get()
    days = []

    if rawJSON != None:
        for entry in rawJSON:
            rating = ref.child(str(entry)).get()
            if(ref.child(str(entry)).child("email").get() == email):
                returnHTML = returnHTML + str(rating) + "<br>"

                day = str(ref.child(str(entry)).child("day").get())
                month = str(ref.child(str(entry)).child("month").get())
                year = str(ref.child(str(entry)).child("year").get())

                uniquedate = year+month+day
                if uniquedate not in days:
                    days.append(uniquedate)

        print(sorted(days))
        days = sorted(days)
        previous = 0

        streaks = []
        streakcounter = 1
        for d in days:
            if(int(d)-previous == 1):
                streakcounter = streakcounter + 1
            else:
                streakcounter = 1
            streaks.append({d: streakcounter})
            previous = int(d)

        returnHTML = returnHTML + "<br>Here are the streaks in the format YYYYMMDD : streak count<br>"
        returnHTML = returnHTML + str(streaks)

    else:
        returnHTML = returnHTML + "There is no data to display."

    #add the html and javascript to support adding more mood ratings
    returnHTML = returnHTML + "</p>"
    returnHTML = returnHTML + "<input type = 'text' placeholder = 'Enter your mood rating' id = 'rating'>"
    returnHTML = returnHTML + "<input type='submit' onclick='rate()' value='Post Mood Rating'\>"
    returnHTML = returnHTML + "<script>"
    returnHTML = returnHTML +  "function rate() {" \
          "var r = document.getElementById('rating').value; $.ajax({ \
          url: '/mood', \
          type: 'POST', \
          data: {email: localStorage.getItem('email'), rating: r}, \
          dataType: 'text', \
          headers: {'Authorization': localStorage.getItem('token')}, \
           success: function(returnData) { \
                window.history.pushState('', '', '/mood'); \
                document.open(); \
                document.write(returnData); \
                document.close(); \
           } \
        }); } </script>"

    return(returnHTML)

if __name__ == '__main__':
    app.run() #run app (for testing, on localhost)