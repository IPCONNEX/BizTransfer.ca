from wtforms import Form, StringField, TextAreaField, PasswordField, DecimalField, validators

class EnterpriseForm(Form):
    ent_name = StringField('')
    neq = DecimalField('')
    contact = StringField('')
    email = StringField('')
    phone = StringField('')
    ebitda = DecimalField('')


class UserForm(Form):
    username = StringField('Username')  #  [validators.length(min=5, max= 50)
    name = StringField('Full name')
    email = StringField('Email')
    phone = StringField('Phone')
    password = PasswordField('Password', [validators.DataRequired(), validators.EqualTo('confirm', message='Passwords do not match')])
    confirm = PasswordField('Confirm Password')

class LoginForm(Form):
    username = StringField('Username')  #  [validators.length(min=5, max= 50)
    password = PasswordField('Password', [validators.DataRequired()])