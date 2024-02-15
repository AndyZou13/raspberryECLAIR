from flask import Flask, render_template, url_for, redirect, flash
from forms import RegistrationForm, LoginForm

app = Flask(__name__)

app.config['SECRET_KEY'] = '163c1af8b4a801e8fddec7e72b6db4dd'

global username

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def loginPage():
    form = LoginForm()
    title = "Login"
    if form.validate_on_submit():
        global username 
        username = form.username.data
        flash(f'Logged in as {form.username.data}', 'Success')
        return redirect(url_for('profilePage'))
    return render_template('login.html', form = form, title=title)

@app.route('/register', methods=['GET', 'POST'])
def registerPage():
    form = RegistrationForm()
    title = "Register"
    if form.validate_on_submit():
        global username 
        username = form.username.data
        flash(f'Account created for {form.username.data}', 'Success')
        return redirect(url_for('profilePage'))
    return render_template('register.html', form = form, title=title)

@app.route('/profile')
def profilePage():
    return render_template('profile.html', name = username)

if __name__ == '__main__':
    app.run(debug=True)