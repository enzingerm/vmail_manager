from flask import render_template, redirect, url_for, request, flash
from flask_login import login_required

from .forms import AliasForm, get_catchall_form, AccountForm, PasswordForm, CheckPasswordForm, CreateAccountForm
from .hashes import check_pw, create_hash
from .models import Domain, Alias, Account

from . import app, db

@app.route('/')
@login_required
def start():
	return render_template('start.html')

@app.route('/domain/<domain>')
@login_required
def edit_domain(domain):
	domain = db.get_or_404(Domain, domain)
	catchall = Alias.get_catchall(domain)
	aliases = db.session.execute(
		db.select(Alias)
			.filter_by(source_domain=domain.domain)
			.filter(Alias.source_username.isnot(None))
			.order_by(Alias.source_username)
	).scalars()
	accounts = db.session.execute(
		db.select(Account)
			.filter_by(domain=domain.domain)
			.order_by(Account.username)
	).scalars()
	return render_template('edit_domain.html', domain=domain, catchall=catchall, aliases=aliases, accounts=accounts)

@app.route('/domain/<domain>/edit_catchall', methods=['GET', 'POST'])
@login_required
def edit_catchall(domain):
	domain = db.get_or_404(Domain, domain)
	catchall = Alias.get_catchall(domain)
	if catchall is None:
		return redirect(url_for('edit_domain', domain=domain.id))
	form = get_catchall_form(domain)
	if form.validate_on_submit():
		form.populate_obj(catchall)
		db.session.commit()
		flash('Catchall erfolgreich gespeichert!', 'success')
		return redirect(url_for('edit_domain', domain=domain.id))
	elif request.method == 'POST':
		flash('Fehler beim Speichern des Catchall!', 'danger')
	form.destination_username.data = catchall.destination_username
	form.enabled.data = catchall.enabled
	return render_template('edit_catchall.html', domain=domain, form=form)

@app.route('/domain/<domain>/delete_catchall', methods=['POST'])
@login_required
def delete_catchall(domain):
	domain = db.get_or_404(Domain, domain)
	catchall = Alias.get_catchall(domain)
	if catchall is not None:
		db.session.delete(catchall)
		db.session.commit()
		flash('Catchall erfolgreich gelöscht!', 'success')
	return redirect(url_for('edit_domain', domain=domain.id))


@app.route('/domain/<domain>/create_catchall', methods=['GET', 'POST'])
@login_required
def create_catchall(domain):
	domain = db.get_or_404(Domain, domain)
	form = get_catchall_form(domain)
	if form.validate_on_submit():
		catchall = Alias()
		form.populate_obj(catchall)
		db.session.add(catchall)
		db.session.commit()
		flash('Catchall erfolgreich erstellt!', 'success')
		return redirect(url_for('edit_domain', domain=domain.id))
	elif request.method == 'POST':
		flash('Fehler beim Erstellen des Catchall!', 'danger')
	return render_template('edit_catchall.html', domain=domain, form=form)

@app.route('/domain/<domain>/alias/<id>', methods=['GET', 'POST'])
@login_required
def edit_alias(domain, id):
	alias, domain = Alias.get_or_404(id, domain)
	form = AliasForm(obj=alias)
	if form.validate_on_submit():
		form.populate_obj(alias)
		db.session.commit()
		flash('Alias erfolgreich gespeichert!', 'success')
		return redirect(url_for('edit_alias', domain=domain.id, id=id))
	elif request.method == 'POST':
		flash('Fehler beim Speichern des Alias!', 'danger')
	return render_template('edit_alias.html', alias=alias, domain=domain, form=form)

@app.route('/domain/<domain>/add_alias', methods=['GET', 'POST'])
@login_required
def add_alias(domain):
	domain = db.get_or_404(Domain, domain)
	form = AliasForm()
	form.source_domain.data = domain.domain
	if form.validate_on_submit():
		alias = Alias()
		form.populate_obj(alias)
		db.session.add(alias)
		db.session.commit()
		flash('Alias erfolgreich erstellt!', 'success')
		return redirect(url_for('edit_alias', domain=domain.id, id=alias.id))
	elif request.method == 'POST':
		flash('Fehler beim Erstellen des Alias!', 'danger')
	return render_template('edit_alias.html', alias=None, form=form, domain=domain)

@app.route('/delete_alias/<alias>', methods=['POST'])
@login_required
def delete_alias(alias):
	alias = db.get_or_404(Alias, alias)
	domain = alias.get_domain()
	db.session.delete(alias)
	db.session.commit()
	flash('Alias erfolgreich gelöscht!', 'success')
	return redirect(url_for('edit_domain', domain=domain.id))

@app.route('/domain/<domain>/edit_account/<account>', methods=['GET', 'POST'])
@login_required
def edit_account(domain, account, from_action=None):
	account, domain = Account.get_or_404(account, domain)
	form = AccountForm(obj=account)
	if form.validate_on_submit():
		form.populate_obj(account)
		db.session.commit()
		flash('Account erfolgreich gespeichert!', 'success')
		return redirect(url_for('edit_account', domain=domain.id, account=account.id, from_action='edit'))
	elif request.method == 'POST':
		flash('Fehler beim Speichern des Accounts!', 'danger')
	password_form = PasswordForm()
	from_action = 'edit' if request.method == 'POST' else request.args.get('from_action')
	return render_template('edit_account.html', domain=domain, from_action=from_action, account=account, check_password_form=CheckPasswordForm(), password_form=password_form, form=form)

@app.route('/domain/<domain>/add_account', methods=['GET', 'POST'])
@login_required
def add_account(domain):
	domain = db.get_or_404(Domain, domain)
	form = CreateAccountForm()
	form.domain.data = domain.domain
	form.quota.data = 1024
	form.enabled.data = True
	if form.validate_on_submit():
		account = Account()
		form.populate_obj(account)
		hash = create_hash(form.password.data)
		account.password = hash
		db.session.add(account)
		db.session.commit()
		flash('Account erfolgreich erstellt!', 'success')
		return redirect(url_for('edit_account', domain=domain.id, account=account.id, from_action='create'))
	return render_template('create_account.html', domain=domain, form=form)

@app.route('/change_password/<account>', methods=['POST'])
@login_required
def change_password(account):
	account = db.get_or_404(Account, account)
	domain = account.get_domain()
	form = PasswordForm()
	if form.validate_on_submit():
		hash = create_hash(form.password.data)
		account.password = hash
		db.session.commit()
		flash('Passwort erfolgreich geändert!', 'success')
		return redirect(url_for('edit_account', domain=domain.id, account=account.id, from_action='pwchange'))
	flash('Fehler beim Ändern des Passworts!', 'warning')
	return redirect(url_for('edit_account', domain=domain.id, account=account.id, from_action='pwchange'))
	

@app.route('/check_password/<account>', methods=['POST'])
@login_required
def check_password(account):
	account = db.get_or_404(Account, account)
	domain = account.get_domain()
	form = CheckPasswordForm()
	if form.validate_on_submit():
		try:
			if check_pw(form.password.data, account.password):
				flash('Das eingegebene Passwort ist korrekt!', 'success')
			else:
				flash('Das eingegebene Passwort ist falsch!', 'danger')
		except:
			flash('Das eingegebene Passwort konnte leider nicht überprüft werden!', 'warning')
	return redirect(url_for('edit_account', domain=domain.id, account=account.id, from_action='pwcheck'))

@app.errorhandler(404)
def page_not_found(e):
	flash('Die aufgerufene Seite konnte leider nicht gefunden werden!', 'danger')
	return render_template('start.html'), 404

@app.context_processor
def context_processor():
	domains = [ d for d in db.session.execute(db.select(Domain).order_by(Domain.domain)).scalars() ]
	return dict(domains=domains)
