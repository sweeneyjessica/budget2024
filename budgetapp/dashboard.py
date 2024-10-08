from dash import Dash, html, dcc, callback, Output, Input, exceptions, dash_table
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
                ' FROM debit d JOIN merchants m ON d.descr = m.merchant'
                ' GROUP BY m.category'
            )

        return pd.DataFrame(df)

    def get_weekly_category_spend_data(category_chosen):
        db = get_db()

        df = db.execute(
                'SELECT m.category AS Category, '
                '       d.amount AS Total, '
                '       substr(d.transaction_date, 0, 5) AS Year, '
                '       substr(d.transaction_date, 6, 2) AS Month, '
                '       substr(d.transaction_date, 9, 2) AS Day, '
                '       w.quarter as Week_Number'
                ' FROM debit d '
                ' JOIN merchants m ON d.descr = m.merchant'
                ' JOIN weekly_quarters w on Day = w.day_of_month'
            )
        
        df = pd.DataFrame(df)

        df.columns = ['Category', 'Total', 'Year', 'Month', 'Day', 'Week_Number']
        df['x_axis'] = df['Year'].astype(str)+df['Month'].astype(str)+df['Week_Number'].astype(str)

        df = df.groupby(by=['x_axis', 'Category']).aggregate({'Total': sum})

        df = df.add_suffix('_by_week').reset_index()
        
        df = df[(df['Category'] == category_chosen)]

        return pd.DataFrame(df)
    

    def get_categories():
        db = get_db()

        df = db.execute(
            'SELECT DISTINCT category AS Category FROM merchants'
        )
        df = pd.DataFrame(df)
        df.columns=['Category']

        return df['Category'].tolist()

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
            categories = get_categories()
            return [dcc.Dropdown(categories, id='category-choices'), dcc.Graph(figure={}, id='bar-graph')]
        elif graph_chosen == 'Line chart':
            categories = get_categories()
            return [dcc.Dropdown(categories, id='category-choices'), dcc.Graph(figure={}, id='line-graph')]
        
    @callback(
        Output(component_id='bar-graph', component_property='figure'),
        Input(component_id='category-choices', component_property='value'), 
    )
    def select_bar_category(category_chosen):
        df = get_weekly_category_spend_data(category_chosen)

        df['Average'] = df['Total_by_week'].mean()
        fig = px.bar(df, x='x_axis', y='Total_by_week')
        # TODO: figure out how to make it say 'average' and not 'trace 1'
        fig.add_traces([go.Line(x=df['x_axis'], y=df['Average'])]) # they say go.Line is deprecated

        return fig
    

    @callback(
        Output(component_id='line-graph', component_property='figure'),
        Input(component_id='category-choices', component_property='value'), 
    )
    def select_bar_category(category_chosen):
        df = get_weekly_category_spend_data(category_chosen)

        fig = px.line(df, x='x_axis', y='Total_by_week')
        return fig


    # @callback(
    #     Output(component_id='bar-graph', component_property='figure'),
    #     Input(component_id='bar-choices', component_property='value'),
    #     Input(component_id='category-choices', component_property='value')
    # )
    # def update_bar_graph(trace_chosen, category_chosen):
    #     df = get_weekly_category_spend_data(category_chosen)

    #     db = get_db()

    #     budget_df = db.execute(
    #             'SELECT category, dollar_limit'
    #             ' FROM budget'
    #         )
                
    #     budget_df = pd.DataFrame(budget_df)
    #     budget_df.columns = ['Category', 'Dollar Limit']
    #     budget_df = budget_df.set_index('Category')

    #     df['Budget'] = budget_df.loc[category_chosen, 'Dollar Limit']
    #     df['Average'] = df['Total_by_week'].mean()
    #     fig = px.bar(df, x='Week Number', y='Total_by_week')
    #     # TODO: figure out how to make it say 'average' and not 'trace 1'
    #     fig.add_traces([go.Line(x=df['Week Number'], y=df[trace_chosen])]) # they say go.Line is deprecated

    #     return fig

    @callback(
        Output("table-container", "children"),
        Input("bar-graph", "clickData"),
    )
    def fig_click(clickData):
        if not clickData:
            raise exceptions.PreventUpdate
        
        df = get_weekly_category_spend_data('Dining')

        tab = dash_table.DataTable(
            data=df.loc[df["x_axis"].eq(clickData["points"][0]["x"])]
            .tail(5)
            .to_dict("records"),
            columns=[{"name": i, "id": i} for i in df.columns],
        )

        return tab