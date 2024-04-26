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
import pandas as pd
import hashlib
from datetime import datetime as dt
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import DatetimeTickFormatter, HoverTool
app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['MONGODB_URI'] = os.environ.get('MONGODB_URI')

stripeKeys = {
    "secret_key": os.environ.get('STRIPE_SECRET'),
    "publishable_key": os.environ.get('STRIPE_PUBLIC')
}

client = MongoClient(os.environ.get('MONGODB_URI'))
baseURL = "https://raspberryeclair.azurewebsites.net/"

# app.config['SECRET_KEY'] = "163c1af8b4a801e8fddec7e72b6db4dd"
# stripeKeys = {
#     "secret_key": 'sk_test_51Ou2ppKySml2ekNAVRVYHbeAiiAx9FR48HW0ZG3Ppx1NvZIBzEhnvnmhEfCWZCWwYMOLphXpClfwNiBLfV8IA4Mp00uISbXiHj',
#     "publishable_key": 'pk_test_51Ou2ppKySml2ekNAvQ4TTTCUmCeZ4NDYqIZHFqtHrLYGp5rBGDrHZC3yjkejgqYwgnikhxeZ56hQuI5PfmZsDwN200QH7y4PJQ'
# }
# client = MongoClient("mongodb+srv://public:public@tmu.vgmkgse.mongodb.net/?retryWrites=true&w=majority&appName=TMU")
# baseURL = "http://127.0.0.1:8000/"

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)
    
db = client["raspberryECLAIR"]
colUsers = db["users"]
colData = db["data"]
colCal = db["calendar"]
colDataModel = db['dataModels']
colChargeValues = db['charge-values']

def graphData(id):
    docMaster = colData.find_one({"_id": ObjectId(id)})
    hist = docMaster['history']
    months = hist['month'].split(' ')
    days = hist['day'].split(' ')
    if hist['month'] == "":
        return None, None
    x = []
    for i in range(len(months)):
        x.append(dt(2024, int(months[i]), int(days[i])))
    y1 = hist['pricePKW'].split(' ')
    for i in range(len(y1)):
        y1[i] = int(y1[i])
    y2 = hist['recentCharges'].split(' ')
    for i in range(len(y2)):
        y2[i] = int(y2[i])
    xLabels1 = []
    for i in range(len(x)):
        xLabels1.append(x[i].strftime('%Y-%m-%d') + ' | ' + str(y1[i]) + 'cents')
    xLabels2 = []
    for i in range(len(x)):
        xLabels2.append(x[i].strftime('%Y-%m-%d') + ' | ' + str(y2[i]) + 'kWh')
    df1 = pd.DataFrame({'x': x, 
                     'y': y1,
                     'labels': xLabels1})
    df2 = pd.DataFrame({'x': x, 
                     'y': y2,
                     'labels': xLabels2})
    p1 = figure(sizing_mode='stretch_height', x_axis_type="datetime", title='Recently Charged Prices in Cents')
    p1.line(x = 'x', y = 'y', source = df1)
    p1.scatter(x = 'x', y = 'y', source = df1)
    p1.xaxis.formatter=DatetimeTickFormatter(
        hours=["%d %B %Y"],
        days=["%d %B %Y"],
        months=["%d %B %Y"],
        years=["%d %B %Y"],
    )
    p1.yaxis.axis_label = "price per kWh (cents)"
    p1.xaxis.major_label_orientation = math.pi/4
    p1.toolbar.logo = None
    p1.toolbar_location = None
    hover = HoverTool(tooltips=[('Label', '@labels')]) 
    p1.add_tools(hover)
    
    p2 = figure(sizing_mode='stretch_height', x_axis_type="datetime", title='Recently Charged in Kilowatts')
    p2.line(x = 'x', y = 'y', source = df2)
    p2.scatter(x = 'x', y = 'y', source = df2)
    p2.xaxis.formatter=DatetimeTickFormatter(
        hours=["%d %B %Y"],
        days=["%d %B %Y"],
        months=["%d %B %Y"],
        years=["%d %B %Y"],
    )
    p2.yaxis.axis_label = "Kilowatt per hour"
    p2.xaxis.major_label_orientation = math.pi/4
    p2.toolbar.logo = None
    p2.toolbar_location = None
    hover = HoverTool(tooltips=[('Label', '@labels')]) 
    p2.add_tools(hover)

    y3 = []
    for x in colChargeValues.find():
        y3.append(int(x['data']))
    y3.reverse()
    x = []
    xLabels3 = []
    for i in range(1, len(y3) + 1):
        x.append(i)
        xLabels3.append(f'{i} minutes ago, {y3[i-1]}kWh')
    df3 = pd.DataFrame({'x': x, 
                     'y': y3,
                     'labels': xLabels3})
    p3 = figure(sizing_mode='stretch_both', x_axis_type="datetime", title='Current Charging in Kilowatts')
    p3.line(x = 'x', y = 'y', source = df3)
    p3.scatter(x = 'x', y = 'y', source = df3)
    p3.yaxis.axis_label = "Kilowatt per hour"
    p3.xaxis.major_label_orientation = math.pi/4
    p3.toolbar.logo = None
    p3.toolbar_location = None
    hover = HoverTool(tooltips=[('Label', '@labels')]) 
    p3.add_tools(hover)

    plots = {'pricePKW': p1, 'recentCharges': p2, 'currentCharging': p3}

    script, div = components(plots)
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
        message = calendar.month_name[int(month)] + " " + day + ", " + time
        if len(session) == 0:
            session.append(message)
    if slot2["month"] != "":
        month = slot2["month"]
        day = slot2["day"]
        time = slot2["time"]
        message = calendar.month_name[int(month)] + " " + day + ", " + time
        if len(session) == 1:
            session.append(message)
    if slot3["month"] != "":
        month = slot3["month"]
        day = slot3["day"]
        time = slot3["time"]
        message = calendar.month_name[int(month)] + " " + day + ", " + time
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
        
        query = {"username" : hashlib.sha256(form.username.data.encode('utf-8')).hexdigest()}
        doc = colUsers.find_one(query)
        if doc:
            p=doc["password"]
            if hashlib.sha256(form.password.data.encode('utf-8')).hexdigest() == p:
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
        query = {"username" : hashlib.sha256(form.username.data.encode('utf-8')).hexdigest()}
        doc = colUsers.find_one(query)
        if doc:
            return render_template('register.html', form = form, title=title)
        else :
            doc = {"username" : hashlib.sha256(form.username.data.encode('utf-8')).hexdigest(), "password" : hashlib.sha256(form.password.data.encode('utf-8')).hexdigest()}
            x = colUsers.insert_one(doc)
            fileData = colDataModel.find_one({"_id": ObjectId('66182294f166bef419e850df')})
            print(fileData)
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
        resp = make_response(redirect(url_for('checkAvailability')))
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
    time = request.cookies.get('time')
    startTime = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
    duration = ((float)(request.cookies.get('duration'))) * 60
    endTime = (startTime + datetime.timedelta(minutes=duration))
    print('start', startTime)
    print('end',endTime)
    docMaster = colCal.find({"date": time.split(' ')[0]})
    for i in docMaster:
        timeDif = startTime > datetime.datetime.strptime(i['date'] + " " +i['startTime'], '%Y-%m-%d %H:%M:%S')
        if timeDif == True:
            timeDif = startTime < datetime.datetime.strptime(i['date'] + " " +i['endTime'], '%Y-%m-%d %H:%M:%S')
            if timeDif == True:
                return redirect(url_for('failedBooking'))
        timeDif = endTime > datetime.datetime.strptime(i['date'] + " " +i['startTime'], '%Y-%m-%d %H:%M:%S')
        if timeDif == True:
            timeDif = endTime < datetime.datetime.strptime(i['date'] + " " +i['endTime'], '%Y-%m-%d %H:%M:%S')
            if timeDif == True:
                return redirect(url_for('failedBooking'))
    docMaster = colData.find_one({"_id": ObjectId(request.cookies.get('personalID'))})
    doc = docMaster["booked"]
    slot1 = doc["slot1"]
    slot2 = doc["slot2"]
    slot3 = doc["slot3"]
    if slot1["month"] != "" and slot2["month"] != "" and slot3["month"] != "":
        return redirect(url_for('failedBooking'))
    return redirect(url_for('confirmPage'))

@app.route('/failedBooking', methods=['GET', 'POST'])
def failedBooking():
    title = "Booking Failed"
    if request.method == 'POST':
        return redirect(url_for('bookingPage'))
    return render_template('failedBooking.html', title = title)

@app.route('/confirmPage', methods=['GET', 'POST'])
def confirmPage():
    arr = []
    arr.append(request.cookies.get('amount'))
    arr.append(request.cookies.get('TOD'))
    arr.append(request.cookies.get('time'))
    title = "Confirm Order"
    if request.method == 'POST':
        submitted_value = request.form['submit']
        if submitted_value == 'Confirm Order':
            return redirect(url_for('create_checkout_session'))
        elif submitted_value == 'Back to Dashboard':
            return redirect(url_for('dashMain'))
    return render_template('confirmPage.html', arr = arr, title = title)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashMain():
    title = "Dashboard"
    sesh = readSlots(request.cookies.get('personalID'))
    script, divs = graphData(request.cookies.get('personalID'))
    return render_template('dashMain.html', title=title, session = sesh, script = script, div = divs)

@app.route('/history', methods=['GET', 'POST'])
def historyPage():
    title = "History"
    cont = readHistory(request.cookies.get('personalID'))
    sesh = readSlots(request.cookies.get('personalID'))
    return render_template('historyPage.html', title = title, content = cont, session = sesh)

@app.route('/config', methods=['GET', 'POST'])
def get_publishable_key():
    stripe_config = {"publicKey": stripeKeys["publishable_key"]}
    return jsonify(stripe_config)

@app.route('/success')
def paymentSuccess():
    time = request.cookies.get('time')
    startTime = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
    duration = ((float)(request.cookies.get('duration'))) * 60
    endTime = (startTime + datetime.timedelta(minutes=duration))
    date = startTime.strftime("%Y-%m-%d")
    docMaster = colData.find_one({"_id": ObjectId(request.cookies.get('personalID'))})
    doc = docMaster["booked"]
    slot1 = doc["slot1"]
    slot2 = doc["slot2"]
    slot3 = doc["slot3"]
    if slot1["month"] == "":
        slot1["month"] = startTime.strftime("%m")
        slot1["day"] = startTime.strftime("%d")
        slot1["time"] = startTime.strftime("%H:%M:%S")
        print('saved', startTime.strftime("%m"), startTime.strftime("%d"), startTime.strftime("%H:%M:%S"))
    elif slot2["month"] == "":
        slot2["month"] = startTime.strftime("%m")
        slot2["day"] = startTime.strftime("%d")
        slot2["time"] = startTime.strftime("%H:%M:%S")
    elif slot3["month"] == "":
        slot3["month"] = startTime.strftime("%m")
        slot3["day"] = startTime.strftime("%d")
        slot3["time"] = startTime.strftime("%H:%M:%S")
    doc["slot1"] = slot1
    doc["slot2"] = slot2
    doc["slot3"] = slot3
    docMaster["booked"] = doc
    newVal = { "$set" : docMaster}
    colData.update_one({"_id": ObjectId(request.cookies.get('personalID'))}, newVal)
    doc = {'date': date, 'startTime': startTime.strftime("%H:%M:%S"), 'endTime': endTime.strftime("%H:%M:%S")}
    colCal.insert_one(doc)
    return redirect(url_for('dashMain'))

@app.route('/create-checkout-session', methods=['GET', 'POST'])
def create_checkout_session():
    domain_url = baseURL
    stripe.api_key = stripeKeys["secret_key"]
    try:
        checkout_session = stripe.checkout.Session.create(
            success_url=domain_url + "success",
            cancel_url=domain_url + "failedBooking",
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