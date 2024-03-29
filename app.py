from flask import Flask, render_template, url_for, redirect, flash, make_response, request
from forms import RegistrationForm, LoginForm, BookingForm
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from bson import ObjectId
import os
import json
app = Flask(__name__)

# app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
# app.config['MONGODB_URI'] = os.environ.get('MONGODB_URI')
app.config['SECRET_KEY'] = "163c1af8b4a801e8fddec7e72b6db4dd"
client = MongoClient("mongodb+srv://public:public@tmu.vgmkgse.mongodb.net/?retryWrites=true&w=majority&appName=TMU")

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)
    
db = client["raspberryECLAIR"]
colUsers = db["users"]
colData = db["data"]

# def readRecentCharges():
    
# def readRecentPrices():
    
# def readHistory():
    
def readSlots(id):
    docMaster = colData.find_one({"_id": ObjectId(id)})
    doc = docMaster["booked"]
    slot1 = doc["slot1"]
    slot2 = doc["slot2"]
    slot3 = doc["slot3"]
    session = []
    if slot1["month"] == "":
        return
    else:
        month = slot1["month"]
        day = slot1["day"]
        time = slot1["time"]
        time = int(time)
        if time > 1300:
            time = time - 1200
            time = str(time)
            while len(time) < 3:
                time = "0" + time
            time = time[:2] + ':' + time[2:] + "PM"
        elif time < 1300 and time >= 1200:
            time = str(time)
            time = time[:2] + ':' + time[2:] + "PM"
        else:
            time = time[:2] + ':' + time[2:] + "PM"
        match month:
            case '1': 
                month = "January"
            case '2': 
                month = "February"
            case '3': 
                month = "March"
            case '4': 
                month = "April"
            case '5': 
                month = "May"
            case '6': 
                month = "June"
            case '7': 
                month = "July"
            case '8': 
                month = "August"
            case '9': 
                month = "September"
            case '10': 
                month = "October"
            case '11': 
                month = "November"
            case '12': 
                month = "December"
        message = month + " " + day + ", " + time
        if len(session) == 0:
            session.append(message)
    if slot2["month"] != "":
        month = slot2["month"]
        day = slot2["day"]
        time = slot2["time"]
        time = int(time)
        if time > 1300:
            time = time - 1200
            time = str(time)
            while len(time) < 3:
                time = "0" + time
            time = time[:2] + ':' + time[2:] + "PM"
        elif time < 1300 and time >= 1200:
            time = str(time)
            time = time[:2] + ':' + time[2:] + "PM"
        else:
            time = time[:2] + ':' + time[2:] + "PM"
        match month:
            case '1': 
                month = "January"
            case '2': 
                month = "February"
            case '3': 
                month = "March"
            case '4': 
                month = "April"
            case '5': 
                month = "May"
            case '6': 
                month = "June"
            case '7': 
                month = "July"
            case '8': 
                month = "August"
            case '9': 
                month = "September"
            case '10': 
                month = "October"
            case '11': 
                month = "November"
            case '12': 
                month = "December"
        message = month + " " + day + ", " + time
        if len(session) == 1:
            session.append(message)
    if slot3["month"] != "":
        month = slot3["month"]
        day = slot3["day"]
        time = slot3["time"]
        if time > 1300:
            time = time - 1200
            time = str(time)
            while len(time) < 3:
                time = "0" + time
            time = time[:2] + ':' + time[2:] + "PM"
        elif time < 1300 and time >= 1200:
            time = str(time)
            time = time[:2] + ':' + time[2:] + "PM"
        else:
            time = time[:2] + ':' + time[2:] + "PM"
        match month:
            case '1': 
                month = "January"
            case '2': 
                month = "February"
            case '3': 
                month = "March"
            case '4': 
                month = "April"
            case '5': 
                month = "May"
            case '6': 
                month = "June"
            case '7': 
                month = "July"
            case '8': 
                month = "August"
            case '9': 
                month = "September"
            case '10': 
                month = "October"
            case '11': 
                month = "November"
            case '12': 
                month = "December"
        message = month + " " + day + ", " + time
        if len(session) == 2:
            session.append(message)
    return session

@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def loginPage():
    form = LoginForm()
    title = "Login"
    resp = make_response(render_template('login.html', form = form, title=title))
    resp.set_cookie('personalID', '', expires=0) 
    if form.validate_on_submit():
        query = {"username" : form.username.data}
        doc = colUsers.find_one(query)
        if doc:
            p=doc["password"]
            if form.password.data == p:
                id = doc["_id"]
                resp = make_response(redirect(url_for('dashMain')))
                resp.set_cookie('personalID', str(id)) 
                return resp
    return resp
    
@app.route('/register', methods=['GET', 'POST'])
def registerPage():
    form = RegistrationForm()
    title = "Register"
    if form.validate_on_submit():
        query = {"username" : form.username.data}
        doc = colUsers.find_one(query)
        if doc:
            return render_template('register.html', form = form, title=title)
        else :
            doc = {"username" : form.username.data, "password" : form.password.data}
            x = colUsers.insert_one(doc)
            file = []
            with open('customerDataModelBlank.json') as file:
                fileData = json.load(file)
            fileData.update({"_id" : x.inserted_id})
            colData.insert_one(fileData)
            resp = make_response(redirect(url_for('dashMain')))
            resp.set_cookie('personalID', str(x.inserted_id)) 
            return resp
    return render_template('register.html', form = form, title=title)

@app.route('/booking', methods=['GET', 'POST'])
def bookingPage():
    form = BookingForm();
    title = "Book a time"
    sesh = readSlots(request.cookies.get('personalID'))
    if form.validate_on_submit():
        print(form.datum.data)
        print(form.submit3.data)
        print(form.submit2.data)
        print(form.submit1.data)
        return redirect(url_for('dashMain'))
    return render_template('bookingPage.html', form = form, title=title, session = sesh)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashMain():
    title = "Dashboard"
    sesh = readSlots(request.cookies.get('personalID'))
    return render_template('dashMain.html', title=title, session = sesh)

@app.route('/history')
def historyPage():
    return render_template('bookingPage.html')

if __name__ == '__main__':
    app.run(debug=True)