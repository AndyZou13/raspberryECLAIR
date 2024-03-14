from flask import Flask, render_template, url_for, redirect, flash
from forms import RegistrationForm, LoginForm, BookingForm
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import os
import json
app = Flask(__name__)

# app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
# app.config['MONGODB_URI'] = os.environ.get('MONGODB_URI')
app.config['SECRET_KEY'] = "163c1af8b4a801e8fddec7e72b6db4dd"
client = MongoClient("mongodb+srv://public:public@tmu.vgmkgse.mongodb.net/?retryWrites=true&w=majority&appName=TMU", server_api=ServerApi('1'))

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)
    
db = client["raspberryECLAIR"]
colUsers = db["users"]
colData = db["data"]

docMaster = "dummy"
username = "dummy"
session = []
id = "dummy"
# def findData() :
#     doc = colData.find_one({"_id": id})
#     print(doc)
    
# def readRecentCharges():
    
# def readRecentPrices():
    
# def readHistory():
    
def readSlots():
    doc = docMaster["booked"]
    slot1 = doc["slot1"]
    print(slot1)
    slot2 = doc["slot2"]
    slot3 = doc["slot3"]
    if slot1["month"] == "":
        return
    else:
        month = slot1["month"]
        day = slot1["day"]
        time = slot1["time"]
        match month:
            case 1: month = "January"
            case 2: month = "February"
            case 3: month = "March"
            case 4: month = "April"
            case 5: month = "May"
            case 6: month = "June"
            case 7: month = "July"
            case 8: month = "August"
            case 9: month = "September"
            case 10: month = "October"
            case 11: month = "November"
            case 12: month = "December"
        message = month + " " + day + ", " + time[:2] + ':' + time[2:]
        print(message)
    if slot2["month"] != "":
        month = slot2["month"]
        day = slot2["day"]
        time = slot2["time"]
        match month:
            case 1: month = "January"
            case 2: month = "February"
            case 3: month = "March"
            case 4: month = "April"
            case 5: month = "May"
            case 6: month = "June"
            case 7: month = "July"
            case 8: month = "August"
            case 9: month = "September"
            case 10: month = "October"
            case 11: month = "November"
            case 12: month = "December"
        message = month + " " + day + ", " + time[:2] + ':' + time[2:]
        print(message)
    if slot3["month"] != "":
        month = slot3["month"]
        day = slot3["day"]
        time = slot3["time"]
        match month:
            case 1: month = "January"
            case 2: month = "February"
            case 3: month = "March"
            case 4: month = "April"
            case 5: month = "May"
            case 6: month = "June"
            case 7: month = "July"
            case 8: month = "August"
            case 9: month = "September"
            case 10: month = "October"
            case 11: month = "November"
            case 12: month = "December"
        message = month + " " + day + ", " + time[:2] + ':' + time[2:]
        print(message)
@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def loginPage():
    form = LoginForm()
    title = "Login"
    if form.validate_on_submit():
        query = {"username" : form.username.data}
        global docMaster
        docMaster = colUsers.find_one(query)
        if docMaster:
            p=docMaster["password"]
            if form.password.data == p:
                global username
                username = form.username.data
                global id
                id = docMaster["_id"]
                docMaster = colData.find_one({"_id" : id})
                return redirect(url_for('dashMain'))
            return redirect(url_for('loginPage'))
    return render_template('login.html', form = form, title=title)

@app.route('/register', methods=['GET', 'POST'])
def registerPage():
    form = RegistrationForm()
    title = "Register"
    if form.validate_on_submit():
        query = {"username" : form.username.data}
        global docMaster
        docMaster = colUsers.find_one(query)
        if docMaster:
            return render_template('register.html', form = form, title=title)
        else :
            global username
            username = form.username.data
            docMaster = {"username" : form.username.data, "password" : form.password.data}
            x = colUsers.insert_one(docMaster)
            file = []
            with open('customerDataModelBlank.json') as file:
                fileData = json.load(file)
            fileData.update({"_id" : x.inserted_id})
            colData.insert_one(fileData)
            return redirect(url_for('dashMain'))
    return render_template('register.html', form = form, title=title)

@app.route('/booking', methods=['GET', 'POST'])
def bookingPage():
    form = BookingForm();
    title = "Book a time"
    if form.validate_on_submit():
        print(form.datum.data)
        print(form.submit3.data)
        print(form.submit2.data)
        print(form.submit1.data)
    return render_template('bookingPage.html', form = form, title=title, sessions = session)

@app.route('/dashboard')
def dashMain():
    title = "Dashboard"
    readSlots()
    return render_template('dashMain.html', title = title, sessions = session)

if __name__ == '__main__':
    app.run(debug=True)