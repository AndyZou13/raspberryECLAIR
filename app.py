from flask import Flask, render_template, url_for, request
from forms import RegistrationForm, LoginForm

app = Flask(__name__)

app.config['SECRET_KEY'] = '163c1af8b4a801e8fddec7e72b6db4dd'

username = "Andy"

@app.route('/')
@app.route('/login')
def loginPage():
    form = LoginForm()
    return render_template('login.html', form = form)

@app.route('/register')
def registerPage():
    form = RegistrationForm()
    return render_template('register.html', form = form)

@app.route('/profile')
def profilePage():
    return render_template('profile.html', name = username)

if __name__ == '__main__':
    app.run(debug=True)