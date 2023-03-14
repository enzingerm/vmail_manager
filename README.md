# Vmail-Manager

- Verwaltung eines Mailservers, der nach dem von Thomas Leister vorgeschlagenen Datenbank-Schema eingerichtet wurde (siehe https://thomas-leister.de/mailserver-debian-buster/)
- Webbasiert (Python/Flask)
- Verwaltung von
  - Catchall-Adressen
  - Aliassen
  - Accounts
- Optionale LDAP-Authentifizierung und -authorisierung zur Zugangsbeschränkung


## Einrichtung
- Repository klonen
- Abhängigkeiten installieren: `pip install -r requirements.txt` 
- Konfigurationsdatei erstellen: `cp vmail_manager/config.yaml.example vmail_manager/config.yaml`
- `config.yaml` anpassen (Datenbank-URI, Flask SECRET_KEY generieren, evtl LDAP-Authentifizierung konfigurieren)
- Webserver starten (`flask --app vmail_manager run --debug`)
- oder per WSGI einbinden (`from vmail_manager import app as application`)