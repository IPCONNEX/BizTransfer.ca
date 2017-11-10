#! /Users/omarelmohri/.venvs/lpthw/bin/python
# sample for web app to display the database content

from pymongo import MongoClient
from flask import render_template, request, Flask, flash, redirect, url_for, session, logging
from random import randint
from wtforms import Form, StringField, TextAreaField, PasswordField, DecimalField, validators
from passlib.hash import sha256_crypt
from lib.BizTransfer import Enterprise
from flask_pymongo import PyMongo
import time
import json



client = MongoClient('ds243055.mlab.com', 43055)
db = client['biztransfer']
db.authenticate('mac', 'mac')
enterprisesDB = db['enterprises']
posts = db.enterprisesDB


class EnterpriseForm(Form):
    ent_name = StringField('Enterprise name', [validators.length(min=5, max= 50)])
    neq = DecimalField('NEQ')
    contact = StringField('Contact name', [validators.length(min=5, max= 50)])
    email = StringField('Email', [validators.length(min=6, max= 50)])
    phone = DecimalField('Phone')
    ebitda = DecimalField('EBITDA')


class UserForm(Form):
    username = StringField('Username')
    name = StringField('Full name')
    email = StringField('Email')
    phone = StringField('Phone')
    password = StringField('Password')

# THE APP

app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'biztransfer'
app.config['MONGO_URI'] = 'mongodb://mac:mac@ds243055.mlab.com:43055/biztransfer'
mongo = PyMongo(app)

@app.route("/", methods=["GET"])
def index():
    data = mongo.db.enterprises.find()
    return render_template('index.html', data=data)

@app.route("/ent/<string:id>/", methods=["GET"])
def ent(id):
    result = mongo.db.enterprises.find_one({"id":id})
    return render_template('entreprise.html', result=result, id=id)

@app.route("/add-biz/", methods=["GET", "POST"])
def addBiz():
    IdList = [0]  # this should be populated with all existing IDs
    while True:
        newId = str(randint(1, 999999)).rjust(6, '0')
        if newId not in IdList:
            break
    form = EnterpriseForm(request.form)

    if request.method == 'POST' and form.validate():
        if mongo.db.enterprises.find({'neq' : str(form.neq.data)}).count() > 0:
            flash("This company already exists", "danger")
            return render_template('addbiz.html', form=form, newId=newId)
        mongo.db.enterprises.insert({'id':newId, 'entr_name': form.ent_name.data, 'neq': str(form.neq.data),
            'contact': form.contact.data, 'email': form.email.data, 'phone': str(form.phone.data),
            'ebitda': int(str(form.ebitda.data))})
        flash("You successfully entered your enterprise", "success")
        return redirect(url_for('ent', id=newId))

    return render_template('addbiz.html', form=form, newId=newId)

@app.route("/login", methods=['POST', 'GET'])
def login():
    return render_template('login.html')

@app.route("/register/", methods=['POST', 'GET'])
def register():
    form = UserForm(request.form)

    if request.method == 'POST' and form.validate():
        if mongo.db.users.find({'username': form.username.data}).count() > 0:
            flash("Username already exists", "danger")
            return render_template('register.html', form=form, newId=newId)
        if mongo.db.users.find({'email': form.email.data}).count() > 0:
            flash("Email already in use", "danger")
            return render_template('register.html')

        mongo.db.users.insert({'name': form.name.data, 'username': form.username.data, 'email': form.email.data,
                                     'phone': form.phone.data, 'password': form.password.data})
        flash("Your account has been created successfully", "success")
        return redirect(url_for('login'))
        # existingUser = mongo.db.users.find_one({'name' : request.form['username']})

        # if not existingUser:
        #    hashpass = bcrypt.hashpw(request.form['password'])
    return render_template('register.html', form=form)

if __name__ == '__main__':
    app.secret_key = "secr3tkey"
    app.run(debug=True, host='0.0.0.0', port=5000)
