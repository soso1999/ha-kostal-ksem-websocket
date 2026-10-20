# Entwicklung

Python 3.13 und Home Assistant 2025.6.0 sind die Referenzumgebung.

```sh
python -m venv .venv
. .venv/bin/activate
pip install -r requirements-dev.txt
pytest -q
ruff check custom_components tests
ruff format --check custom_components tests
```

Tests verwenden ausschließlich synthetische Protobuf-Nachrichten und lokale HTTP-/WS-Server.
Keine realen Zugangsdaten oder Netzwerkmitschnitte committen. Protokolländerungen mit
Firmwarestand und anonymisierter Struktur beschreiben. Vor einem Release zusätzlich
Einrichtung, sechs Werte, Netzwerkunterbrechung, Neustart, Passwortänderung und Entfernen
der Integration in Home Assistant an realer Hardware prüfen.
