README – Kurzanleitung für products.json

Zweck
- Produkte und Kategorien für das Kassensystem pflegen.
- Änderungen nachvollziehbar halten über meta.version und meta.ausgabedatum.
- Hinweis: JSON unterstützt keine Kommentare.

Version/Datum
- Bei jeder inhaltlichen Änderung:
  - meta.version nach SemVer anheben (Patch/Minor).
  - meta.ausgabedatum auf YYYY-MM-DD setzen.

Neues Produkt anlegen
1) In products ein neues Objekt einfügen.
2) Einzigartige id (Slug) vergeben.
3) category auf eine existierende categories.id setzen.
4) order vergeben (empfohlen in 10er-Schritten).
5) version/ausgabedatum aktualisieren.

    {
      "id": "produkt-id",
      "name": "Produktname",
      "price": 0.00,
      "unit": { "quantity": 1, "uom": "Stück", "packaging": null, "display": "pro Stück" },
      "category": "kategorie-id",
      "active": true,
      "order": 90,
      "aliases": []
    }

Neue Kategorie anlegen
1) Objekt zu categories hinzufügen (id, name, order).
2) category der betroffenen Produkte auf diese id setzen.
3) version/ausgabedatum aktualisieren.

    { "id": "kategorie-id", "name": "Kategoriename", "order": 90 }

Produkt anpassen
- price, name oder unit ändern; bei Preis-/Textänderungen version/ausgabedatum aktualisieren.

Produkt inaktiv setzen (ausblenden)
- active auf false setzen (empfohlen, um Historie zu behalten).

    "active": false

Produkt löschen (dauerhaft entfernen)
- Produktobjekt aus products entfernen.
- Hinweis: Besser active=false, wenn Belege/Verläufe existieren.

Sortierung
- Über order aufsteigend. In 10er-Schritten anlegen (10, 20, 30 …), damit später dazwischen eingefügt werden kann.

ID-/Slug-Regeln
- Kleinbuchstaben, Ziffern, Bindestriche.
- Umlaute ersetzen: ä→ae, ö→oe, ü→ue, ß→ss.
- IDs nach Veröffentlichung nicht ändern.

Schnell-Check vor dem Veröffentlichen
- Gültiges JSON (keine Kommentare, keine überflüssigen Kommatare).
- Jede product.category existiert in categories.
- Preise mit Dezimalpunkt (z. B. 5.00).
- meta.version und meta.ausgabedatum aktualisiert.
