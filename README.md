# 🎓 ÓraTracker — Egyetemi Hiányzás Követő

## Áttekintés

A **ÓraTracker** egy webes alkalmazás, amivel nyomon követheted az egyetemi hiányzásaidat. Figyelmeztet, ha közel vagy a maximum hiányzáshoz, és segít rendben tartani az óráidat.

## ✨ Funkciók

### 🔐 Bejelentkezés / Regisztráció
- Felhasználónév + jelszó alapú bejelentkezés
- Biztonságos jelszó hashelés (Werkzeug)
- Session kezelés Flask-Login-nal

### 📚 Kurzus kezelés
- Kurzus hozzáadása: név, oktató, típus (Előadás/Gyakorlat/Szeminárium/Labor), kreditek
- Időpont: nap, kezdés, befejezés, terem
- Szerkesztés és törlés
- Egyéni szín minden kurzushoz
- Megjegyzések mező

### 📅 Naptár importálás (.ics)
- Közvetlen importálás Google Calendar, Outlook, Neptun vagy Apple Calendar `.ics` naptárfájlból
- Automatikus felismerés:
  - Kurzus neve
  - Kurzus típusa (Előadás / Gyakorlat / Labor / Szeminárium)
  - Nap és időintervallum (pl. Hétfő 08:00 - 09:30)
  - Terem / Helyszín
  - Oktató neve a leírásból
- Előnézet képernyő, ahol kiválaszthatod, melyik kurzusokat szeretnéd importálni
- Minta naptárfájl mellékelve az azonnali teszteléshez: `sample_timetable.ics`

### 📊 Hiányzás követés
- Dashboard áttekintéssel: összesítés, veszélyeztetett kurzusok
- Színkódolt állapotjelzők:
  - 🟢 **Zöld** — < 50% kihasznált hiányzás
  - 🟡 **Sárga** — 50-80%
  - 🔴 **Piros** — > 80% (kritikus!)
- Gyors hiányzás rögzítés gombbal a dashboard-ról
- Részletes nézet: dátum + opcionális indoklás
- Hiányzás törlés

### ⚙️ Testreszabás
- **Világos / Sötét téma** váltás
- **Kiemelő szín** testreszabás (színválasztó)
- Félév megadása
- Jelszó módosítás
- Fiók törlés

## 🚀 Indítás

### 1. Egyszerű indítás (Ajánlott)

A mellékelt `run.sh` script automatikusan a virtuális környezetet (`venv`) használja:

```bash
cd /Users/kornel/.gemini/antigravity/scratch/attendance-tracker
./run.sh
```

### 2. Kézi indítás a virtuális környezettel

```bash
cd /Users/kornel/.gemini/antigravity/scratch/attendance-tracker

# Virtuális környezet aktiválása (opcionális):
source venv/bin/activate
python app.py

# VAGY közvetlen futtatás venv-ből:
./venv/bin/python app.py
```

### Megnyitás

Böngészőben nyisd meg: **http://127.0.0.1:5000**

1. Kattints a "Regisztrálj!" linkre
2. Hozz létre egy fiókot
3. Adj hozzá kurzusokat
4. Rögzítsd a hiányzásaid!

## 📁 Projekt struktúra

```
attendance-tracker/
├── app.py                    # Flask alkalmazás (modellek + route-ok)
├── requirements.txt          # Python függőségek
├── instance/
│   └── attendance.db         # SQLite adatbázis (automatikusan létrejön)
├── static/
│   ├── style.css             # Stílusok (téma, reszponzív, animációk)
│   └── app.js                # JavaScript (témaváltás, modálok, AJAX)
└── templates/
    ├── base.html             # Alap sablon (sidebar, flash üzenetek)
    ├── login.html            # Bejelentkezés
    ├── register.html         # Regisztráció
    ├── dashboard.html        # Főoldal / Áttekintés
    ├── add_course.html       # Kurzus hozzáadás/szerkesztés
    ├── course_detail.html    # Kurzus részletek + hiányzások
    └── settings.html         # Beállítások
```

## 🛠 Technológiák

| Technológia | Verzió | Cél |
|---|---|---|
| Flask | 3.1.0 | Web framework |
| Flask-SQLAlchemy | 3.1.1 | Adatbázis ORM |
| Flask-Login | 0.6.3 | Session kezelés |
| Werkzeug | 3.1.3 | Jelszó hashelés |
| SQLite | - | Adatbázis |
| Material Icons | - | Ikonok |
