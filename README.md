# VictronSolar

Requires .env file with the following values
```
VRM_USERNAME=[username]
VRM_PASSWORD="[password]"
VRM_DAYSPAST=30'
```
## Web UI

A small Flask app can display interactive graphs from live Victron API data.

1. Install the Python dependencies (use the provided virtualenv or your own):
   ```sh
   python -m pip install -r requirements.txt
   ```
2. Start the web server:
   ```sh
   export FLASK_APP=src/VRM/app.py
   flask run
   ```
4. Visit http://127.0.0.1:5000/ in your browser and you should see a dashboard.

You can also launch the app directly with `python src/VRM/app.py` when
`debug=True` is acceptable.
## main.py
Executing the main.py with `python src/VRM/main.py` will create json files in the project `output/*.json` folder.