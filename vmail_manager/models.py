from flask import abort

from . import db

class Domain(db.Model):
	__table__ = db.Model.metadata.tables['domains']


class Alias(db.Model):
	__table__ = db.Model.metadata.tables['aliases']

	@classmethod
	def get_catchall(cls, domain):
		return db.session.execute(db.select(cls).filter_by(source_username=None, source_domain=domain.domain)).scalar()
	
	@classmethod
	def get_or_404(cls, id, domain_id=None):
		alias = db.get_or_404(cls, id)
		if domain_id is not None:
			domain = db.get_or_404(Domain, domain_id)
			if domain.domain != alias.source_domain:
				abort(404)
			return alias, domain
		return alias 

	def get_domain(self):
		return db.session.execute(db.select(Domain).filter_by(domain=self.source_domain)).scalar()


class Account(db.Model):
	__table__ = db.Model.metadata.tables['accounts']

	@classmethod
	def get_or_404(cls, id, domain_id=None):
		account = db.get_or_404(cls, id)
		if domain_id is not None:
			domain = db.get_or_404(Domain, domain_id)
			if domain.domain != account.domain:
				abort(404)
			return account, domain
		return account 
	
	def get_domain(self):
		return db.session.execute(db.select(Domain).filter_by(domain=self.domain)).scalar()

