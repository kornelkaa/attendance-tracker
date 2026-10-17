#!/bin/bash
# ÓraTracker indító script

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

if [ ! -d "venv" ]; then
    echo "Virtuális környezet nem található! Létrehozás..."
    python3 -m venv venv
    ./venv/bin/pip install -r requirements.txt
fi

echo "ÓraTracker indítása a virtuális környezetből..."
./venv/bin/python app.py
