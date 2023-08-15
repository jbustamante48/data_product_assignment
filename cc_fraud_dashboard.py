import pandas as pd
import plotly.express as px
import plotly.io as pio  # Import the plotly.io module
from dash import Dash, dcc, html, dash_table, Input, Output, State
import base64
import datetime
import io
import warnings
warnings.filterwarnings('ignore')

fraud_data = pd.read_csv("/Users/JP/Desktop/fraudTrain.csv")

fraud_data = fraud_data.drop(['Unnamed: 0'], axis=1)

app = Dash(__name__)

app.layout = html.Div([
    html.Button("Help", id='help-button'),
    html.Div(id='help-modal', style={'display': 'none'}, children=[
        html.H2("Dashboard Help"),
        html.P("Welcome to the dashboard! Here's some information to get you started."),
        html.P("The upload data feature allows a drag and drop of a CSV or Excel file to view a dataset. The first "
               "scatterplot shows the relationship between fraudulent transactions, gender, and transaction amount. "
               "The second scatterplot shows the relationship between fraudulent transactions, gender, "
               "and city population. Both graphs can be viewed at an individual transaction category. Fraudulent "
               "transactions can be seen in yellow. Legitimate transactions can be seen in blue. The purpose of this "
               "dashboard is to provide insight into what I believe are the key variables with this dataset as it "
               "relates to credit card fraud."),
        html.Button("Close", id='close-help-button')
    ]),
    html.H1('Upload Data Set'),
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        multiple=True
    ),
    html.Div(id='output-data-upload'),

    html.H1('Fraudulent Transactions by Transaction Category'),
    html.H3('Compared to Gender and Amount'),
    dcc.Dropdown(
        id="dropdown",
        options=["misc_net", "grocery_pos", "entertainment", "gas_transport", "misc_pos", "grocery_net", "shopping_net", "shopping_pos", "food_dining", "personal_care", "health_fitness", "travel", "kids_pets", "home"],
        value="misc_net",
        clearable=False,
    ),
    dcc.Graph(id="graph"),
    html.A("Download Graph", id='download-link1', download="graph.pdf", href="", target="_blank"),

    html.H1('Fraudulent Transactions by Transaction Category'),
    html.H3('Compared to Gender and City Population'),

    dcc.Graph(id="graph2"),
    html.A("Download Graph", id='download-link2', download="graph2.pdf", href="", target="_blank"),
])

def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return html.Div([
        html.H5(filename),
        html.H6(datetime.datetime.fromtimestamp(date)),

        dash_table.DataTable(
            df.to_dict('records'),
            [{'name': i, 'id': i} for i in df.columns]
        ),

        html.Hr(),

        html.Div('Raw Content'),
        html.Pre(contents[0:200] + '...', style={
            'whiteSpace': 'pre-wrap',
            'wordBreak': 'break-all'
        })
    ])

# Define separate callback functions for the two graphs
@app.callback(
    Output("graph", "figure"),
    Input("dropdown", "value"),
)
def update_bar_chart1(selected_category):
    mask = fraud_data['category'] == selected_category
    fig = px.scatter(fraud_data[mask], x='amt', y='gender', color='is_fraud', title=f'Fraudulent Transactions in {selected_category}')
    return fig

@app.callback(
    Output("graph2", "figure"),
    Input("dropdown", "value"),
)
def update_bar_chart2(selected_category):
    mask2 = fraud_data['category'] == selected_category
    fig2 = px.scatter(fraud_data[mask2], x='city_pop', y='gender', color='is_fraud', title=f'Fraudulent Transactions in {selected_category}')
    return fig2

@app.callback(
    Output('help-modal', 'style'),
    Input('help-button', 'n_clicks'),
    Input('close-help-button', 'n_clicks')
)
def display_help_modal(n_clicks_help, n_clicks_close):
    if n_clicks_help is None and n_clicks_close is None:
        return {'display': 'none'}
    if n_clicks_help is not None:
        return {'display': 'block'}
    if n_clicks_close is not None:
        return {'display': 'none'}

@app.callback(
    Output('download-link1', 'href'),
    Output('download-link1', 'target'),  # Specify the target attribute
    Input('download-link1', 'n_clicks'),
    State('dropdown', 'value'),  # Include the dropdown value as state
)
def update_download_link(n_clicks, selected_category):
    if n_clicks is None:
        return "", "_blank"  # Open in a new tab

    mask = fraud_data['category'] == selected_category
    fig = px.scatter(fraud_data[mask], x='amt', y='gender', color='is_fraud', title=f'Fraudulent Transactions in {selected_category}')

    # Generate a downloadable image of the graph
    img_buffer = io.BytesIO()
    pio.write_image(fig, img_buffer, format="pdf", engine="kaleido")  # Use 'fig' here
    img_buffer.seek(0)
    img_string = base64.b64encode(img_buffer.read()).decode()

    # Define the download link URL
    download_url = f"data:application/pdf;base64,{img_string}"

    return download_url, "_blank"  # Open in a new tab

@app.callback(
    Output('download-link2', 'href'),
    Output('download-link2', 'target'),  # Specify the target attribute
    Input('download-link2', 'n_clicks'),
    State('dropdown', 'value'),  # Include the dropdown value as state
)
def update_download_link(n_clicks, selected_category):
    if n_clicks is None:
        return "", "_blank"  # Open in a new tab

    mask2 = fraud_data['category'] == selected_category
    fig2 = px.scatter(fraud_data[mask2], x='city_pop', y='gender', color='is_fraud', title=f'Fraudulent Transactions in {selected_category}')

    # Generate a downloadable image of the graph
    img_buffer = io.BytesIO()
    pio.write_image(fig2, img_buffer, format="pdf", engine="kaleido")  # Use 'fig2' here
    img_buffer.seek(0)
    img_string = base64.b64encode(img_buffer.read()).decode()

    # Define the download link URL
    download_url = f"data:application/pdf;base64,{img_string}"

    return download_url, "_blank"  # Open in a new tab

if __name__ == '__main__':
    app.run_server(debug=True)