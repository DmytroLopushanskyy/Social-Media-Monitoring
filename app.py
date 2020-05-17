"""
Main module run it to run application
"""
import bcrypt
from flask import Flask, render_template, url_for, request, session, redirect, flash
from forms import LoginForm, RegistrationForm
import config
from classes.user import to_class
from db_connect import mongo
from classes.keyword import Keywords
from classes.user import User

app = Flask(__name__)
app.secret_key = config.flask_key
app.config['SECRET_KEY'] = config.secret_key
app.config['MONGO_DBNAME'] = config.mongoname


@app.route('/')
def index():
    """
    Home page
    :return: html
    """
    if 'user' in session:
        user = User(session['user'])
        data = {'username': session['user'], 'keywords': user.get_full_data(),
                'links_telegram': user.get_pretty_links('telegram'),
                'links_twitter': user.get_pretty_links('twitter')}
        print(data)
        return render_template('index.html', username=session['user'], data=data)
    flash("Create an account or login firstly", 'warning')
    return redirect(url_for('login'))


@app.route('/register', methods=['POST', 'GET'])
def register():
    """
    Register page
    :return: html
    """
    form = RegistrationForm()
    if form.validate_on_submit():
        users = mongo.db.users
        hashpass = bcrypt.hashpw(form.password.data.encode('utf-8'), bcrypt.gensalt())
        users.insert({'name': form.username.data,
                      'email': form.email.data, 'password': hashpass, 'keywords': [], 'links_twitter': [],
                      'links_telegram': []})
        session['user'] = form.username.data
        flash(f"Account created for {form.username.data}!", 'success')
        return redirect(url_for('index'))

    return render_template('main_register.html', title='Register', form=form)


@app.route('/login', methods=['POST', 'GET'])
def login():
    """
    Login Page
    :return: html
    """
    form = LoginForm()
    if form.validate_on_submit():
        users = mongo.db.users
        login_user = users.find_one({'name': form.username.data})

        if login_user:
            if bcrypt.hashpw(form.password.data.encode('utf-8'), login_user['password']) \
                    == login_user['password']:
                session['user'] = form.username.data
                flash(f"You have logged in as {form.username.data}!", 'success')
                return redirect(url_for('index'))
        flash('Incorrect password or/and username', 'danger')
    return render_template('main_login.html', title='Register', form=form)


@app.route('/add', methods=['POST'])
def add():
    """
    Add new keyword for user
    :return: redirect to Home page
    """
    if request.method == 'POST':
        user = to_class(session['user'])
        if request.form['keyword'] in user.keywords:
            flash("This word is already in your dictionary", 'danger')
        elif not ukrainian(request.form['keyword']):
            flash("This site only work with ukrainian words", 'danger')
        elif len(request.form['keyword'].split()) > 1:
            flash("Enter only one word!", 'danger')
        else:
            user.add_keyword(request.form['keyword'])
            flash("This word is added to your dictionary", 'success')
    return redirect(url_for('index'))


@app.route('/logout', methods=['POST'])
def logout():
    """
    Logout user
    :return: redirect to Login Page
    """
    if request.method == 'POST':
        del session['user']
    flash("You have logged out", "danger")
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True, port=5003)
