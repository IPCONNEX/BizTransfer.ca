#! /Users/omarelmohri/.venvs/lpthw/bin/python
# sample for web app to display the database content

from pymongo import MongoClient
from flask import render_template, request, Flask, flash, redirect, url_for, session, logging
from random import randint
from wtforms import Form, StringField, TextAreaField, PasswordField, DecimalField, validators
from passlib.hash import sha256_crypt
from lib.BizTransfer import Enterprise
from flask_pymongo import PyMongo



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

# THE APP

app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'biztransfer'
app.config['MONGO_URI'] = 'mongodb://mac:mac@ds243055.mlab.com:43055/biztransfer'

@app.route("/", methods=["GET"])
def index():
    data = []
    for post in enterprisesDB.find():
        data.append(post)
    return render_template('index.html', data=data)

@app.route("/ent/<string:id>", methods=["GET"])
def entProfile(id):
    result = enterprisesDB.find_one({"id":id})
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
        newEnt = {}
        print("STEP REACHED")
        newEnt['entr_name'] = form.ent_name.data
        newEnt['neq'] = str(form.neq.data)
        newEnt['contact'] = form.contact.data
        newEnt['email'] = form.email.data
        newEnt['phone'] = str(form.phone.data)
        newEnt['ebitda'] = int(str(form.ebitda.data))
        enterprisesDB.insert_one(newEnt).inserted_id
        flash("You successfuly entered your enterprise", "success")
        redirect(url_for('/ent/' + newId))
    return render_template('addbiz.html', form=form, newId=newId)



if __name__ == '__main__':
    app.secret_key = "secr3tkey"
    app.run(debug=True, host='0.0.0.0', port=5000)
