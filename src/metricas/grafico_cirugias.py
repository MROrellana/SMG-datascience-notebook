import dash
import dash_html_components as html
import dash_core_components as dcc
import pandas as pd
from dash.dependencies import Input, Output
import dash_table
import unidecode
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from server import server

from dbconn import querydb, querydbtopandas 

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css 5", 
                        'https://codepen.io/amyoshino/pen/jzXypZ.css']

App_1 = dash.Dash(__name__, server=server, url_base_pathname='/grafico_cirugias/', external_stylesheets=external_stylesheets )


colors = {'text': 'grey'}


App_1.layout = html.Div([
    html.Div([
        html.H1(
            children='Plots prestadores',
            className='twelve columns',
            style={
                'textAlign': 'center',
                'color': colors['text']
        })

    
    ]),

    
    
    html.Div([
        html.Div([
            html.P('Inserte el id del prestador a visualizar')
    ]),
    html.Div([
        dcc.Input(id="prestador", type="number", placeholder = "id prestador aquí"),
    ]),
    ],

    style={"width": "15%", "float": "left"}
    ),


    html.Div([
        html.Div([
        dcc.Graph(id="fig_cirugias", style={"width": "85%", "display": "inline-block"}, animate=None)
                 ]  #style={"margin-top": "110px", "margin-bottom": "1px"} #"margin-left" : "10px"} 
    ),
    
])
    
])


@App_1.callback(Output('fig_cirugias', 'figure'),
     [Input('prestador', "value")])
def calculo_graficos(prestador): 
    fechas = [i for i in os.listdir('datos_cirugias/') if len(i) == 12]
    fechas.sort()
    temporal_prestador = pd.DataFrame(columns= ["cirugías"], data= ["porcentaje de cirugías en centros propios", "porcentaje de cirugías en centros no propios"])
    temporal_total = pd.DataFrame(columns= ["cirugías"], data= ["porcentaje de cirugías en centros propios", "porcentaje de cirugías en centros no propios"])
    for i in fechas:
        #final = pd.read_parquet(f'datos_cirugias/{i}')  
        final = pd.read_parquet()  
        propios = final["Propias"].sum()
        no_propios = final["No propias"].sum()
        total = propios + no_propios
        ar = [propios / total , no_propios /total]
        temporal_total[i[:7] ] = ar
        final_prestador = final[final["Prestador"] == prestador]
        final_prestador['porcentaje de cirugías en centros propios'] = final_prestador["Propias"] / final_prestador["Total general"]
        final_prestador['porcentaje de cirugías en centros no propios' ] = final_prestador["No propias"] / final_prestador["Total general"]
        temporal_prestador[i[:7]] = final_prestador[["porcentaje de cirugías en centros no propios", "porcentaje de cirugías en centros propios"]].values[0]
        
    temporal_total = temporal_total.melt(id_vars = ["cirugías"] ,value_vars = temporal_total.columns[1:].values)
    temporal_total["tipo"] = "general"
    temporal_prestador = temporal_prestador.melt(id_vars = ["cirugías"],value_vars = temporal_prestador.columns[1:].values)
    temporal_prestador["tipo"] = "Prestador"
    final = pd.concat([temporal_prestador, temporal_total]).round(2)

    final.rename(columns={"value": "porcentaje"},inplace=True)
    
    fig_cirugias = px.bar(final, x="tipo", y="porcentaje", color="cirugías", barmode="stack",
             facet_col="variable", 
             color_discrete_map = {"porcentaje de cirugías en centros propios": "#0080ff",
                                  "	porcentaje de cirugías en centros no propios": "#ccccff"})
    fig_cirugias.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))  
    for i in range(0,13):
        fig_cirugias.data[i]["marker"]["color"] = "#45b6fe"

    for i in range(13,26):
        fig_cirugias.data[i]["marker"]["color"] = "#3792cb"

    fig_cirugias.layout.xaxis1.tickangle = -90
    fig_cirugias.layout.xaxis2.tickangle = -90
    fig_cirugias.layout.xaxis3.tickangle = -90
    fig_cirugias.layout.xaxis4.tickangle = -90
    fig_cirugias.layout.xaxis5.tickangle = -90
    fig_cirugias.layout.xaxis5.tickangle = -90
    fig_cirugias.layout.xaxis6.tickangle = -90
    fig_cirugias.layout.xaxis7.tickangle = -90
    fig_cirugias.layout.xaxis8.tickangle = -90
    fig_cirugias.layout.xaxis9.tickangle = -90
    fig_cirugias.layout.xaxis10.tickangle = -90
    fig_cirugias.layout.xaxis11.tickangle = -90
    fig_cirugias.layout.xaxis12.tickangle = -90
    fig_cirugias.layout.xaxis13.tickangle =-90

    fig_cirugias.layout.xaxis1.title = None
    fig_cirugias.layout.xaxis2.title = None
    fig_cirugias.layout.xaxis3.title = None
    fig_cirugias.layout.xaxis4.title = None
    fig_cirugias.layout.xaxis5.title = None
    fig_cirugias.layout.xaxis5.title = None
    fig_cirugias.layout.xaxis6.title = None
    fig_cirugias.layout.xaxis7.title = None
    fig_cirugias.layout.xaxis8.title = None
    fig_cirugias.layout.xaxis9.title = None
    fig_cirugias.layout.xaxis10.title = None
    fig_cirugias.layout.xaxis11.title = None
    fig_cirugias.layout.xaxis12.title = None
    fig_cirugias.layout.xaxis13.title = None

    fig_cirugias.layout.legend = {"orientation": "h", "xanchor" :"center", "y":1.14, "x":0.5}

    fig_cirugias.update_yaxes(range=[-0,1],tickformat = "%")
    
    return fig_cirugias
    
    
