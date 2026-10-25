# Release-Verfahren

Repository: https://github.com/soso1999/ha-kostal-ksem-websocket (öffentlich).

1. `VALIDATION.md` prüfen und für neue Änderungen aktualisieren; reale HA-/KSEM-Tests dokumentieren.
2. Version in `custom_components/ksem_ws/manifest.json` und Release-Text aktualisieren.
3. Tests und Formatprüfungen ausführen; `SHA256SUMS` und Download-ZIP neu erzeugen.
4. Änderungen auf GitHub hochladen und GitHub Actions prüfen.
5. Passenden Release-Tag erstellen; für v0.1.0 ist `RELEASE_v0.1.0.md` der Release-Text.
6. Installation und Updates über den vorhandenen HACS-Katalogeintrag testen.

Das Repository ist in der [HACS-Standardliste](https://github.com/hacs/default/blob/master/integration) enthalten.
Für reine Dokumentationskorrekturen ist kein Versionswechsel und kein neuer Release erforderlich;
die Versions- und Release-Schritte gelten für neue Integrationsversionen.
Keine `.storage`-Dateien, Backups oder persönliche `secrets.yaml` hochladen.
