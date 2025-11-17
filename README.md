# ChargeNode RFID CSV Converter

Ett Streamlit-program för att konvertera Excel-filer med RFID-data till standardiserat CSV-format för ChargeNodes laddstolpar.

## 🚀 Installation

### 1. Installera Python
Se till att du har Python 3.8 eller senare installerat.

### 2. Installera dependencies
```bash
pip install -r requirements.txt
```

## ▶️ Köra programmet

```bash
streamlit run rfid_converter.py
```

Programmet öppnas automatiskt i din webbläsare på `http://localhost:8501`

## 📋 Funktioner

- ✅ Konvertera RFID-data från olika Excel-format
- ✅ Hantera både HEX-nummer och TAGG ID
- ✅ Validera och rensa data automatiskt
- ✅ Dela upp per företag (om flera finns)
- ✅ Detektera och rapportera fel och varningar
- ✅ Förhandsgranska data innan export
- ✅ Statistik och översikt

## 📊 Stödda format

### Indatafiler
- Excel (.xlsx) med en eller flera flikar
- RFID-nummer (HEX) eller TAGG ID
- Regnummer/Referens (Identifieringsnummer)
- Företagsnamn (valfritt)

### Utdataformat
```
RFID;Identifieringsnummer
1A2B3C4D;ABC123
5E6F7890;XYZ789
```

## 🎯 Arbetsflöde

1. **Instruktioner** - Läs om hur programmet fungerar
2. **Ladda upp fil** - Välj din Excel-fil och flik
3. **Kolumnmappning** - Ange vilka kolumner som innehåller vad
4. **Validering** - Automatisk validering och felrapportering
5. **Resultat** - Ladda ner genererade CSV-filer

## ⚙️ TAGG ID → RFID Konvertering

Om din fil innehåller TAGG ID istället för RFID-nummer, behöver du också ladda upp en MER-fil som innehåller mappningen:

**MER-filens kolumner:**
- `Visible Number` (= TAGG ID)
- `Key/Card number` (= RFID)

## 🔍 Validering

Programmet validerar automatiskt:
- ✅ HEX-format (6-10 tecken, endast 0-9 och A-F)
- ✅ Duplicerade RFID-nummer
- ✅ Saknade obligatoriska fält
- ✅ Tomma rader

## 📁 Filstruktur

```
rfid_converter/
├── rfid_converter.py      # Huvudprogram
├── requirements.txt        # Python dependencies
└── README.md              # Denna fil
```

## 💡 Tips

- Se till att Excel-filerna är korrekta innan uppladdning
- Använd förhandsgranskningsfunktionen för att verifiera data
- Kontrollera statistiken innan export
- Ladda ner felrapporter för att åtgärda problem

## 🆘 Felsökning

### "Module not found"
```bash
pip install -r requirements.txt
```

### Programmet öppnas inte i webbläsaren
Öppna manuellt: `http://localhost:8501`

### Excel-fil kan inte läsas
Kontrollera att filen är i .xlsx format (inte .xls)

## 📝 Version

Version 1.0 - November 2025

## 🏢 ChargeNode Group

Utvecklat för ChargeNode Group - Sveriges största laddoperatör
