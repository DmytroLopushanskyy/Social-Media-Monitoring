# coding=utf8
"""
Main module run it end run application
"""
import bcrypt
from flask import Flask, render_template, url_for, request, session, redirect, flash
from forms import LoginForm, RegistrationForm
import config
from db_connect import mongo
from classes.user import to_class, User
from classes.keyword import ukrainian

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
        try:
            user = User(session['user'])
        except NameError:
            return redirect(url_for('login'))
        data = {'username': session['user'], 'keywords': user.get_full_data(),
                'telegram_links': user.get_pretty_links('telegram'),
                'twitter_links': user.get_pretty_links('twitter')}
        return render_template('index.html', username=session['user'], data=data)
    return redirect(url_for('login'))


@app.route('/register', methods=['POST', 'GET'])
def register():
    """
    Register page
    :return: html
    """
    form = RegistrationForm()
    print()
    if form.validate_on_submit():
        users = mongo.db.users
        hashpass = bcrypt.hashpw(form.password.data.encode('utf-8'), bcrypt.gensalt())

        users.insert({'name': form.username.data,
                      'email': form.email.data, 'password': hashpass,
                      'keywords': [], 'links_twitter': [],
                      'links_telegram': []})
        session['user'] = form.username.data
        print(session['user'])
        return redirect(url_for('index'))
    if request.method == 'POST':
        flash("Невдалось стоворити користувача,\n перевірте чи усі дані введено коректно", 'danger')

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
        login_user = users.find_one({'email': form.email.data})

        if login_user:
            if bcrypt.hashpw(form.password.data.encode('utf-8'), login_user['password']) \
                    == login_user['password']:
                session['user'] = login_user['name']
                return redirect(url_for('index'))
        flash("Неправильна пошта або пароль!", 'danger')
    elif not form.validate_on_submit() and request.method == 'POST':
        flash("Неправильна пошта або пароль!", 'danger')
    return render_template('main_login.html', title='Register', form=form)


@app.route('/add', methods=['POST'])
def add():
    """
    Add new keyword for user
    :return: redirect end Home page
    """
    if request.method == 'POST':
        user = to_class(session['user'])
        if request.form['keyword'] in user.keywords:
            flash("Це слово уже є у вашому словнику", 'danger')
        elif len(request.form['keyword'].split()) > 1:
            flash("Введіть рівно одне слово!", 'danger')
        elif not ukrainian(request.form['keyword']):
            flash("Цей сайт працює тільки з українськими словами", 'danger')
        else:
            user.add_keyword(request.form['keyword'])
            flash("Це слово додано у ваш словник", 'success')
    return redirect(url_for('index'))


@app.route('/logout', methods=['POST'])
def logout():
    """
    Logout user
    :return: redirect end Login Page
    """
    if request.method == 'POST':
        del session['user']
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run()
