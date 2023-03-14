from flask_ldap3_login import LDAP3LoginManager
from flask_login import LoginManager, login_user, UserMixin, current_user
from flask import render_template, redirect, flash, url_for, request
from flask_ldap3_login.forms import LDAPLoginForm

from . import app
from .util import is_safe_url

login_manager = LoginManager(app)              # Setup a Flask-Login Manager
login_manager.login_view = 'login'
login_manager.login_message = 'Bitte einloggen, um diese Seite sehen zu können!'
ldap_manager = LDAP3LoginManager(app)          # Setup a LDAP3 Login Manager.

# Create a dictionary to store the users in when they authenticate
# This example stores users in memory.
users = {}

# Declare an Object Model for the user, and make it comply with the
# flask-login UserMixin mixin.
class User(UserMixin):
    def __init__(self, dn, username, data, groups):
        self.dn = dn
        self.username = username
        self.data = data
        self.groups = groups

    def __repr__(self):
        return self.dn

    def get_id(self):
        return self.dn

    def get_cn(self):
        return self.data['cn']
    
    def is_in_group(self, group_name):
        return any(group['cn'] == group_name for group in self.groups)


# Declare a User Loader for Flask-Login.
# Simply returns the User if it exists in our 'database', otherwise
# returns None.
@login_manager.user_loader
def load_user(id):
    if id in users:
        return users[id]
    return None

# Declare The User Saver for Flask-Ldap3-Login
# This method is called whenever a LDAPLoginForm() successfully validates.
# Here you have to save the user, and return it so it can be used in the
# login controller.
@ldap_manager.save_user
def save_user(dn, username, data, memberships):
    user = User(dn, username, data, memberships)
    users[dn] = user
    return user

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Instantiate a LDAPLoginForm which has a validator to check if the user
    # exists in LDAP.
    form = LDAPLoginForm()

    if form.validate_on_submit():
        if 'MAILADMIN_GROUP' in app.config and app.config['MAILADMIN_GROUP'] \
            and not form.user.is_in_group(app.config['MAILADMIN_GROUP']):
                flash('Leider fehlt dir die Berechtigung zur Mailverwaltung!')
        else:
            login_user(form.user)  # Tell flask-login to log them in.
            next = request.args.get('next')
            if next and is_safe_url(next):
                return redirect(next)
            return redirect(url_for('start'))  # Send them home
    elif request.method == 'POST':
        flash('Fehler beim Einloggen, Benutzername/Passwort falsch?', 'danger')
    return render_template('login.html', form=form)