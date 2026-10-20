# Prüfstand v0.1.0

Datum: 20. Oktober 2026.

## Ausgeführt

- **40 Tests bestanden** mit echtem Home-Assistant-Kernpaket 2025.6.0 und aiohttp 3.12.12.
- Synthetische Protobuf-Nachrichten: alle drei Phasen, Milli-Skalierung, positive/negative
  Wirkleistung, fehlende/Null-Werte, unbekannte Felder und fehlerhafte/trunkierte Nachrichten.
- Lokaler aiohttp-Testserver: OAuth-Formular, Bearer-Nachricht am WebSocket, erneute
  Tokenanforderung, HTTP-Fehler, abgelehntes Passwort, Redirect-Verweigerung, fehlender
  Token, falscher Stream, ungültiges Protobuf, Verbindungsende und ausbleibende Daten.
- HA-Klassen/API-Aufrufe: Formularerfolg und Fehlerzuordnung, Hostvalidierung,
  Passwortaktualisierung, sechs Sensorbeschreibungen, Verfügbarkeit bei Nullwert,
  Authentifizierungsfehler, Wiederverbindung, Task-Abbruch und Unload.
  Config-Entry-Verwaltung und einzelne UI-/Lifecycle-Aufrufe werden dabei gemockt;
  dies ist kein vollständiger Home-Assistant-Systemtest.
- Manifest, HACS-Metadaten und deutsche/englische Übersetzungskonsistenz geprüft.
- Ruff 0.17.1: Code- und Formatprüfung bestanden.
- JSON-Dateien eingelesen, Python-Dateien syntaktisch geprüft; ZIP-Inhalt und Prüfsummen geprüft.
- Kein übernommener persönlicher Host, kein persönliches Passwort und kein persönlicher Token
  aus dem Quellchat im Projekt. Tests verwenden nur Loopback, reservierte Beispielnamen
  und ausdrücklich synthetische Zugangsdaten.

## Grenzen der lokalen Testumgebung

Lokale Prüfungen unter macOS mit Python 3.13.1, pytest 9.1.1 und pytest-asyncio 1.4.0.
Home Assistant 2025.6.0 fordert offiziell mindestens Python 3.13.2. Für die lokalen
Import-/API-Tests wurde sein Kernpaket gezielt mit den benötigten Abhängigkeiten installiert;
dies ist keine vollständig aufgelöste oder gestartete HA-Installation. Mehrere nicht
benötigte HA-Abhängigkeiten fehlen, einige Hilfsbibliotheken haben neuere Versionen.
Eine DeprecationWarning stammt aus Home Assistants HTTP-Anwendung.
Der mitgelieferte CI-Workflow verwendet Python 3.13 und die vollständigen Anforderungen
aus requirements-dev.txt; dieser GitHub-Workflow wurde noch nicht auf GitHub ausgeführt.

Zusätzlich bestanden zuvor 29 unabhängige Protokoll-/Transporttests unter Python 3.12.2
mit aiohttp 3.14.5. Dabei wurden die HA-unabhängigen Module isoliert geladen.

## Noch in der echten Installation zu prüfen

- [ ] Migration vom alten YAML-Block, Neustart und UI-Einrichtung.
- [ ] Ein Gerät und genau sechs verfügbare Sensoren.
- [ ] Alle Werte und Leistungsvorzeichen mit der KSEM-Oberfläche vergleichen.
- [ ] Netzwerkausfall: nicht verfügbar, anschließend automatische Wiederverbindung.
- [ ] Passwortänderung: erneute Authentifizierung und Wiederaufnahme des Streams.
- [ ] Entfernen/erneutes Hinzufügen sowie Home-Assistant-Neustart ohne verwaiste Tasks.
- [ ] Mehrstündiger Betrieb, Firmwarekompatibilität und HACS-Installation nach Veröffentlichung.

Die Ausgangsversion wurde laut Nutzer mit KSEM-Firmware 2.7.2 plausibel betrieben.
Die neue Fassung wurde hier nicht mit einem realen KSEM verbunden. Es wurden keine
bestehende Home-Assistant-Installation und keine Geräteeinstellungen verändert.
