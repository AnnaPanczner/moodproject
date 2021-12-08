from functools import wraps #for middleware
import firebase_admin as fba #firebase admin tools
from firebase_admin import db #for accessing database
from firebase_admin import auth
from flask import Flask, render_template, request, jsonify
import pyrebase
import json
import secrets
from datetime import date

#app initial setup
app = Flask(__name__, template_folder='./templates',static_folder='./static')
app.config['SESSION_TYPE'] = 'filesystem'
secret = secrets.token_urlsafe(32)
app.secret_key = secret
cred = fba.credentials.Certificate('firebaseadmin.json')
firebase = fba.initialize_app(cred)
pb = pyrebase.initialize_app(json.load(open('firebaseconfig.json')))

#authenticates a user's validity using token
#used as decorator for mood endpoint
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

#home landing page
@app.route('/')
def home():
    return render_template('home.html')

#login page
@app.route('/login', methods=['GET','POST'])
def login():
    return render_template('login.html')

#Attempts to log in or sign up a user (if new)
#will handle errors if error logging in or incorrect credentials
#login html remains displayed as this endpoint's method runs
@app.route('/loginsignup', methods=['POST'])
def loginsignup():
    #get credentials from POST request
    email = request.form.get('email')
    password = request.form.get('password')

    if email is None or password is None: #if either no email or pass
        return jsonify(status="fail", response="no email or password provided")
    try: #try to create a new user
        auth.create_user(email=email, password=password)

        try: #if successful, attempt to authenticate and sign in
            user = pb.auth().sign_in_with_email_and_password(email, password)
            token = user['idToken']
            return jsonify(status="created", response=token)
        except Exception as e: #if failed, return error
            return jsonify(status="fail", response=str(e))

    except Exception as e: #if user creation failed
        if "EMAIL_EXISTS" in str(e): #if it's because email exists, no issue
            try: #try to log in existing user
                user = pb.auth().sign_in_with_email_and_password(email, password)
                token = user['idToken']
                return jsonify(status="exists", response=token)
            except: #error with logging in
                return jsonify(status="exists", response="Error logging in.")

        return jsonify(status="fail", response=str(e)) #else something wrong in creation

#Mood endpoint
#Can GET: returns mood rating and streak data for given email
#Can POST: posts mood rating data and then reloads the page with updated data
@app.route('/mood', methods=['GET', 'POST'])
@authenticate #must be logged in
def mood():
    email = ""
    ref = db.reference(url="https://mood-c9d58-default-rtdb.firebaseio.com/") #Anna's firebase database
    returnHTML = "<p>" #start forming return HTML string

    if request.method == 'POST': #if post, push new JSON
        email = request.form.get('email')
        rating = request.form.get('rating')
        d = date.today()

        ref.push().set({ #push day, month, year, and mood
            'email': email,
            'year': d.year,
            'month': str('{:02d}'.format(d.month)),
            'day': str('{:02d}'.format(d.day)),
            'rating': rating
        })
    elif request.method == 'GET': #else, obtain email through args
        email = request.args.get('email')

    rawJSON = ref.get() #get all data at DB root
    days = []

    if rawJSON != None:
        for entry in rawJSON: #iterate over root level data
            rating = ref.child(str(entry)).get() #get all data for single push (day, month, year, rating)

            if(ref.child(str(entry)).child("email").get() == email): #if user we're looking for
                returnHTML = returnHTML + str(rating) + "<br>" #add this data to return HTML

                day = str(ref.child(str(entry)).child("day").get())
                month = str(ref.child(str(entry)).child("month").get())
                year = str(ref.child(str(entry)).child("year").get())

                uniquedate = year+month+day
                if uniquedate not in days: #add day to list of post days if not already there
                    days.append(uniquedate)

        days = sorted(days) #sort before iteration
        previous = 0
        streaks = [] #stores dicts of days (military format) and streaks as numbers
        streakcounter = 1

        for d in days: #iterate over days in order
            if(int(d)-previous == 1): #if next sequential day
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
    #text input for mood rating and button to submit mood
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