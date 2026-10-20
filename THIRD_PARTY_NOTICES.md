# Herkunft und Credits

Die funktionierende YAML-Testintegration wurde aus dem vom Nutzer referenzierten Chat
wiederhergestellt. Deren Smart-Meter-Endpunkt, Bearer-Anmeldung, neun OBIS-Codes,
Skalierung und sechs Messgrößen sind die technische Ausgangsbasis dieser Fassung.
Es wurden keine privaten Chat-Auszüge oder Gerätedumps in dieses Repository kopiert.

Öffentliches Reverse Engineering: [mgoeppe/ksem](https://github.com/mgoeppe/ksem),
Stand `12d08f4d8380712ae8df6f995c07ece9b0a29515` (bei Erstellung abgerufen).
Das Projekt dokumentiert OAuth-Anmeldung, GDRs/GDR und OBIS-Werttabellen.
Der hier enthaltene Python-Decoder ist eine eigenständige minimale Implementierung;
Go-Dateien, generierte Protobuf-Dateien und das vollständige Schema werden nicht verteilt.
Zur nachvollziehbaren Attribution ist die unveränderte MIT-Lizenz einschließlich
Copyright (c) 2024 Mathias Göppel unter `licenses/mgoeppe-ksem-MIT.txt` enthalten.

`emos`, `admin` und der numerische OAuth-Clientwert im Client sind veröffentlichte
Protokollkonstanten, keine persönlichen Zugangsdaten. Persönliche Administratorpasswörter
und kurzlebige Bearer-Tokens gehören ausschließlich in die laufende Installation.

KOSTAL und KSEM sind Marken ihrer jeweiligen Rechteinhaber. Dieses inoffizielle
Community-Projekt ist nicht mit KOSTAL verbunden und wird nicht von KOSTAL unterstützt.

Die geometrischen Zählersymbole in `brand/` und `custom_components/ksem_ws/brand/`
sind eigene Projektgrafiken unter der Projekt-MIT-Lizenz; keine KOSTAL-Logos.
