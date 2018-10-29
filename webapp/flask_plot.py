import pandas as pd
import numpy as np
import io
import pickle
from collections import defaultdict
import psycopg2 as pg
from random import sample
from bokeh.models import (HoverTool, FactorRange, LinearAxis, Grid,
                          Range1d)
from bokeh.models.glyphs import VBar, Line
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models.sources import ColumnDataSource
from flask import Flask, render_template

app = Flask(__name__)

# Load data
# with open('../data/cs_df_M.pkl', 'rb') as f:
#     df = pickle.load(f)

# Connect to the database
conn = pg.connect(dbname='steam_capstone', host='localhost')
cur = conn.cursor()
# Get the item names
query = """SELECT DISTINCT item_name from id;"""
cur.execute(query)
items = set(cur.fetchall()) # set of item names
# Get the item ids (they will be easier to work with and test manually for now)
query = """SELECT DISTINCT item_id from id;"""
cur.execute(query)
item_ids = set([x[0] for x in cur.fetchall()]) # Set of item id's


# The home page will redirect to a random item id for now
@app.route('/')
def index():
    return graph(sample(item_ids, 1)[0])


# NEED TO USE CALLBACKS TO GET SQL QUERIES
@app.route("/<int:item_id>/")
def graph(item_id):
    # Get dates, prices, quantity for the given item_id
    query = """
            SELECT date, price, quantity 
            FROM sales
            WHERE item_id = %s
            ORDER BY date asc;
            """
    cur.execute(query, (item_id,))
    query_data = cur.fetchall()
    data = {'dates': [x[0] for x in query_data],
            'prices': [x[1] for x in query_data],
            'quantities': [x[2] for x in query_data]}

    # Get item name
    query = """
            SELECT item_name
            FROM id
            WHERE item_id = %s;"""
    cur.execute(query, (item_id,))
    item_name = cur.fetchone()[0]


    hover = create_hover_tool()
    plot = create_graph(data, item_name, "dates",
                            "prices", hover)
    script, div = components(plot)

    return render_template("chart.html", item_name=item_name,
                           the_div=div, the_script=script)


def create_hover_tool():
    return HoverTool(
                tooltips=[
                    ('Date',   '@dates{%F}'),
                    ('Median Price',  '$@{prices}{%0.2f}'), # use @{ } for field names with spaces
                    ('Quantity', '@quantities'),],
                formatters={
                    'dates'      : 'datetime', # use 'datetime' formatter for 'date' field
                    'prices' : 'printf',   # use 'printf' formatter for 'adj close' field
                                              # use default 'numeral' formatter for other fields
                },
                # display a tooltip whenever the cursor is vertically in line with a glyph
                mode='vline'
            )

def anomaly_toggle():
    # I'd like to be able to add a button that will turn on and off the anomaly labels, attached to the graph
    pass

def create_graph(data, title, x_name, y_name, hover_tool=None,
                     width=1200, height=300):
    """Creates a bar chart plot with the exact styling for the centcom
       dashboard. Pass in data as a dictionary, desired plot title,
       name of x axis, y axis and the hover tool HTML.
    """
    source = ColumnDataSource(data)
    ydr = Range1d(start=0, end=max(data[y_name])*1.5)

    plot = figure(title=title, x_axis_type='datetime', y_range=ydr, plot_width=width,
                  plot_height=height, h_symmetry=False, v_symmetry=False,
                  min_border=0, toolbar_location="above", sizing_mode='scale_width',
                  outline_line_color="#666666")

    if hover_tool:
        plot.add_tools(hover_tool)

    plot.line(x=x_name, y=y_name, source=source)

    xaxis = LinearAxis()
    yaxis = LinearAxis()

    plot.add_layout(Grid(dimension=0, ticker=xaxis.ticker))
    plot.add_layout(Grid(dimension=1, ticker=yaxis.ticker))
    plot.toolbar.logo = None
    plot.min_border_top = 0
    plot.xgrid.grid_line_color = None
    plot.ygrid.grid_line_color = "#999999"
    plot.yaxis.axis_label = "Price"
    plot.ygrid.grid_line_alpha = 0.1
    plot.xaxis.axis_label = "Date"
    plot.xaxis.major_label_orientation = 1
    return plot

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)

