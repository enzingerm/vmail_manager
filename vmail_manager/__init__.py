import sys, os

import yaml

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

try:
    with open(os.path.join(app.config.root_path, 'config.yaml'), 'r') as stream:
        config = yaml.safe_load(stream)
except yaml.YAMLError as e:
    sys.exit(f"Error in config file: {e}")
except:
    sys.exit(f"Error loading config from 'config.yaml'")

app.config.from_mapping(config)

db = SQLAlchemy()
db.init_app(app)
with app.app_context():
    db.Model.metadata.reflect(db.engine)

import vmail_manager.views
if not app.config['LOGIN_DISABLED']:
    import vmail_manager.ldap