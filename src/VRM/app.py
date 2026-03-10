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
        # when showing consumption data we want a single chart with multiple
        # series rather than one figure per key; the other prefixes keep the
        # old behaviour.
        if prefix == "cons":
            fig = go.Figure()
            for key, series in source.items():
                if key in ["total_genset", "grid_history_to", "iOI1","gc"]:
                    continue
                x = [datetime.datetime.fromtimestamp(pt[0] / 1000) for pt in series]
                y = [pt[1] for pt in series]
                fig.add_trace(go.Scatter(x=x, y=y, mode="lines", name=f"{prefix}:{key}"))

            fig.update_layout(
                template="plotly_dark",
                title="consumption",
                xaxis=dict(title="time"),
                yaxis=dict(title="value"),
            )

            divs.append(plot(fig, output_type="div", include_plotlyjs=False))
            return

        # default/legacy behavior for non-consumer prefixes
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
                    layout=go.Layout(template="plotly_dark", title=title, xaxis=dict(title="date"), yaxis=dict(title="value")),
                )
            else:
                # default line plot
                x = [datetime.datetime.fromtimestamp(pt[0] / 1000) for pt in series]
                y = [pt[1] for pt in series]

                fig = go.Figure(
                    data=[go.Scatter(x=x, y=y, mode="lines", name=title)],
                    layout=go.Layout(template="plotly_dark", title=title, xaxis=dict(title="time"), yaxis=dict(title="value")),
                )

            div = plot(fig, output_type="div", include_plotlyjs=False)
            divs.append(div)

    # merge evcs into consumption before plotting, adjusting Bc when
    # Pc would go negative after subtraction
    if "Pc" in cons_records and "evE" in evcs_records:
        # build lookup for evE by timestamp
        ev_lookup = {pt[0]: pt[1] for pt in evcs_records.get("evE", [])}
        new_pc = []
        # build a dictionary for Bc so we can easily adjust by timestamp
        bc_lookup = {pt[0]: pt[1] for pt in cons_records.get("Bc", [])}
        for pt in cons_records.get("Pc", []):
            ts, val = pt
            ev_val = ev_lookup.get(ts, 0)
            adjusted = val - ev_val
            if adjusted < 0:
                # move deficit into Bc
                deficit = -adjusted
                bc_lookup[ts] = bc_lookup.get(ts, 0) - deficit
                adjusted = 0
            new_pc.append([ts, adjusted])
        cons_records["Pc"] = new_pc
        # write modified bc_lookup back into records list form
        cons_records["Bc"] = [[ts, v] for ts, v in sorted(bc_lookup.items())]
        # also add evE as its own series under consumption
        cons_records["evE"] = evcs_records.get("evE", [])

    # build graphs for each dataset
    append_graphs(records)
    append_graphs(cons_records, prefix="cons")
    append_graphs(evcs_records, prefix="evcs")

    return render_template("index.html", graphs=divs)


if __name__ == "__main__":
    app.run(debug=True)
