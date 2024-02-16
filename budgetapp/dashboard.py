from dash import Dash, html, dcc, callback, Output, Input
from budgetapp.db import get_db
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def init_dashboard(server):
    dash_app = Dash(__name__, 
                    server=server, 
                    routes_pathname_prefix = '/dashboard/')
    
    dash_app.config.suppress_callback_exceptions = True

    dash_app.layout = html.Div([
        html.Div(children='Graphs'),
        html.Hr(),
        dcc.Dropdown(options=['Pie chart', 'Line chart', 'Bar chart'], value='Pie chart', id='which-graph'),
        html.Div([
            # dcc.Graph(figure={})
        ], id='graph')
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
        Output(component_id='graph', component_property='children'),
        Input(component_id='which-graph', component_property='value'),
    )
    def change_graph(graph_chosen):
        if graph_chosen == 'Pie chart':
            df = get_yearly_category_spend_data()
            fig = px.pie(df, values=1, names=0, title='Category Spending')
            return [dcc.Graph(figure=fig)]

        elif graph_chosen == 'Bar chart':
            df = get_weekly_category_spend_data('Dining')
            df['Average'] = df['Total_by_week'].mean()
            fig = px.bar(df, x='Week Number', y='Total_by_week')
            # TODO: figure out how to make it say 'average' and not 'trace 1'
            fig.add_traces([go.Line(x=df['Week Number'], y=df['Average'])]) # they say go.Line is deprecated
            return [dcc.RadioItems(['Average', 'Budget'], id='bar-choices'), dcc.Graph(figure=fig, id='bar-graph')]
        elif graph_chosen == 'Line chart':
            df = get_weekly_category_spend_data('Administrative')
            fig = px.line(df, x='Week Number', y='Total_by_week')
            return [dcc.Graph(figure=fig)]

    @callback(
        Output(component_id='bar-graph', component_property='figure'),
        Input(component_id='bar-choices', component_property='value'),
    )
    def update_bar_graph(trace_chosen):
        df = get_weekly_category_spend_data('Dining')

        db = get_db()

        budget_df = db.execute(
                'SELECT category, dollar_limit'
                ' FROM budget'
            )
                
        budget_df = pd.DataFrame(budget_df)
        budget_df.columns = ['Category', 'Dollar Limit']
        budget_df = budget_df.set_index('Category')

        df['Budget'] = budget_df.loc['Dining', 'Dollar Limit']
        df['Average'] = df['Total_by_week'].mean()
        fig = px.bar(df, x='Week Number', y='Total_by_week')
        # TODO: figure out how to make it say 'average' and not 'trace 1'
        fig.add_traces([go.Line(x=df['Week Number'], y=df[trace_chosen])]) # they say go.Line is deprecated

        return fig