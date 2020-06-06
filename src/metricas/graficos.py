import dash
import dash_html_components as html
import dash_core_components as dcc
import pandas as pd
import numpy as np
from dash.dependencies import Input, Output
import dash_table

import unidecode
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from server import server
from dbconn import querydb, querydbtopandas 
import os

import dash_bootstrap_components as dbc


external_stylesheets = [dbc.themes.BOOTSTRAP, "https://codepen.io/chriddyp/pen/bWLwgP.css 5", 
                        'https://codepen.io/amyoshino/pen/jzXypZ.css']

#external_stylesheets = [dbc.themes.BOOTSTRAP]                     

App_1 = dash.Dash(__name__, server=server, url_base_pathname='/graficos/', external_stylesheets=external_stylesheets )

colors = {'text': 'grey'}


App_1.layout = html.Div([
    html.Div([
        html.H1(
            children='Plots prestadores',
            className='twelve columns',
            style={
                'textAlign': 'center',
                'color': colors['text'],
                "margin-top": 15
        })

    
    ]),

    
    
    html.Div([
        dbc.Row([
            dbc.Col(html.Div(html.P('Inserte el id del prestador a visualizar'), style={"margin-top" : 10}),
                    width={"size": 3, "offset": 4,  "order": 1,}, ),
            dbc.Col(dcc.Input(id="prestador", type="number", placeholder = "id prestador aquí"), 
                    width={"size": 3, "offset": 0,  "order": 2,}, 
                   )]), 
        
        dbc.Row([
            dbc.Col(html.Div(html.P('Nombre del prestador seleccionado:')),
                    width={"size": 3, "offset": 4,  "order": 1,}, ),
            dbc.Col(html.Div(html.Div(id="prestador_nombre")),
                    width={"size": 3, "offset": 0,  "order": 2,}, 
                   
                   )]),
        
        dbc.Row([
            dbc.Col(html.Div(html.P('Especialidad del prestador seleccionado:')),
                    width={"size": 3, "offset": 4,  "order": 1,}, ),
            dbc.Col(html.Div(html.Div(id="especialidad")),
                    width={"size": 3, "offset": 0,  "order": 2,}, 
                   
                   )]), 
              
    
    ],style={"width": "100%",} ),
    
    


    html.Div([
        html.Div([
        dcc.Graph(id="fig_consultas", style={"width": "100%", "display": "inline-block"}, animate=None)
                 ]  #style={"margin-top": "110px", "margin-bottom": "1px"} #"margin-left" : "10px"} 
    ),
    
    ]),
    
    html.Div(
        dbc.Row([
            dbc.Col(dcc.Graph(id="fig_calificaciones", animate=None), width= {"order": "first", "size": 6},
                ),
            dbc.Col([
                dbc.Row(dcc.Graph(id="fig_quejas", animate=None)),
                dbc.Row(dcc.Graph(id="fig_desconocimientos", animate=None)),
                
            ], width ={"order": "last", "size": 6})
        
        ]
        
        )),
    
    html.Div(
        dbc.Row([
            dbc.Col(dcc.Graph(id="fig_imagenes", animate=None), width= {"order": "first", "size": 6},
                ),
            dbc.Col([
                dbc.Row(dcc.Graph(id="fig_cirugias", animate=None)),
                dbc.Row(dcc.Graph(id="fig_farmacia", animate=None)),
                
            ], width ={"order": "last", "size": 6})
        
        ]
        
        )),
    
    
])


@App_1.callback([Output('prestador_nombre', 'children'),
                 Output('especialidad', 'children'),
                 Output('fig_consultas', 'figure'), 
                 Output('fig_cirugias', 'figure'), 
                 Output("fig_calificaciones","figure"), 
                 Output("fig_imagenes","figure"),
                 Output("fig_farmacia","figure"),
                 Output("fig_quejas","figure"),
                 Output("fig_desconocimientos","figure"),],
     [Input('prestador', "value")])
def calculo_graficos(prestador): 
    
    #consultas
    temporal_prestador = pd.DataFrame(columns= ["consulta"], data= ['Consultas - Q afiliados Médica', '2 consultas - Q afiliados', '3 consultas - Q afiliado',
   '4 consultas - Q afiliados', 'Más de 4 - Q afiliados'])

    temporal_especialidad = pd.DataFrame(columns= ["consulta"], data= ['Consultas - Q afiliados Médica', '2 consultas - Q afiliados', '3 consultas - Q afiliado',
   '4 consultas - Q afiliados', 'Más de 4 - Q afiliados'])
    
    fechas = [i for i in os.listdir('datos_consultas/') if len(i) == 12]
    fechas.sort()

    for i in fechas:
        tabla = pd.read_parquet(f'datos_consultas/{i}', columns =['Prestador', 'Razon social', 'Especialidad','Consultas - participación %', '2 consultas - participación %','3 consultas - participación %', '4 consultas - participación %','Más de 4 - participación %'] )  
        if len(tabla[tabla["Prestador"] == prestador]) ==0:
            temporal_prestador[i[:10]] = 0
            temporal_especialidad[i[:10]] = 0
        else:
            #especialidad 
            especialidad_prestador = tabla[tabla["Prestador"] == prestador].values[0][2]
            #nombre del prestador!!!!
            nombre_prestador = tabla[tabla["Prestador"] == prestador].values[0][1]
            prestador_values = tabla[tabla["Prestador"] == prestador].iloc[:,3:]
            temporal_prestador[i[:10]] = prestador_values.T.values
            temporal_especialidad[i[:10]] = tabla[tabla["Especialidad"] == especialidad_prestador].iloc[:,3:].mean(axis=0).values
            
    temporal_prestador = temporal_prestador.melt(id_vars="consulta", value_vars=temporal_prestador.columns[1:])
    temporal_prestador["tipo"] = "prestador"

    temporal_especialidad = temporal_especialidad.melt(id_vars="consulta",  value_vars=temporal_especialidad.columns[1:])
    temporal_especialidad["tipo"] = "especialidad"

    final = pd.concat([temporal_especialidad,temporal_prestador])
    final = final.round(2)

    di = {"Consultas - Q afiliados Médica": "Porcentaje de afiliados con consultas únicas", 
         "2 consultas - Q afiliados": "Porcentaje de afiliados con 2 consultas",
         "3 consultas - Q afiliado": "Porcentaje de afiliados con 3 consultas", 
         "4 consultas - Q afiliados": "Porcentaje de afiliados con 4 consultas",
         "Más de 4 - Q afiliados": "Porcentaje de afiliados con más de 4 consultas"}
    final = final.replace({"consulta": di})

    final = final.rename(columns={"value": "Participación mensual"})

    final["Participación mensual"] = final["Participación mensual"] / 100

    fig_consultas = px.bar(final, x="tipo", y="Participación mensual", barmode="stack",
                 facet_col="variable",  color="consulta")

    fig_consultas.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1][:-3]))


    fig_consultas.layout.xaxis1.tickangle = -90
    fig_consultas.layout.xaxis2.tickangle = -90
    fig_consultas.layout.xaxis3.tickangle = -90
    fig_consultas.layout.xaxis4.tickangle = -90
    fig_consultas.layout.xaxis5.tickangle = -90
    fig_consultas.layout.xaxis5.tickangle = -90
    fig_consultas.layout.xaxis6.tickangle = -90
    fig_consultas.layout.xaxis7.tickangle = -90
    fig_consultas.layout.xaxis8.tickangle = -90
    fig_consultas.layout.xaxis9.tickangle = -90
    fig_consultas.layout.xaxis10.tickangle = -90
    fig_consultas.layout.xaxis11.tickangle = -90
    fig_consultas.layout.xaxis12.tickangle = -90
    fig_consultas.layout.xaxis13.tickangle =-90

    fig_consultas.layout.xaxis1.title = None
    fig_consultas.layout.xaxis2.title = None
    fig_consultas.layout.xaxis3.title = None
    fig_consultas.layout.xaxis4.title = None
    fig_consultas.layout.xaxis5.title = None
    fig_consultas.layout.xaxis5.title = None
    fig_consultas.layout.xaxis6.title = None
    fig_consultas.layout.xaxis7.title = None
    fig_consultas.layout.xaxis8.title = None
    fig_consultas.layout.xaxis9.title = None
    fig_consultas.layout.xaxis10.title = None
    fig_consultas.layout.xaxis11.title = None
    fig_consultas.layout.xaxis12.title = None
    fig_consultas.layout.xaxis13.title = None


    for i in range(0,13):
        fig_consultas.data[i]["marker"]["color"] = "#45b6fe"

    for i in range(13,26):
        fig_consultas.data[i]["marker"]["color"] = "#3792cb"

    for i in range(26,39):
        fig_consultas.data[i]["marker"]["color"] = "#296d98"

    for i in range(39,52):
        fig_consultas.data[i]["marker"]["color"] = "#1c4966"
    for i in range(52,65):
        fig_consultas.data[i]["marker"]["color"] = "black"

    fig_consultas.layout.legend = {"orientation": "h", "xanchor" :"center", "y":-0.4, "x":0.5}
    fig_consultas.update_yaxes(range=[-0,1],tickformat = "%")
    fig_consultas.update_layout(title=dict(text="Métrica: Consultas", x=0.5))
    
    #cirugias 
                
    fechas = [i for i in os.listdir('datos_cirugias/') if len(i) == 12]
    fechas.sort()
    temporal_prestador = pd.DataFrame(columns= ["cirugías"], data= ["porcentaje de cirugías en centros propios", "porcentaje de cirugías en centros no propios"])
    temporal_total = pd.DataFrame(columns= ["cirugías"], data= ["porcentaje de cirugías en centros propios", "porcentaje de cirugías en centros no propios"])
    for i in fechas:
        final = pd.read_parquet(f'datos_cirugias/{i}') 
        if len(final[final["Prestador"] == prestador]) == 0:
            temporal_total[i[:7]] = [np.nan] * 2
            temporal_prestador[i[:7]] =  [np.nan] * 2
        else: 
            propios = final["Propias"].sum()
            no_propios = final["No propias"].sum()
            total = propios + no_propios
            ar = [propios / total , no_propios /total]
            temporal_total[i[:7]] = ar
            final_prestador = final[final["Prestador"] == prestador]
            final_prestador['porcentaje de cirugías en centros propios'] = final_prestador["Propias"] / final_prestador["Total general"]
            final_prestador['porcentaje de cirugías en centros no propios' ] = final_prestador["No propias"] / final_prestador["Total general"]
            temporal_prestador[i[:7]] = final_prestador[["porcentaje de cirugías en centros no propios", "porcentaje de cirugías en centros propios"]].values[0]
    
    x = temporal_prestador.columns[1:]
    y_prestador = temporal_prestador[:1].values[0][1:]
    y_total =  temporal_total[:1].values[0][1:]
    fig_cirugias = go.Figure()
    fig_cirugias.add_trace(go.Bar(x = x ,
                             y = y_prestador,
                             name = "Prestador",
                             marker_color ="#45b6fe"))
    fig_cirugias.add_trace(go.Scatter(x = x ,
                             y = y_total,
                             name = "Cartilla Swiss Medical Medicina Privada",
                             marker_color ="#3792cb"))
    fig_cirugias.layout.legend = {"orientation": "h", "xanchor" :"center", "y":1.14, "x":0.5}
    fig_cirugias.update_yaxes(range=[-0,1],tickformat = "%", title="Porcentaje de cirugías en centros propios")
    fig_cirugias.update_layout(title=dict(text="Métrica: Cirugías", x=0.5), height = 500, width= 800)
    
    #calificaciones
    
    fechas = [i for i in os.listdir('datos_calificaciones/') if len(i) == 12]
    fechas.sort()

    temporal_prestador = pd.DataFrame(columns= ["calificaciones"], data= ['Promedio Calificación Atención Médica',
           'Promedio Calificación Disponibilidad de Turno',
           'Promedio Calificación Limpieza y Confort', 
           'Promedio Calificación Puntualidad',
           'Promedio Calificación Trato y Cordialidad', "cantidad_afiliados" ])
    temporal_general = pd.DataFrame(columns= ["calificaciones"], data= ['Promedio Calificación Atención Médica',
           'Promedio Calificación Disponibilidad de Turno',
           'Promedio Calificación Limpieza y Confort', 
           'Promedio Calificación Puntualidad',
           'Promedio Calificación Trato y Cordialidad' ])

    for i in fechas:
        pivot = pd.read_parquet(f'datos_calificaciones/{i}', columns= ['Prestador', 
                                                            'Razón social',
                                                            'Q respuestas', 
                                                            'Q afiliados',
                                                            'Promedio Calificación Atención Médica', 
                                                            'Promedio Calificación Disponibilidad de Turno',
                                                            'Promedio Calificación Limpieza y Confort', 
                                                            'Promedio Calificación Puntualidad', 
                                                            'Promedio Calificación Trato y Cordialidad']) 
        if len(pivot[pivot["Prestador"]== prestador]) == 0:

            prestador_values = [np.nan] * 6
            general = [np.nan] * 5
            prestador_nombre = ""
        else:
            prestador_nombre = pivot[pivot["Prestador"]== prestador].iloc[0:1,1:2].values[0][0]
            prestador_values = pivot[pivot["Prestador"]== prestador].iloc[0:,4:].values[0]
            afiliados_calificadores = pivot[pivot["Prestador"]== prestador].iloc[0:,2:3].values[0][0]

            prestador_values = np.append(prestador_values, [afiliados_calificadores])
            general = pivot.iloc[0:,4:].mean().values


        temporal_prestador[i[:7]] = prestador_values
        temporal_general[i[:7]] = general 

    temporal_general = temporal_general.round(1)

    x = temporal_prestador.columns[1:]
    fig_calificaciones = make_subplots(rows=6, cols=1,
                        shared_xaxes=True,
                         y_title='Promedio calificación',
                        vertical_spacing=0.03, subplot_titles=('Atención Médica: Calificación Promedio',
           'Disponibilidad de Turno: Calificación Promedio',
           'Limpieza y Confort: Calificación Promedio',
           'Puntualidad: Calificación Promedio',
           'Trato y Cordialidad: Calificación Promedio', 
           "Número de afiliados que calificaron en cada mes"))
    fig_calificaciones.add_trace(go.Scatter(x=x, y=temporal_general.iloc[0:1,1:].values[0], name="Cartilla Swiss Medical Medicina Privada",
                        line_shape='linear'), row=1, col=1)
    fig_calificaciones.add_trace(go.Scatter(x=x, y=temporal_prestador.iloc[0:1,1:].values[0], name=f"Prestador: {prestador_nombre}",
                        line_shape='linear'), row=1, col=1)

    for i,j in zip(range(1,5), range(2,6)):
        fig_calificaciones.add_trace(go.Scatter(x=x, y=temporal_general.iloc[i:j,1:].values[0],showlegend=False,
                        line_shape='linear'), row=j, col=1)
        fig_calificaciones.add_trace(go.Scatter(x=x, y=temporal_prestador.iloc[i:j,1:].values[0], showlegend=False,
                        line_shape='linear'), row=j, col=1)

    fig_calificaciones.add_trace(go.Bar(x=x, y=temporal_prestador.iloc[5:6,1:].values[0], showlegend=False,
                         marker_color = "#45b6fe",),row=6, col=1, )

    for i in [1,3,5,7,9]:
        for j in ["marker", "line"]:
            fig_calificaciones.data[i][j]["color"] = "#45b6fe"

    for i in [0,2,4,6,8]:
        for j in ["marker", "line"]:
            fig_calificaciones.data[i][j]["color"] = "#296d98"

    for i in range(0,6):
        fig_calificaciones.update_yaxes(range=[0, 5.6], row=i, col=1)

    fig_calificaciones.update_yaxes(title_text="Cantidad", range=[0, 35],showgrid=False, row=1, col=6)

    fig_calificaciones.update_layout(title=dict(text="Métrica: Calificaciones", x=0.5), height=1100, #width=900,
                     legend=dict(traceorder='reversed', font_size=15, orientation="h"))


    
    #imagenes
    
    fechas = [i for i in os.listdir('datos_imagenes/') if len(i) == 12]
    fechas.sort()
    temporal = pd.DataFrame(columns= ["normalidad"], data= ["prestador", "especialidad", "cantidad_imagenes"])
    for i in fechas: 
        final_imagenes = pd.read_parquet(f'datos_imagenes/{i}', columns= ['N° Prescriptor', 'Prescriptor', 'deno','Total general', 'Normalidad']) 

        if len((final_imagenes[final_imagenes["N° Prescriptor"] == prestador])) == 0:
            ar = [np.nan,np.nan, np.nan]
        else:
            especialidad = final_imagenes[final_imagenes["N° Prescriptor"] == prestador].values[0][2]
            general = final_imagenes[final_imagenes["deno"] == especialidad]["Normalidad"].mean()
            prestador_values = final_imagenes[final_imagenes["N° Prescriptor"] == prestador].Normalidad.mean()
            cantidad_imagenes = final_imagenes[final_imagenes["N° Prescriptor"] == prestador].values[0][3]
            ar = [prestador_values,general, cantidad_imagenes]
    
        temporal[i[:7]] = ar
    temporal = temporal.round(2)
    
    x = temporal.columns[1:]
    y_prestador = temporal[:1].values[0][1:]
    y_especialidad = temporal[1:3].values[0][1:]

    fig_imagenes = make_subplots(rows=2, cols=1,
                        shared_xaxes=True,
                        vertical_spacing=0.13, subplot_titles=('Normalidad de imágenes',
           'Número de imágenes mensuales'))
    fig_imagenes.add_trace(go.Scatter(x = x ,
                             y = y_prestador,
                             name = "Prestador", marker_color = "#45b6fe"
                             ),row=1, col=1,)
    fig_imagenes.add_trace(go.Scatter(x = x ,
                             y = y_especialidad,
                             name = "Especialidad", marker_color ="#3792cb"
                             ),row=1, col=1,)

    fig_imagenes.add_trace(go.Bar(x=x, y=temporal[2:3].values[0][1:], showlegend=False,
                         marker_color = "#45b6fe",),row=2, col=1)


    fig_imagenes.update_yaxes(range=[-0.1,1.1], title="% de normalidad", row=1, col=1)
    fig_imagenes.update_yaxes(title="Número de imágenes", row=2, col=1)
    fig_imagenes.update_layout(title=dict(text="Métrica: Imágenes", x =0.5), 
                        yaxis_tickformat = "%", height=1000)
    fig_imagenes.layout.legend = {"orientation": "h", "xanchor" :"center", "x":0.5}
    
    
    #farmacia
    
    temporal = pd.DataFrame(columns= ["farmacia"], data= ["desvio"])
    fechas = [i for i in os.listdir('datos_farmacia/') if len(i) == 12]
    fechas.sort()

    for i in fechas:
        df = pd.read_parquet(f'datos_farmacia/{i}', columns =['N° Prestador', "Médico", "Especialidad", "Media por especialidad", "Afil. Usuarios","Recetas", "Promedio por afiliado"  ] )
        if len(df[df["N° Prestador"] == prestador]) == 0:
            temporal[i[:7]] = 0 
        else:
            especialidad = df[df["N° Prestador"] == prestador].iloc[0,2]

            desvio = df[df["Especialidad"] == especialidad]['Promedio por afiliado'].std()

            desvios_amedia = ((df[df["N° Prestador"] == prestador]["Promedio por afiliado"]) - (df[df["N° Prestador"] == prestador]["Media por especialidad"])) /desvio

            temporal[i[:7]]=desvios_amedia.iloc[0].round(2)
            
    x = temporal.columns[1:]
    y_prestador = temporal[:1].values[0][1:]
    fig_farmacia = go.Figure()
    fig_farmacia.add_trace(go.Bar(x = x ,
                         y = y_prestador,
                         name = "Prestador", base=0, text=y_prestador, textposition="auto", marker_color = "#45b6fe"
                             ))
    fig_farmacia.update_traces(textposition="outside")


    fig_farmacia.update_layout(title=dict(text= "Métrica: Farmacia", x=0.5, y =0.9),
                     showlegend= False, height = 500, width= 800)
    fig_farmacia.update_yaxes(range=[-2,2],tickvals = [2, 1, 0, -1,-2], ticktext=["2 desvíos", "1 desvío", "Media especialidad","-1 desvío", "-2 desvíos"])

    #quejas
    
    temporal = pd.DataFrame(columns= ["quejas"], data= ["prestador"])
    fechas = [i for i in os.listdir('datos_quejas/') if len(i) == 12]
    fechas.sort()
    
    for i in fechas:
        final = pd.read_parquet(f'datos_quejas/{i}')
        if len(final[final.Prestador == prestador]) == 0:
            ar = [np.nan]
        else:
            ar = final[final.Prestador == prestador]["Total de quejas prestador"].unique()[0]


        temporal[i[:7]] = ar
        
    x = temporal.columns[1:]
    y_prestador = temporal[:1].values[0][1:]
    fig_quejas = go.Figure()
    fig_quejas.add_trace(go.Bar(x = x ,
                             y = y_prestador,
                             name = "Prestador",
                             marker_color = "#45b6fe"))
    fig_quejas.update_layout(title=dict(text = "Métrica: Quejas", x=0.5, y=0.9),  height = 500, width= 800)
    fig_quejas.update_yaxes(title="N° de quejas por mes")
    
    
    #desconocimientos
    
    fechas = [i for i in os.listdir('datos_desconocimiento/') if len(i) == 12]
    fechas.sort()

    temporal = pd.DataFrame(columns= ["desconocimientos"], data= ["prestador"])

    for i in fechas:
        final = pd.read_parquet(f'datos_desconocimiento/{i}')
        if len(final[final.Prestador == prestador]) == 0:
            ar = [np.nan]
        else:
            prestador_values = final[final.Prestador == prestador]["Q afiliados"].unique()[0]
            ar = [prestador_values]

        temporal[i[:7]] = ar
        
    
    x = temporal.columns[1:]
    y_prestador = temporal[:1].values[0][1:]
    fig_desconocimientos = go.Figure()
    fig_desconocimientos.add_trace(go.Bar(x = x ,
                             y = y_prestador,
                             name = "Prestador",
                             marker_color = "#45b6fe"))
    fig_desconocimientos.update_layout(title=dict(text = "Métrica: Desconocimientos", x=0.5, y=0.9),  height = 500, width= 800)
    fig_desconocimientos.update_yaxes(title="N° de desconocimientos por mes")


    return nombre_prestador, especialidad_prestador, fig_consultas, fig_cirugias, fig_calificaciones, fig_imagenes, fig_farmacia, fig_quejas, fig_desconocimientos
