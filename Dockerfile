FROM python:3.11-slim

# Munkakönyvtár beállítása
WORKDIR /app

# Környezeti változók: Python kimenet azonnali kiírása és bytecode elkerülése
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5000

# Függőségek másolása és telepítése
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Alkalmazás forráskódjának másolása
COPY . .

# Instance könyvtár létrehozása a perzisztens SQLite adatbázisnak
RUN mkdir -p /app/instance

# Port megnyitása
EXPOSE 5000

# Gunicorn WSGI szerver indítása
CMD ["gunicorn", "--workers=2", "--bind=0.0.0.0:5000", "app:app"]
