from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, IntegerField, PasswordField
from wtforms.validators import DataRequired, EqualTo, Length

class AliasForm(FlaskForm):
    source_username = StringField('Alias', validators=[DataRequired()])
    source_domain = StringField('Domain', validators=[DataRequired()])
    destination_username = StringField('Ziel-Adresse', validators=[DataRequired()])
    destination_domain = StringField('Ziel-Domain', validators=[DataRequired()])
    enabled = BooleanField('Aktiv?')
    blocked = BooleanField('Blockiert?')

class AccountForm(FlaskForm):
    username = StringField('Benutzername', validators=[DataRequired()])
    domain = StringField('Domain', validators=[DataRequired()])
    quota = IntegerField('Quota in Megabyte', validators=[DataRequired()])
    enabled = BooleanField('Aktiv?')
    sendonly = BooleanField('Nur senden?')

class PasswordForm(FlaskForm):
    password = PasswordField('Passwort', [
        Length(min=10, max=30, message='10-30 Zeichen')
    ])
    confirm_password = PasswordField('Passwort wiederholen', [
        EqualTo('password', message='Passwörter stimmen nicht ueberein!')
    ])

class CreateAccountForm(AccountForm, PasswordForm):
    pass

class CheckPasswordForm(FlaskForm):
    password = PasswordField('Passwort', validators=[ DataRequired() ])

def get_catchall_form(domain):
    form = AliasForm()
    form.source_username.validators = []
    form.source_username.data = None
    form.blocked.data = False
    form.source_domain.data = domain.domain
    form.destination_domain.data = domain.domain
    return form
