from flask import Flask, render_template, url_for, redirect, flash
from forms import RegistrationForm, LoginForm
from pymongo import MongoClient
from pymongo.server_api import ServerApi

app = Flask(__name__)

app.config['SECRET_KEY'] = '163c1af8b4a801e8fddec7e72b6db4dd'
app.config['MONGODB_URI'] = "mongodb+srv://public:public@tmu.vgmkgse.mongodb.net/?retryWrites=true&w=majority"

client = MongoClient(app.config.get('MONGODB_URI'), server_api=ServerApi('1'))
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)
    
db = client["public-charger"]
colUsers = db["users"]
colData = db["data"]

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def loginPage():
    form = LoginForm()
    title = "Login"
    if form.validate_on_submit():
        query = {"username" : form.username.data}
        doc = colUsers.find_one(query)
        if doc:
            p=doc["password"]
            if form.password.data == p:
                global username 
                username = form.username.data
                return redirect(url_for('profilePage'))
    return render_template('login.html', form = form, title=title)

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
            global username 
            username = form.username.data
            doc = {"username" : form.username.data, "password" : form.password.data}
            x = colUsers.insert_one(doc)
            doc = {"_id" : x.inserted_id}
            colData.insert_one(doc)
            return redirect(url_for('profilePage'))
    return render_template('register.html', form = form, title=title)

@app.route('/profile')
def profilePage():
    return render_template('profile.html', name = username)

if __name__ == '__main__':
    app.run(debug=True)