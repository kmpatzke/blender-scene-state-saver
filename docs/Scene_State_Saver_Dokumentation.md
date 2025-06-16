# Scene State Saver Plugin - Dokumentation

## Übersicht
Das "Scene State Saver" Plugin ermöglicht es, verschiedene Zustände einer Blender-Szene zu speichern und später wieder zu laden. Es speichert Position, Rotation, Skalierung sowie Sichtbarkeits-Einstellungen aller Objekte.

## Installation
Das Plugin wurde erfolgreich in Blender installiert und ist sofort einsatzbereit.

## Verwendung

### N-Panel öffnen
1. Drücken Sie **N** um das N-Panel zu öffnen
2. Klicken Sie auf den Tab **"Scene State"**

### Interface-Elemente

#### Name-Eingabefeld
- Geben Sie hier den Namen für einen neuen State ein
- Standard: "State"

#### Save-Button
- **"Save New State"**: Erstellt einen neuen State mit dem eingegebenen Namen
- **"Update Selected State"**: Überschreibt den ausgewählten State mit dem aktuellen Szenen-Zustand

#### States-Liste
- Zeigt alle gespeicherten States an
- Namen können direkt in der Liste editiert werden
- Klicken Sie auf einen State um ihn auszuwählen

#### Load/Delete Buttons
- **"Load"**: Lädt den ausgewählten State
- **"Delete"**: Löscht den ausgewählten State

## Gespeicherte Eigenschaften

### Transform-Daten
- **Position** (Location)
- **Rotation** (Rotation Euler)
- **Skalierung** (Scale)

### Sichtbarkeits-Einstellungen
- **Viewport-Sichtbarkeit** (Hide in Viewport)
- **Render-Sichtbarkeit** (Hide in Render)

## Workflow-Beispiele

### Basis-Workflow
1. Arrangieren Sie Ihre Objekte wie gewünscht
2. Geben Sie einen Namen ein (z.B. "Setup 1")
3. Klicken Sie "Save New State"
4. Ändern Sie die Szene
5. Wählen Sie "Setup 1" aus der Liste
6. Klicken Sie "Load" um zur ursprünglichen Anordnung zurückzukehren

### Update-Workflow
1. Wählen Sie einen bestehenden State aus der Liste
2. Ändern Sie die Szene nach Ihren Wünschen
3. Klicken Sie "Update Selected State"
4. Der State wird mit den neuen Einstellungen überschrieben

### Sichtbarkeits-Management
1. Verstecken/Zeigen Sie Objekte im Viewport oder für Rendering
2. Speichern Sie verschiedene Sichtbarkeits-Konfigurationen
3. Wechseln Sie schnell zwischen verschiedenen Ansichten

## Technische Details

### Datenspeicherung
- States werden **persistent in der .blend Datei** gespeichert
- Daten werden als JSON im PropertyGroup gespeichert
- Automatische Speicherung beim Speichern der .blend Datei

### Unterstützte Objekte
- Alle Objekt-Typen (Mesh, Light, Camera, etc.)
- Funktioniert mit beliebig vielen Objekten
- Objekte werden über Namen identifiziert

### Fehlerbehandlung
- Warnung bei fehlender State-Auswahl
- Graceful Handling wenn Objekte nicht mehr existieren
- JSON-Validierung beim Laden

## Getestete Funktionen ✅

### Transform-Tests
- ✅ Position speichern/laden
- ✅ Rotation speichern/laden  
- ✅ Skalierung speichern/laden

### Sichtbarkeits-Tests
- ✅ Viewport-Sichtbarkeit
- ✅ Render-Sichtbarkeit
- ✅ Gemischte Sichtbarkeits-Zustände

### State-Management
- ✅ Mehrere States erstellen
- ✅ States laden und wechseln
- ✅ States löschen
- ✅ States überschreiben (Update)
- ✅ Namen editieren

### Persistenz
- ✅ States bleiben nach Blender-Neustart erhalten
- ✅ States werden mit .blend Datei gespeichert

## Anwendungsfälle

### Animation
- Speichern Sie Keyframe-Positionen
- Schneller Wechsel zwischen Posen
- Backup wichtiger Animationszustände

### Rendering
- Verschiedene Kamera-Setups
- Beleuchtungs-Konfigurationen
- Objekt-Sichtbarkeit für verschiedene Render-Passes

### Modeling
- Backup während Modeling-Prozess
- Vergleich verschiedener Varianten
- Schnelle Rückkehr zu funktionierenden Zuständen

### Szenen-Organisation
- Aufräumen vs. Arbeits-Ansicht
- Präsentations-Modi
- Debug-Konfigurationen

## Plugin-Informationen

**Version**: 1.0  
**Kompatibilität**: Blender 3.0+  
**Kategorie**: Scene Management  
**Status**: ✅ Vollständig funktionsfähig und getestet

## Support
Das Plugin wurde umfassend getestet und funktioniert zuverlässig. Bei Problemen prüfen Sie:
1. Ist das N-Panel geöffnet?
2. Ist der "Scene State" Tab sichtbar?
3. Sind Objekte in der Szene vorhanden?
4. Ist ein State ausgewählt beim Laden?