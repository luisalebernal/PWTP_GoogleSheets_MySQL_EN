import dash
from dash import html
from dash import dcc
import plotly.express as px
import pandas as pd
from pandas.io import sql
import numpy as np
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input, State
import plotly.graph_objects as go
from datetime import datetime
import dash_daq as daq
# Importar hojas de trabajo de google drive     https://bit.ly/3uQfOvs
from googleapiclient.discovery import build
from google.oauth2 import service_account
from datetime import datetime
import time
import mysql.connector
import pymysql
from sqlalchemy import create_engine

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SANDSTONE])
app.css.append_css({'external_url': '/static/reset.css'})
app.server.static_folder = 'static'
server = app.server

app.layout = dbc.Container([


    dbc.Row([
        dbc.Col([dbc.CardImg(
            src="/assets/Logo.jpg",

            style={"width": "6rem",
                   'text-align': 'right'},
        ),

        ], align='right', width=2),
        dbc.Col(html.H5(
            '“Any sufficiently advanced technology is indistinguishable from magic” - Arthur C. Clarke '),
                style={'color': "green", 'font-family': "Franklin Gothic"}, width=7),

    ]),
    dbc.Row([
        dbc.Col(html.H1(
            "Data Entry - Google Sheets to MySQL in the Cloud - CL-800C Clarifier - Barrancabermeja Refinery",
            style={'textAlign': 'center', 'color': '#082255', 'font-family': "Franklin Gothic"}), width=12, )
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Accordion([
                dbc.AccordionItem([
                    html.H5([
                                'The following app sends the data from a google sheets file to MySQL cloud databases located at Clever Console and Railway'])

                ], title="Introduction"),
            ], start_collapsed=True, style={'textAlign': 'left', 'color': '#082255', 'font-family': "Franklin Gothic"}),

        ], style={'color': '#082255', 'font-family': "Franklin Gothic"}),
    ]),
    dbc.Row([
        dbc.Col([
            html.Button('Enter', id='ingresar', n_clicks=0),
            dbc.Spinner(children=[html.Div(id='mensaje-de-exito', children='Press "Enter" to send the data from Google Sheets to MYSQL.')], size="lg", color="primary",
                                                            type="border", fullscreen=True, ),

        ])

    ]),
])

@app.callback(
    Output('mensaje-de-exito', 'children'),
    Input('ingresar', 'n_clicks'),

)
def update_output(n_clicks):

    if n_clicks >= 1:
        start = time.time()
        # Extraer Fase 5 de google sheets

        namesSQL = ['Fecha PURGAS', 'Hora Inicio PURGAS', 'Hora Fin PURGAS', 'Altura Inicial [m] PURGAS',
                    'Altura Final [m] PURGAS', 'Fase PURGAS', 'Vacio 1', 'Vacio 2', 'Vacio 3',
                    'Fecha LODOS', 'Hora Inicio LODOS', 'Hora Fin LODOS', 'Altura Inicial [m] LODOS',
                    'Altura Final [m] LODOS', 'Fase LODOS', 'Vacio 4', 'Vacio 5', 'Vacio 6', 'Fecha CLR',
                    'Hora Inicio CLR', 'Hora Fin CLR', 'Lectura Inicial CLR', 'Lectura Final CLR', 'Turbidez [NTU] CLR',
                    'Color [Pt-Co] CLR', 'pH CLR', 'Fase CLR', 'Vacio 7', 'Vacio 8', 'Vacio 9', 'Fase', 'Numero',
                    'Largo', 'Ancho', 'Fecha', 'Hora', 'Altura Promedio', 'Capacidad [m3]', 'Referencia', 'Link']

        SERVICE_ACCOUNT_FILE = 'keys-PTAP.json'
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        creds = None
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)

        # The ID spreadsheet.
        SAMPLE_SPREADSHEET_ID = '1hT5gjZ8QES6GtPmnoxhmR3NG8xyzf0kFUfd7sunzV70'

        SAMPLE_RANGE_COMBINADO = "Fase 5 MySQL"

        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result_COMBINADO = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                              range=SAMPLE_RANGE_COMBINADO).execute()

        dfCOMBINADO3 = result_COMBINADO.get('values', [])
        dfCOMBINADO3 = pd.DataFrame(dfCOMBINADO3, columns=namesSQL)
        dfCOMBINADO3 = dfCOMBINADO3.drop('Link', axis=1)
        dfCOMBINADO3.drop([0], inplace=True)
        dfCOMBINADO3 = dfCOMBINADO3.rename(index=lambda x: x - 1)

        # Realiza conexión con phpMyAdmin Clever Console y transfiere los datos

        # Create SQLAlchemy engine to connect to MySQL Database
        engine = create_engine("mysql+pymysql://{user}:{pw}@{host}/{db}"
                               .format(host='bwubf7s9b4yum09xuoqq-mysql.services.clever-cloud.com',
                                       db='bwubf7s9b4yum09xuoqq', user='ubqeiuvtqvrnumdm', pw='Nedd53w8GAtIAC1EVzRh'))

        dfCOMBINADO3.to_sql(con=engine, name='datos_ptap_fase5_norm', if_exists='replace', index=False)
        end = time.time()
        t = end - start
        print('Tiempo Clever Console es:')
        print(t)

        # Realiza Back up a Railway
        now = str(datetime.now())
        print(now)
        user = 'root'
        password = 'V3QZGvts4KyQ7NxoThyP'
        host = 'containers-us-west-98.railway.app'
        port = 6520
        database = 'railway'
        start = time.time()

        enginePS = create_engine(url="mysql+pymysql://{0}:{1}@{2}:{3}/{4}".format(
            user, password, host, port, database))

        # dfCOMBINADO3.to_sql(con=enginePS, name='datos_ptap_fase5_norm', if_exists='replace', index=False)
        dfCOMBINADO3.to_sql(con=enginePS, name=now, if_exists='replace', index=False)
        end = time.time()
        t = end - start
        print('Tiempo planet scale es:')
        print(t)


    return 'Data has been successfully sent from Google sheets to MYSQL {} times'.format(
        n_clicks
    )

if __name__ == '__main__':
    app.run_server()

