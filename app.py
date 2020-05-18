# coding=utf8
"""
Main module run it to run application
"""
import bcrypt
from flask import Flask, render_template, url_for, request, session, redirect, flash
from forms import LoginForm, RegistrationForm
import config
from classes.user import to_class
from db_connect import mongo
from classes.keyword import ukrainian
from classes.keyword import Keywords

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
        print(session['user'])
        data = {'username': 'BohdanVey11', 'keywords': {
            'корона': {'telegram_views': [0, 0, 1, 3, 3, 1, 5],
                       'telegram_reaction': [0, 0, 1, 3, 3, 1, 5],
                       'telegram_posts': [0, 0, 1, 3, 3, 1, 5],
                       'twitter_replies': [20, 20, 14, 24, 24, 15, 22],
                       'twitter_likes': [20, 20, 14, 24, 24, 15, 22],
                       'twitter_retweets': [5, 5, 2, 7, 7, 2, 11],
                       'twitter_posts': [0, 0, 1, 3, 3, 1, 5]}, 'коронавірус': {
                'telegram_views': [1188, 1188, 1183, 1031, 1352, 1347, 1060],
                'telegram_reaction': [0, 0, 0, 1, 3, 3, 1],
                'telegram_posts': [2, 2, 2, 2, 7, 7, 2],
                'twitter_replies': [20, 20, 20, 14, 24, 24, 15],
                'twitter_likes': [20, 20, 20, 14, 24, 24, 15],
                'twitter_retweets': [5, 5, 5, 2, 7, 7, 2],
                'twitter_posts': [0, 0, 0, 1, 3, 3, 1]}}, 'links_telegram': [
            ['https://t.me/bbc_ukr/16636',
             'Коронавірус в Україні: кількість нових хворих зростає четвертий день поспіль\nСтаном на 16 травня в Україні зареєстрували 17 858 випадків COVID-19. За добу зафіксували 528 нових хворих.\n\nhttp://www.bbc.com/ukrainian/news-52684024',
             0, '678'], ['https://t.me/Koronavirus_info_moz/341',
                         '⚡МОЗ повідомляє:\n\nВ Україні зафіксовано 17858 випадків коронавірусної хвороби COVID-19\n\nЗа даними ЦГЗ, станом на 9:00 16 травня в Україні 17858 лабораторно підтверджених випадків COVID-19, з них 497 летальних, 4906 пацієнтів одужало. За добу зафіксовано 528 нових випадків.\n\nНаразі коронавірусна хвороба виявлена:\n\nВінницька область — 700 випадків;\nВолинська область — 599 випадків;\nДніпропетровська область — 806 випадків;\nДонецька область — 121 випадок;\nЖитомирська область — 540 випадків;\nЗакарпатська область — 858 випадків;\nЗапорізька область — 365 випадків;\nІвано-Франківська область — 1200 випадків;\nКіровоградська область — 441 випадок;\nм. Київ — 2221 випадок;\nКиївська область — 1143 випадки;\nЛьвівська область — 969 випадків;\nЛуганська область — 42 випадки;\nМиколаївська область — 236 випадків;\nОдеська область — 734 випадки;\nПолтавська область — 263 випадки;\nРівненська область — 1104 випадки;\nСумська область — 161 випадок;\nТернопільська область — 1065 випадків;\nХарківська область — 773 випадки;\nХерсонська область — 167 випадків;\nХмельницька область — 235 випадків;\nЧернівецька область — 2647 випадків;\nЧеркаська область — 363 випадки;\nЧернігівська область — 105 випадків.\n\nДані з тимчасово окупованих територій АР Крим, Донецької, Луганської областей та міста Севастополя відсутні.\n\nДослідження проводилися вірусологічною референс-лабораторією Центру громадського здоров’я України, а також обласними лабораторіями. Станом на ранок 16 травня 2020 року до Центру надійшло 1196 повідомлень про підозру на COVID-19. Всього з початку 2020 року надійшло 45038 повідомлень про підозру на COVID-19.\n\n🔴НАГАДУЄМО!🔴\n✅Отримати кредит ПІД 0,01% можна тут — MONEYGO.PP.UA',
                         0, '510']], 'links_twitter': [
            ['https://twitter.com/FCBarcelona/status/1250023822239191043',
             'Some text', 5, 10, 25],
            ['https://twitter.com/prisonpsg/status/1206949629964763142',
             'Another text', 15, 110, 215]]}
        data = {'username': 'BohdanVey11', 'keywords': {
            'корона': {'telegram_views': [0, 0, 1, 3, 3, 1, 5],
                       'telegram_reaction': [0, 0, 1, 3, 3, 1, 5],
                       'telegram_posts': [0, 0, 1, 3, 3, 1, 5],
                       'twitter_replies': [20, 20, 14, 24, 24, 15, 22],
                       'twitter_likes': [20, 20, 14, 24, 24, 15, 22],
                       'twitter_retweets': [5, 5, 2, 7, 7, 2, 11],
                       'twitter_posts': [0, 0, 1, 3, 3, 1, 5]}, 'коронавірус': {}}}
        #data = {'username': 'BohdanVey11', 'keywords': {}}
        return render_template('index.html', data=data)
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
    app.run(debug=True, port=5005)
