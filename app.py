#! /Users/omarelmohri/.venvs/lpthw/bin/python
# sample for web app to display the database content

from lib.AppForms import EnterpriseForm, UserForm, LoginForm
from pymongo import MongoClient
from flask import render_template, request, Flask, flash, redirect, url_for, session, logging
from random import randint

from passlib.hash import sha256_crypt
#  from lib.BizTransfer import Enterprise, #  is_logged_in
from flask_pymongo import PyMongo
from functools import wraps
import time

client = MongoClient('ds243055.mlab.com', 43055)
db = client['biztransfer']
db.authenticate('mac', 'mac')
enterprisesDB = db['enterprises']
posts = db.enterprisesDB

# THE APP

app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'biztransfer'
app.config['MONGO_URI'] = 'mongodb://mac:mac@ds243055.mlab.com:43055/biztransfer'
mongo = PyMongo(app)


@app.route("/", methods=["GET"])
def index():
    data = mongo.db.enterprises.find()
    return render_template('index.html', data=data)


@app.route("/ent/<string:id>/", methods=["GET", 'POST'])
def ent(id):
    result = mongo.db.enterprises.find_one({"id": id})
    return render_template('entreprise.html', result=result, id=id)


def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged' in session:
            return f(*args, **kwargs)
        else:
            flash ("You are not authorized, Please login", 'danger')
            return redirect(url_for('login'))
    return wrap


@app.route("/dashboard/", methods=['GET'])
@is_logged_in
def dashboard():
    myEnter = mongo.db.enterprises.find({'owner': session['username']})
    return render_template('dashboard.html', myEnter=myEnter)

@app.route("/add-biz/", methods=["GET", "POST"])
@is_logged_in
def addBiz():
    IdList = [0]  # this should be populated with all existing IDs
    while True:
        newId = str(randint(1, 999999)).rjust(6, '0')
        if newId not in IdList:
            break
    form = EnterpriseForm(request.form)

    if request.method == 'POST' and form.validate():
        if mongo.db.enterprises.find({'neq': str(form.neq.data)}).count() > 0:
            flash("This company already exists", "danger")
            return render_template('addbiz.html', form=form, newId=newId)
        mongo.db.enterprises.insert({'id': newId, 'entr_name': form.ent_name.data, 'neq': str(form.neq.data),
                                     'contact': form.contact.data, 'email': form.email.data,
                                     'phone': str(form.phone.data),
                                     'ebitda': int(str(form.ebitda.data)), 'owner':session['username']})
        flash("You successfully entered your enterprise", "success")
        return redirect(url_for('ent', id=newId))

    return render_template('addbiz.html', form=form, newId=newId)


@app.route("/login/", methods=['POST', 'GET'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST':
        newUser = form.username.data
        newPass = form.password.data

        if mongo.db.users.find_one({'username': newUser}):
            hashPass = mongo.db.users.find_one({'username': newUser})['password']
            if sha256_crypt.verify(newPass, hashPass):
                session['logged'] = True
                session['username'] = newUser
                session['name'] = mongo.db.users.find_one({'username': newUser})['name']
                flash("Login successful", "success")
                return redirect(url_for('dashboard'))
        else:
            flash("Wrong combination username/password", "danger")

    return render_template('login.html', form=form)

@app.route("/logout/", methods=['GET'])
def logout():
    session.clear()
    flash('Successfully logged out of your session', "info")
    return redirect(url_for('index'))

@app.route("/signup/", methods=['POST', 'GET'])
def sigup():
    form = UserForm(request.form)

    if request.method == 'POST' and form.validate():
        newUser = form.username.data
        newEmail = form.email.data
        if mongo.db.users.find({'username': newUser}).count() > 0:
            flash("Username already exists", "danger")
            return render_template('signup.html', form=form)
        if mongo.db.users.find({'email': newEmail}).count() > 0:
            flash("Email already in use", "danger")
            return render_template('signup.html', form=form)
        hashPassword = sha256_crypt.encrypt(str(form.password.data)).encode()

        mongo.db.users.insert({'name': form.name.data, 'username': newUser, 'email': newEmail,
                               'phone': form.phone.data, 'password': hashPassword})
        flash("Your account has been created successfully, you can login now", "success")
        return redirect(url_for('login', form=form))

    return render_template('signup.html', form=form)


if __name__ == '__main__':
    app.secret_key = "secr3tkey"
    app.run(debug=True, host='0.0.0.0', port=5000)
