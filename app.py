from flask import Flask, render_template, url_for, redirect, flash, make_response, request, jsonify
from forms import RegistrationForm, LoginForm, BookingForm
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from bson import ObjectId
import os
import json
import calendar
import stripe
import math
import datetime
from bokeh.plotting import figure
from bokeh.models import Range1d
from bokeh.embed import components
app = Flask(__name__)

# app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
# app.config['MONGODB_URI'] = os.environ.get('MONGODB_URI')
app.config['SECRET_KEY'] = "163c1af8b4a801e8fddec7e72b6db4dd"

stripeKeys = {
    "secret_key": 'sk_test_51Ou2ppKySml2ekNAVRVYHbeAiiAx9FR48HW0ZG3Ppx1NvZIBzEhnvnmhEfCWZCWwYMOLphXpClfwNiBLfV8IA4Mp00uISbXiHj',
    "publishable_key": 'pk_test_51Ou2ppKySml2ekNAvQ4TTTCUmCeZ4NDYqIZHFqtHrLYGp5rBGDrHZC3yjkejgqYwgnikhxeZ56hQuI5PfmZsDwN200QH7y4PJQ'
}

client = MongoClient("mongodb+srv://public:public@tmu.vgmkgse.mongodb.net/?retryWrites=true&w=majority&appName=TMU")

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)
    
db = client["raspberryECLAIR"]
colUsers = db["users"]
colData = db["data"]
colCal = db["calendar"]

def graphEverything():
    x1 = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    y1 = [0, 8, 2, 4, 6, 9, 5, 6, 25, 28, 4]

    # the red and blue graphs share this data range
    xr1 = Range1d(start=0, end=30)
    yr1 = Range1d(start=0, end=30)

    # only the green graph uses this data range
    xr2 = Range1d(start=0, end=30)
    yr2 = Range1d(start=0, end=30)

    # build the figures
    p1 = figure(x_range=xr1, y_range=yr1, width=300, height=300)
    p1.scatter(x1, y1, size=12, color="red", alpha=0.5)
    p1.toolbar.logo = None
    p1.toolbar_location = None
    # plots can be a single Bokeh model, a list/tuple, or even a dictionary
    plots = {'Red': p1}

    script, div = components(plots)
    print(script)
    print(div)
    return script, div
    
def readHistory(id):
    docMaster = colData.find_one({"_id": ObjectId(id)})
    doc = docMaster["history"]
    months = doc["month"]
    days = doc["day"]
    TOD = doc["TOD"]
    paid = doc["paid"]
    months = months.split()
    days = days.split()
    TOD = TOD.split()
    paid = paid.split()
    card = []
    content = []
    for i in range(len(days)):
        card.append(calendar.month_name[int(months[i])])
        card.append(days[i])
        if TOD[i] == 'F':
            card.append('Off Peak')
        elif TOD[i] == 'M':
            card.append('Mid Peak')
        elif TOD[i] == 'N':
            card.append('On Peak')
        card.append(paid[i])
        content.append(card)
        card = []
    print(content)
    return content
    
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
        message = calendar.month_name[int(month)] + " " + day + ", " + time
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
        message = calendar.month_name[int(month)] + " " + day + ", " + time
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
        message = calendar.month_name[int(month)] + " " + day + ", " + time
        if len(session) == 2:
            session.append(message)
    return session
    
script, divs = graphEverything()
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
    resp = make_response(render_template('bookingPage.html',  form = form, title=title, session = sesh)) 
    resp.set_cookie('amount', '', expires=0) 
    now = datetime.datetime.now().hour
    if now >= 19 or now <= 7:
        resp.set_cookie('TOD', 'off')
        resp.set_cookie('chargeLevel', 'price_1P23JeKySml2ekNAp6UZ5DHq') 
    elif (now > 7 and now <= 11) or (now >= 17 and now < 19):
        resp.set_cookie('TOD', 'on')
        resp.set_cookie('chargeLevel', 'price_1P23JJKySml2ekNAeAp8XVRe')
    elif now > 11 or now < 17:
        resp.set_cookie('TOD', 'mid')
        resp.set_cookie('chargeLevel', 'price_1P23JUKySml2ekNAnLxJ79J4')
    if form.validate_on_submit():
        selected = (float)(request.form.get('duration'))
        resp = make_response(redirect(url_for('checkAvailbility')))
        if form.submit3.data == True:
            resp.set_cookie('amount', f'{math.trunc(12*selected)}')
        elif form.submit2.data == True: 
            resp.set_cookie('amount', f'{math.trunc(10*selected)}')
        elif form.submit1.data == True:
            resp.set_cookie('amount', f'{math.trunc(8*selected)}')
        resp.set_cookie('time', (str)(form.datum.data))
        resp.set_cookie('duration', (str)(selected))
        return resp
    return resp

@app.route('/checkAvailability', methods=['GET', 'POST'])
def checkAvailability():
    time = request.cookies.get('time').split(' ')
    startTime = datetime.datetime.strptime(time[1], '%H:%M:%S')
    duration = ((float)(request.cookies.get('duration'))) * 30
    endTime = (startTime + datetime.timedelta(minutes=duration))
    docMaster = colData.find({"date": time[0]})
    if docMaster == None:
        return redirect(url_for('confirmPage'))
    else:
        return redirect(url_for('confirmPage'))


@app.route('/confirmPage', methods=['GET', 'POST'])
def confirmPage():
    arr = []
    arr.append(request.cookies.get('amount'))
    arr.append(request.cookies.get('TOD'))
    arr.append(request.cookies.get('time'))
    title = "Confirm Order"
    if request.method == 'POST':
        return redirect(url_for('create_checkout_session'))
    return render_template('confirmPage.html', arr = arr, title = title)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashMain():
    title = "Dashboard"
    sesh = readSlots(request.cookies.get('personalID'))
    return render_template('dashMain.html', title=title, session = sesh, script = script, div = divs)

@app.route('/history', methods=['GET', 'POST'])
def historyPage():
    title = "History"
    cont = readHistory(request.cookies.get('personalID'))
    sesh = readSlots(request.cookies.get('personalID'))
    return render_template('historyPage.html', title = title, content = cont, session = sesh)

@app.route('/config')
def get_publishable_key():
    stripe_config = {"publicKey": stripeKeys["publishable_key"]}
    return jsonify(stripe_config)

@app.route('/success')
def paymentSuccess():
    time = request.cookies.get('time').split(' ')
    docMaster = colData.find_one({"_id": request.cookies.get('personalID')})
    doc = docMaster["booked"]
    slot1 = doc["slot1"]
    slot2 = doc["slot2"]
    slot3 = doc["slot3"]
    if slot1 == None:
        slot1['month'] = time.strftime("%B")
@app.route('/create-checkout-session', methods=['GET', 'POST'])
def create_checkout_session():
    domain_url = "http://127.0.0.1:5000/"
    stripe.api_key = stripeKeys["secret_key"]
    try:
        checkout_session = stripe.checkout.Session.create(
            success_url=domain_url + "success",
            cancel_url=domain_url + "dashboard",
            payment_method_types=["card"],
            mode="payment",
            line_items=[
                {
                    "price" : request.cookies.get('chargeLevel'),
                    "quantity" : request.cookies.get('amount')
                }
            ]

        )
        return jsonify({"sessionId": checkout_session["id"]})
    except Exception as e:
        return jsonify(error=str(e)), 403
    
if __name__ == '__main__':
    app.run(debug=True)