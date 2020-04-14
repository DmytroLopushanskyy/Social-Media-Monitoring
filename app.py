from flask import Flask, render_template, url_for, request, session, redirect
import pymongo
import bcrypt
import config
app = Flask(__name__)
app.secret_key = 'mysecret'
app.config['SECRET_KEY'] = config.secret_key
app.config['MONGO_DBNAME'] = config.mongoname

mongo = pymongo.MongoClient(
    config.mongoclient)


@app.route('/')
def index():
    if 'username' in session:
        return render_template('login')

    return render_template('index.html')


@app.route('/login', methods=['POST'])
def login():
    users = mongo.db.users
    login_user = users.find_one({'name': request.form['username']})

    if login_user:
        if bcrypt.hashpw(request.form['pass'].encode('utf-8'), login_user['password']) == login_user['password']:
            session['username'] = request.form['username']
            print("HERE")
            return redirect(url_for('index'))

    return 'Invalid username/password combination'


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'name': request.form['username']})

        if not existing_user:
            hashpass = bcrypt.hashpw(request.form['pass'].encode('utf-8'), bcrypt.gensalt())
            users.insert({'name': request.form['username'], 'password': hashpass})
            session['username'] = request.form['username']
            return redirect(url_for('index'))

        return 'That username already exists!'

    return render_template('register.html')


if __name__ == '__main__':
    app.run(debug=True)
