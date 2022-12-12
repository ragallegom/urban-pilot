from wtforms import Form, StringField, PasswordField, validators

class RegistrationUser(Form):
    first_name = StringField('First Name', [
        validators.DataRequired(),
        validators.Length(min=3, max=25),
    ])
    middle_name = StringField('Middle Name', [
        validators.Optional(),
        validators.Length(min=3, max=25)
    ])
    last_name = StringField('Last Name', [
        validators.DataRequired(),
        validators.Length(min=3, max=50)
    ])
    username = StringField('Username', [
        validators.DataRequired(),
        validators.Length(min=4, max=25)
    ])
    email = StringField('Email Address', [
        validators.DataRequired(),
        validators.Email(),
        validators.Length(min=6, max=35),
    ])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    zip_code = StringField('Zip Code', [validators.Length(min=5, max=25)])