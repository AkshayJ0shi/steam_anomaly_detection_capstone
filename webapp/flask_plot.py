import pandas as pd
import numpy as np
import io
import pickle
import random
from bokeh.models import (HoverTool, FactorRange, Plot, LinearAxis, Grid,
                          Range1d)
from bokeh.models.glyphs import VBar
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models.sources import ColumnDataSource
from flask import Flask, render_template

app = Flask(__name__)

with open('../data/')

@app.route('/')
def index():
    return chart(10)

@app.route("/<int:bars_count>/")
def chart(bars_count):
    if bars_count <= 0:
        bars_count = 1

    data = {"days": [], "bugs": [], "costs": []}
    for i in range(1, bars_count + 1):
        data['days'].append(i)
        data['bugs'].append(random.randint(1,100))
        data['costs'].append(random.uniform(1.00, 1000.00))

    hover = create_hover_tool()
    plot = create_bar_chart(data, "Bugs found per day", "days",
                            "bugs", hover)
    script, div = components(plot)

    return render_template("chart.html", bars_count=bars_count,
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


def create_bar_chart(data, title, x_name, y_name, hover_tool=None,
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
