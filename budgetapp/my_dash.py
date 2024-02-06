from dash import Dash, html, dcc, callback, Output, Input
from budgetapp.db import get_db
import pandas as pd
import plotly.express as px


def init_dashboard(server):
    dash_app = Dash(__name__, 
                    server=server, 
                    routes_pathname_prefix = '/dashboard/')

    dash_app.layout = html.Div([
        html.Div(children='My First App with Data'),
        html.Hr(),
        dcc.RadioItems(options=['Yearly', 'Weekly'], value='Weekly', id='controls-and-radio-item'),
        dcc.RadioItems(options=['Dining', 'Travel', 'Groceries'], id='controls-sub-radio-item'),
        dcc.Graph(figure={}, id='controls-and-graph')
    ])

    init_callbacks(dash_app)

    return dash_app.server


def init_callbacks(dash_app):
    def get_yearly_category_spend_data():
        db = get_db()

        df = db.execute(
                'SELECT m.category AS Category, round(sum(d.amount), 2) AS Total'
                ' FROM debit d JOIN merchant_to_category m ON d.descr = m.merchant'
                ' GROUP BY m.category'
            )

        return pd.DataFrame(df)

    def get_weekly_category_spend_data(category_chosen):
        db = get_db()

        df = db.execute(
                'SELECT m.category AS Category, d.amount AS Total, d.transaction_date AS Date'
                ' FROM debit d JOIN merchant_to_category m ON d.descr = m.merchant'
            )
        
        df = pd.DataFrame(df)

        df.columns = ['Category', 'Total', 'Date']

        df['Date'] = df['Date'].astype('datetime64[ns]')

        df['Week Number'] = df['Date'].dt.isocalendar().week

        df = df.groupby(by=['Week Number', 'Category']).aggregate({'Total': sum})

        df = df.add_suffix('_by_week').reset_index()
        
        df = df[df['Week Number'] > 5]

        df = df[(df['Category'] == category_chosen)]

        return pd.DataFrame(df)
    

    # Add controls to build the interaction
    @callback(
        Output(component_id='controls-and-graph', component_property='figure'),
        Input(component_id='controls-and-radio-item', component_property='value'),
        Input(component_id='controls-sub-radio-item', component_property='value')
    )
    def update_graph(graph_chosen, category_chosen):
        if graph_chosen == 'Yearly':
            df = get_yearly_category_spend_data()
            fig = px.pie(df, values=1, names=0, title='Category Spending')
        elif graph_chosen == 'Weekly':
            df = get_weekly_category_spend_data(category_chosen)
            # fig = px.pie(df, values='Total_by_week', names='Category', title='Category Spending')
            fig = px.line(df, x='Week Number', y='Total_by_week')
        return fig
    
    # return dash_app.server