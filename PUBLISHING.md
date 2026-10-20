# Release-Verfahren

Repository: https://github.com/soso1999/ha-kostal-ksem-websocket (öffentlich).

1. `VALIDATION.md` prüfen und für neue Änderungen aktualisieren; reale HA-/KSEM-Tests dokumentieren.
2. Version in `custom_components/ksem_ws/manifest.json` und Release-Text aktualisieren.
3. Tests und Formatprüfungen ausführen; `SHA256SUMS` und Download-ZIP neu erzeugen.
4. Änderungen auf GitHub hochladen und GitHub Actions prüfen.
5. Passenden Release-Tag erstellen; für v0.1.0 ist `RELEASE_v0.1.0.md` der Release-Text.
6. Repository als HACS Custom Repository vom Typ Integration testen.

Die Prüfungen ersetzen keine Aufnahme in die HACS-Standardliste.
Keine `.storage`-Dateien, Backups oder persönliche `secrets.yaml` hochladen.
