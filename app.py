import pandas as pd
import pandas_datareader.data as web
import plotly.express as px

import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash

from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_auth

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server


auth = dash_auth.BasicAuth(
    app,
    {'marcos': 'derivatech',
     'andres': 'derivatech',
     'angel': 'derivatech',
     'eduardo': 'derivatech',
     'horacio': 'derivatech'}
)


def get_adj_closes(tickers, start_date='2021-01-01', end_date=None, freq='d'):
    # Fecha inicio por defecto (start_date='2010-01-01') y fecha fin por defecto (end_date=today)
    # Descargamos DataFrame con todos los datos
    closes = web.YahooDailyReader(symbols=tickers, start=start_date, end=end_date, interval=freq).read()['Adj Close']
    # Se ordenan los índices de manera ascendente
    closes.sort_index(inplace=True)
    return closes


app.layout = html.Div(

    children=[
        dbc.Row(html.H1("Simulador de Estrategias"), justify="center", align="center", className="h-50"),

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
     State('strike', 'value')]
)
def build_graph(boton, ticker, vencimiento, strike):
    if ticker is None:
        raise PreventUpdate
    else:
        ticker = ticker.upper()
        df1 = get_adj_closes(ticker)
        precio = px.line(df1, x=df1.index, y=['Adj Close'], height=600)
        precio.update_layout(yaxis={'title': 'Adj Close Price'},
                             title={'text': 'Precio_{0}'.format(ticker),
                                    'font': {'size': 28}, 'x': 0.5, 'xanchor': 'center'})

        if vencimiento:
            precio.add_vline(x=vencimiento)

        if strike:
            precio.add_hline(y=strike)

            opt = web.YahooOptions(ticker)
            opt = opt.get_all_data().reset_index()
            opt.set_index('Expiry')
            calls = opt.loc[(opt.Type == 'call') & (opt.Expiry == vencimiento) & (
                        opt.Strike >= opt.loc[0].Underlying_Price * 0.80 - 5) & (
                                        opt.Strike <= strike)].reset_index().drop(['index'], axis=1)

            spreads_dic = {
                'Long': [{'K': calls['Strike'].loc[i], 'Price': calls['Ask'].loc[i]} for i in range(len(calls))],
                'Short': [{'K': calls['Strike'].loc[i], 'Price': calls['Bid'].loc[i]} for i in range(len(calls))]}

            spreads = pd.DataFrame(columns=['Long K', 'Short K', 'Long Price', 'Short Price', 'Spread', 'Prima'])

            l = len(spreads_dic['Long'])

            for i in range(l):

                for k in range(len(spreads_dic['Short']) - i):
                    long_k = spreads_dic['Long'][i]['K']
                    short_k = spreads_dic['Short'][k + i]['K']
                    if not long_k == short_k:
                        spreads.loc[k + i * l, 'Long K'] = long_k
                        spreads.loc[k + i * l, 'Short K'] = short_k
                        spread = short_k - long_k
                        spreads.loc[k + i * l, 'Spread'] = spread
                        long_p = spreads_dic['Long'][i]['Price']
                        short_p = spreads_dic['Short'][k + i]['Price']
                        spreads.loc[k + i * l, 'Long Price'] = long_p
                        spreads.loc[k + i * l, 'Short Price'] = short_p
                        prima = (long_p - short_p + 12.16 / 100) / (short_k - long_k)
                        spreads.loc[k + i * l, 'Prima'] = prima

            spreads = spreads.loc[spreads.Spread != 0].sort_index().reset_index().drop(['index'], axis=1)

            result = spreads.loc[spreads['Short K'] == strike].sort_values('Prima')
            result['Rend Real'] = (1 / result.Prima - 1) * 100
            result['Rend Cliente'] = (1 / (result.Prima / 0.75) - 1) * 100
            result['Break even'] = result['Long K'] + result.Prima * (result['Short K'] - result['Long K'])
            result['Spread Cost'] = (result['Long Price'] - result['Short Price']) * 100 + 12.16
            result['Spread Price'] = result['Spread Cost'] / 0.8
            result = result.reset_index().drop(['index'], axis=1)

            result = result['Rend Cliente'][0].round(2)

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
    opts = opts.loc[opts.Expiry == vencimiento]

    return [{'label': opt, 'value': opt} for opt in sorted(opts.Strike.unique())]


if __name__ == '__main__':
    app.run_server(debug=True)

