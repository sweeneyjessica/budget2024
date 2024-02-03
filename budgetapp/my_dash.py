from dash import Dash, html, dcc
from budgetapp.db import get_db
import pandas as pd
import plotly.express as px


def init_dashboard(server):
    dash_app = Dash(__name__, 
                    server=server, 
                    routes_pathname_prefix = '/dashboard/')
    
    db = get_db()
    data = db.execute(
        'SELECT m.category, round(sum(d.amount), 2)'
        ' FROM debit d JOIN merchant_to_category m ON d.descr = m.merchant'
        ' GROUP BY m.category'
    )

    df = pd.DataFrame(data)

    dash_app.layout = html.Div([
        html.Div(children='Categories'),
        html.Hr(),
        dcc.Graph(figure=px.pie(df, values=1, names=0, title='Category Spending'))
    ])

    # init_callbacks(dash_app)

    return dash_app.server


# def init_callbacks(dash_app):
#     @dash_app.callback(
#         # callback input/output
#     )
#     def update_graph(rows):
#         # callback logic