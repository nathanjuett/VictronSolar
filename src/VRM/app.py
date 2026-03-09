from flask import Flask, render_template
import json
import datetime
import plotly.graph_objs as go
from plotly.offline import plot

app = Flask(__name__)


def load_data(path="output/output.json"):
    """Read the JSON produced by ``main.py`` and return the ``records`` dict."""
    with open(path, "r") as f:
        data = json.load(f)
    return data.get("records", {})


@app.route("/")
def index():
    # load the measurements
    records = load_data()

    # build a list of div snippets containing plotly graphs
    divs = []

    for key, series in records.items():
        if key in ["total_genset", "grid_history_to", "iOI1"]:
            continue
        # convert timestamps to datetime objects and unpack values
        x = [datetime.datetime.fromtimestamp(pt[0] / 1000) for pt in series]
        y = [pt[1] for pt in series]

        fig = go.Figure(
            data=[go.Scatter(x=x, y=y, mode="lines", name=key)],
            layout=go.Layout(title=key, xaxis=dict(title="time"), yaxis=dict(title="value")),
        )

        div = plot(fig, output_type="div", include_plotlyjs=False)
        divs.append(div)

    return render_template("index.html", graphs=divs)


if __name__ == "__main__":
    app.run(debug=True)
