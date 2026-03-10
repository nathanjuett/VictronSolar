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
    # load the measurements from the main output plus the two additional files
    records = load_data()
    cons_records = load_data("output/output_consumption.json")
    evcs_records = load_data("output/output_evcs.json")

    # build a list of div snippets containing plotly graphs
    divs = []

    # helper that iterates through a dictionary and appends graphs, optionally
    # prefixing the title to avoid collisions when the same key appears in
    # multiple files.
    def append_graphs(source, prefix=None):
        for key, series in source.items():
            if key in ["total_genset", "grid_history_to", "iOI1","gc"]:
                continue

            title = f"{prefix + ':' if prefix else ''}{key}"

            # special handling for evcs energy data: show as a bar chart
            # grouped by date rather than a continuous line
            if prefix == "evcs" and key == "evE":
                # aggregate values by date
                daily = {}
                for pt in series:
                    dt = datetime.datetime.fromtimestamp(pt[0] / 1000)
                    ddate = dt.date()
                    daily.setdefault(ddate, 0)
                    daily[ddate] += pt[1]

                x = list(daily.keys())
                y = list(daily.values())

                fig = go.Figure(
                    data=[go.Bar(x=x, y=y, name=title)],
                    layout=go.Layout(title=title, xaxis=dict(title="date"), yaxis=dict(title="value")),
                )
            else:
                # default line plot
                x = [datetime.datetime.fromtimestamp(pt[0] / 1000) for pt in series]
                y = [pt[1] for pt in series]

                fig = go.Figure(
                    data=[go.Scatter(x=x, y=y, mode="lines", name=title)],
                    layout=go.Layout(title=title, xaxis=dict(title="time"), yaxis=dict(title="value")),
                )

            div = plot(fig, output_type="div", include_plotlyjs=False)
            divs.append(div)

    # build graphs for each dataset
    append_graphs(records)
    append_graphs(cons_records, prefix="cons")
    append_graphs(evcs_records, prefix="evcs")

    return render_template("index.html", graphs=divs)


if __name__ == "__main__":
    app.run(debug=True)
