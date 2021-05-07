import pandas as pd
import pandas_datareader.data as web
import plotly.express as px
import plotly.graph_objects as go

import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
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


def get_adj_closes(tickers, start_date='2021-01-01', end_date=None, freq='d'):
    # Fecha inicio por defecto (start_date='2010-01-01') y fecha fin por defecto (end_date=today)
    # Descargamos DataFrame con todos los datos
    closes = web.YahooDailyReader(symbols=tickers, start=start_date, end=end_date, interval=freq).read()
    # Se ordenan los índices de manera ascendente
    closes.sort_index(inplace=True)
    return closes


app.layout = html.Div(

    children=[
        dbc.Row(html.H1("DERIVATECH 36O"), justify="center", align="center", className="h-50"),

        html.Hr(),

        dbc.Row(
            children=[
                dbc.Col(
                    children=[
                        html.Span(['Ingrese un Ticker:']),
                        dcc.Input(
                            id='ticker',
                            type='text',
                            placeholder='Ingrese el Ticker'),

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

                        html.Div(id='rendimiento')
                    ],
                    width=3),

                dbc.Col(dcc.Graph(id="precio"), width=9)
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
        ticker = ticker.upper()
        df1 = get_adj_closes(ticker)

        if grafico == 'Velas':
            precio = go.Figure(data=[go.Candlestick(x=df1.index,
                                                    open=df1['Open'], high=df1['High'],
                                                    low=df1['Low'], close=df1['Close'])
                                     ])

            precio.update_layout(yaxis={'title': 'Precio'},
                                 xaxis_rangeslider_visible=False,
                                 title={'text': 'Precio {0}'.format(ticker),
                                        'font': {'size': 28}, 'x': 0.5, 'xanchor': 'center'})
        else:
            precio = px.line(df1, x=df1.index, y=['Adj Close'], height=600)
            precio.update_layout(yaxis={'title': 'Precio'},
                                 title={'text': 'Precio {0}'.format(ticker),
                                        'font': {'size': 28}, 'x': 0.5, 'xanchor': 'center'})

        if vencimiento:
            precio.add_vline(x=vencimiento)

        if strike:
            precio.add_hline(y=strike)

            opt = web.YahooOptions(ticker)
            opt = opt.get_all_data().reset_index()
            opt.set_index('Expiry')

            if direccion == 'Up':
                calls = opt.loc[(opt.Type == 'call') & (opt.Expiry == vencimiento) & (
                        opt.Strike >= opt.loc[0].Underlying_Price * 0.80 - 5) & (
                                        opt.Strike <= strike)].reset_index().drop(['index'], axis=1)

                longs = [{'K': calls['Strike'].loc[i], 'Price': calls['Ask'].loc[i]} for i in range(len(calls))]

                spreads = []

                short_p = calls['Bid'].iloc[-1]

                l = len(longs)

                for i in range(l):

                    if not longs[i]['K'] == strike:
                        prima = (longs[i]['Price'] - short_p + 12.12 / 100) / (strike - longs[i]['K'])
                        spreads.append(prima)

                result = [(1 / (i / 0.75) - 1) * 100 for i in sorted(spreads)][0]

                return (precio, 'El rendimiento de la estrategia sería de {}%'.format(result))

            else:
                puts = opt.loc[(opt.Type == 'put') & (opt.Expiry == vencimiento) & (opt.Strike >= strike) & (
                        opt.Strike <= strike * 1.25)].reset_index().drop(['index'], axis=1)

                longs = [{'K': puts['Strike'].loc[i], 'Price': puts['Ask'].loc[i]} for i in range(len(puts))]

                spreads = []

                short_p = puts['Bid'].loc[0]

                l = len(longs)

                for i in range(l):

                    if not longs[i]['K'] == strike:
                        prima = (longs[i]['Price'] - short_p + 12.12 / 100) / (longs[i]['K'] - strike)
                        spreads.append(prima)

                result = [(1 / (i / 0.75) - 1) * 100 for i in sorted(spreads)][0]

                return (precio, 'El rendimiento de la estrategia sería de {}%'.format(result))


@app.callback(
    Output('vencimiento', 'options'),
    [Input('ticker', 'value')]
)
def expiry_options(ticker):
    opt = sorted(web.YahooOptions(ticker).get_all_data().reset_index().Expiry.unique())
    vencimiento = ([pd.to_datetime(str(i)).strftime('%Y-%m-%d') for i in opt])

    return [{'label': opt, 'value': opt} for opt in vencimiento]


@app.callback(
    Output('strike', 'options'),
    [Input('vencimiento', 'value'),
     Input('ticker', 'value')]
)
def options_strikes(vencimiento, ticker):
    opts = web.YahooOptions(ticker).get_all_data().reset_index()
    opts = opts.loc[(opts.Expiry == vencimiento) &
                    (opts.Strike >= opts.loc[0].Underlying_Price * 0.70) &
                    (opts.Strike <= opts.loc[0].Underlying_Price * 1.30)]

    return [{'label': opt, 'value': opt} for opt in sorted(opts.Strike.unique())]


if __name__ == '__main__':
    app.run_server(debug=False)

