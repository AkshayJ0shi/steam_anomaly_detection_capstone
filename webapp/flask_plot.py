import pandas as pd
import numpy as np
import io
import pickle
from collections import defaultdict
import psycopg2 as pg
from random import sample
from bokeh.models import (HoverTool, FactorRange, Plot, LinearAxis, Grid,
                          Range1d)
from bokeh.models.glyphs import VBar
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models.sources import ColumnDataSource
from bokeh import
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
items_query = cur.execute(query)
items = set(items_query.fetchall()) # set of item names
# Get the item ids (they will be easier to work with and test manually for now)
query = """SELECT DISTINCT item_id from id;"""
item_ids_query = cur.execute(query)
item_ids = set(items_query.fetchall()) # Set of item id's

# Use the item names to populate a dictionary when the item id is put into the browser

# The home page will redirect to a random item id for now
@app.route('/')
def index():
    return graph(sample(item_ids, 1))

# NEED TO USE CALLBACKS TO GET SQL QUERIES
@app.route("/<int:item_id>/")
def graph(id):
    data = defaultdict(list)
    # Get dates, prices, quantity for the given item_id
    query = """
            SELECT date, price, quantity 
            FROM sales
            WHERE item_id = %s;
            """
    cur.execute(query, (id,))
    query_data = cur.fetchall()
    data['dates'] = [x[0] for x in query_data]
    data['prices'] = [x[1] for x in query_data]
    data['quantities'] = [x[2] for x in query_data]

    # Get item name
    query = """
            SELECT item_name
            FROM id
            WHERE item_id = %s;"""
    cur.execute(query, (id,))
    item_name = cur.fetchone()[0]


    hover = create_hover_tool()
    plot = create_graph(data, item_name, "dates",
                            "prices", hover)
    script, div = components(plot)

    return render_template("chart.html", item_name=item_name,
                           the_div=div, the_script=script)

# def create_hover_tool():
#     """Generates the HTML for the Bokeh's hover data tool on our graph."""
#     hover_html = """
#       <div>
#         <span class="hover-tooltip">$x</span>
#       </div>
#       <div>
#         <span class="hover-tooltip">@bugs bugs</span>
#       </div>
#       <div>
#         <span class="hover-tooltip">$@costs{0.00}</span>
#       </div>
#     """
#     return HoverTool(tooltips=hover_html)

def create_hover_tool():
    return HoverTool(
        tooltips=[
            ( 'Date',   '@date{%F}'            ),
            ( 'Median Price',  '$@{adj close}{%0.2f}' ), # use @{ } for field names with spaces
            ( 'Quantity', '@volume{0.00 a}'      ),
        ],

        formatters={
            'date'      : 'datetime', # use 'datetime' formatter for 'date' field
            'adj close' : 'printf',   # use 'printf' formatter for 'adj close' field
                                      # use default 'numeral' formatter for other fields
        },

        # display a tooltip whenever the cursor is vertically in line with a glyph
        mode='vline'
    )


def create_graph(data, title, x_name, y_name, hover_tool=None,
                     width=1200, height=300):
    """Creates a bar chart plot with the exact styling for the centcom
       dashboard. Pass in data as a dictionary, desired plot title,
       name of x axis, y axis and the hover tool HTML.
    """
    source = ColumnDataSource(data)
    xdr = FactorRange(factors=tuple([str(x) for x in data[x_name]]))
    ydr = Range1d(start=0,end=max(data[y_name])*1.5)

    tools = []
    if hover_tool:
        tools = [hover_tool,]

    plot = figure(title=title, x_range=xdr, y_range=ydr, plot_width=width,
                  plot_height=height, h_symmetry=False, v_symmetry=False,
                  min_border=0, toolbar_location="above", tools=tools,
                  sizing_mode='scale_width', outline_line_color="#666666")
    # Sample bar graph
    # glyph = VBar(x=x_name, top=y_name, bottom=0, width=1,
    #              fill_color="#e02127")
    # plot.add_glyph(source, glyph)

    # line graph
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


# Almost exactly the hovertool I need
