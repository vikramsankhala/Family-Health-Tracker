@echo off
echo Installing dependencies...
pip install -r requirements.txt
echo.
echo Starting Health Tracker...
echo Open your browser to http://localhost:5000
echo Press Ctrl+C to stop the server
echo.
python app.py

