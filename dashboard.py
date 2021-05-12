import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests

import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_table
import dash

from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_auth

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
#server = app.server


auth = dash_auth.BasicAuth(
    app,
    {'marcos': 'derivatech',
     'andres': 'derivatech',
     'angel': 'derivatech',
     'eduardo': 'derivatech',
     'horacio': 'derivatech',
     'cinthia': 'derivatech'}
)

dt = pd.DataFrame(columns=['Subyacente', 'Precio_objetivo', 'Fecha_vencimiento', 'Direccion', 'Rendimiento'])

app.layout = html.Div(

    children=[
        dbc.Row(html.H1("DERIVATECH 36O"), justify="center", align="center", className="h-50"),

        html.Hr(),

        dbc.Row(
            children=[
                dbc.Col(width=1),

                dbc.Col(
                    children=[
                        html.Span(['Ingrese un Ticker:']),
                        dcc.Input(
                            id='ticker',
                            type='text',
                            placeholder='Ingrese el Ticker'),

                        html.Br(),

                        html.Div(id='subyacente', style={'text-align': 'center'}),

                        html.Span(['Fecha de vencimiento:']),
                        dcc.Dropdown(id='vencimiento'),

                        html.Span(['Selecciona un Strike:']),
                        dcc.Dropdown(id='strike'),

                        html.Br(),

                        html.Span(['Dirección']),
                        dcc.Dropdown(id='direccion',
                                     options=[
                                         {'label': 'Up', 'value': 'Up'},
                                         {'label': 'Down', 'value': 'Down'}
                                     ],
                                     value='Up'),

                        html.Br(),

                        html.Span(['Tipo de gráfico']),
                        dcc.Dropdown(id='grafico',
                                     options=[
                                         {'label': 'Linear', 'value': 'Linear'},
                                         {'label': 'Velas', 'value': 'Velas'}
                                     ],
                                     value='Velas'),

                        html.Br(),

                        html.Button('Graficar', id='boton_1', n_clicks=0),

                        html.Br(),

                        html.Div(id='rendimiento', style={'text-align': 'center'}),

                        html.Br(),

                        html.Button('Guardar', id='boton_2', n_clicks=0),

                    ],
                    width=3),

                dbc.Col(
                    children=[
                        dcc.Graph(id="precio"),

                        dash_table.DataTable(
                            id='table',
                            columns=(
                                [{'id': c, 'name': c} for c in dt.columns]
                            ),
                            data=[]
                        )
                    ], width=7),

                dbc.Col(width=1)

            ])
    ])


@app.callback(
    [Output('precio', 'figure'),
     Output('rendimiento', 'children')],
    [Input('boton_1', 'n_clicks')],
    [State('ticker', 'value'),
     State('vencimiento', 'value'),
     State('strike', 'value'),
     State('direccion', 'value'),
     State('grafico', 'value')]
)
def build_graph(boton, ticker: str, vencimiento, strike, direccion, grafico):
    if ticker is None:
        raise PreventUpdate
    else:
        response = requests.get('https://sandbox.tradier.com/v1/markets/history',
                                params={'symbol': ticker, 'interval': 'daily', 'start': '2021-01-01'},
                                headers={'Authorization': 'Bearer FPgRB3GGnWkgtDMS77RpLggrcd8d',
                                         'Accept': 'application/json'}
                                )
        json_response = response.json()

        df1 = pd.DataFrame(json_response['history']['day'])

        if grafico == 'Velas':
            precio = go.Figure(data=[go.Candlestick(x=df1['date'],
                                                    open=df1['open'], high=df1['high'],
                                                    low=df1['low'], close=df1['close'])
                                     ])

            precio.update_layout(yaxis={'title': 'Precio'},
                                 xaxis_rangeslider_visible=False,
                                 title={'text': 'Precio {0}'.format(ticker.upper()),
                                        'font': {'size': 28}, 'x': 0.5, 'xanchor': 'center'})
        elif grafico == 'Linear':
            precio = px.line(df1, x=df1['date'], y=['close'], height=400)
            precio.update_layout(yaxis={'title': 'Precio'},
                                 title={'text': 'Precio {0}'.format(ticker.upper()),
                                        'font': {'size': 28}, 'x': 0.5, 'xanchor': 'center'})

        if vencimiento:
            precio.add_vline(x=vencimiento)

        if strike:
            precio.add_hline(y=strike)

            underlying_price = df1.iloc[-1].close

            response = requests.get('https://sandbox.tradier.com/v1/markets/options/chains',
                                    params={'symbol': ticker, 'expiration': vencimiento, 'greeks': 'false'},
                                    headers={'Authorization': 'Bearer FPgRB3GGnWkgtDMS77RpLggrcd8d',
                                             'Accept': 'application/json'}
                                    )
            json_response = response.json()
            chain = pd.DataFrame(json_response['options']['option'])

            if direccion == 'Up':
                calls = chain.loc[(chain.option_type == 'call') &
                                  (chain.strike >= underlying_price * 0.80 - 5) &
                                  (chain.strike <= strike)].reset_index().drop(['index'], axis=1)

                longs = [{'K': calls['strike'].loc[i], 'Price': calls['ask'].loc[i]} for i in range(len(calls))]

                spreads = []

                short_p = calls.iloc[-1]['bid']

                l = len(longs)

                for i in range(l):

                    if not longs[i]['K'] == strike:
                        prima = (longs[i]['Price'] - short_p + 12.12 / 100) / (strike - longs[i]['K'])
                        spreads.append(prima)

                result = [(1 / (i / 0.75) - 1) * 100 for i in sorted(spreads)][0]

                return (precio, '{}%'.format(round(result, 2)))

            else:
                puts = chain.loc[(chain.option_type == 'put') &
                                 (chain.strike >= strike) &
                                 (chain.strike <= strike * 1.25)].reset_index().drop(['index'], axis=1)

                longs = [{'K': puts['strike'].loc[i], 'Price': puts['ask'].loc[i]} for i in range(len(puts))]

                spreads = []

                short_p = puts['bid'].loc[0]

                l = len(longs)

                for i in range(l):

                    if not longs[i]['K'] == strike:
                        prima = (longs[i]['Price'] - short_p + 12.12 / 100) / (longs[i]['K'] - strike)
                        spreads.append(prima)

                result = [(1 / (i / 0.75) - 1) * 100 for i in sorted(spreads)][0]

                return (precio, '{}%'.format(round(result, 2)))


@app.callback(
    Output('subyacente', 'children'),
    [Input('ticker', 'value')]
)
def precio_subyacente(ticker):
    response = requests.get('https://sandbox.tradier.com/v1/markets/quotes',
                            params={'symbols': ticker, 'greeks': 'false'},
                            headers={'Authorization': 'Bearer FPgRB3GGnWkgtDMS77RpLggrcd8d',
                                     'Accept': 'application/json'}
                            )
    json_response = response.json()

    return 'El precio actual de la acción es de ${}'.format(json_response['quotes']['quote']['last'])


@app.callback(
    Output('vencimiento', 'options'),
    [Input('ticker', 'value')]
)
def expiry_options(ticker):
    response = requests.get('https://sandbox.tradier.com/v1/markets/options/expirations',
                            params={'symbol': 'AAPL', 'includeAllRoots': 'true', 'strikes': 'false'},
                            headers={'Authorization': 'Bearer FPgRB3GGnWkgtDMS77RpLggrcd8d',
                                     'Accept': 'application/json'}
                            )
    json_response = response.json()
    return [{'label': opt, 'value': opt} for opt in json_response['expirations']['date']]


@app.callback(
    Output('strike', 'options'),
    [Input('vencimiento', 'value'),
     Input('ticker', 'value')]
)
def options_strikes(vencimiento, ticker):
    response = requests.get('https://sandbox.tradier.com/v1/markets/options/strikes',
                            params={'symbol': ticker, 'expiration': vencimiento},
                            headers={'Authorization': 'Bearer FPgRB3GGnWkgtDMS77RpLggrcd8d',
                                     'Accept': 'application/json'}
                            )
    json_response = response.json()

    return [{'label': opt, 'value': opt} for opt in json_response['strikes']['strike']]


@app.callback(
    Output('table', 'data'),
    Input('boton_2', 'n_clicks'),
    [State('table', 'data'),
     State('table', 'columns'),
     State('ticker', 'value'),
     State('strike', 'value'),
     State('vencimiento', 'value'),
     State('direccion', 'value'),
     State('rendimiento', 'children')]
)
def add_row(n_clicks, rows, columns, ticker, strike, vencimiento, direccion, rendimiento):
    info = {'Subyacente': ticker.upper(),
            'Precio_objetivo': strike,
            'Fecha_vencimiento': vencimiento,
            'Direccion': direccion,
            'Rendimiento': rendimiento}
    if rows:
        rows.append({c['id']: info[c['id']] for c in columns})
    else:
        rows = [{c['id']: info[c['id']] for c in columns}]

    return rows


if __name__ == '__main__':
    app.run_server(debug=False)

