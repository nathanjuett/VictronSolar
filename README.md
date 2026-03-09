# VictronSolar

Requires .env file with the following values
APP_NAME=VictronSolar
VRM_USERNAME=[username]
VRM_PASSWORD="[password]"
VRM_LIVEDATA="False"
VRM_TESTDATA="[Test json output file]"
VRM_DAYSPAST=30

## Web UI

A small Flask app can display interactive graphs from the JSON produced by `main.py`.

1. Install the Python dependencies (use the provided virtualenv or your own):
   ```sh
   python -m pip install -r requirements.txt
   ```
2. Run the data-fetch script, or copy an existing `output/output.json` into the project root.
3. Start the web server:
   ```sh
   export FLASK_APP=src/VRM/app.py
   flask run
   ```
4. Visit http://127.0.0.1:5000/ in your browser and you should see a graph for each
   key found under `records` in the JSON file.

You can also launch the app directly with `python src/VRM/app.py` when
`debug=True` is acceptable.
