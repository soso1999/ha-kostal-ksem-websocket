# v0.1.0 — KOSTAL KSEM WebSocket

Erste UI-konfigurierbare Fassung der KSEM-WebSocket-Integration.

- Einrichtung mit IP/Hostname und Administratorpasswort, inklusive Live-Verbindungstest.
- Ein KSEM-Gerät mit Strom L1/L2/L3 und Wirkleistung L1/L2/L3.
- Lokaler WebSocket-/Protobuf-Push ohne Modbus TCP oder KSEM TCP-Slave.
- Automatische Wiederverbindung, Erkennung ausbleibender Daten und Reauthentifizierung.
- Deutsche und englische Oberfläche, HACS-Verzeichnisstruktur und MIT-Lizenz.

**Migration:** Den alten YAML-Plattformblock vor dem Neustart entfernen. Kein automatischer
YAML-Import und keine automatische Übernahme der alten Entitäts-IDs. Dashboards/Automationen
anschließend prüfen. Details in README.md.

**Teststand:** Protokollbasis aus der funktionierenden KSEM-2.7.2-Testversion übernommen.
Für Prüfungen dieser neuen Fassung und offene Hardwaretests siehe VALIDATION.md.
Andere Firmwarestände sind unbestätigt. Inoffiziell, ohne Verbindung zu KOSTAL.
