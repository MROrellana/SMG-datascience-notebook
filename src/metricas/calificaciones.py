import dash
from datetime import datetime as dt
import dash_html_components as html
import dash_core_components as dcc
import pandas as pd
from dash.dependencies import Input, Output
from datetime import datetime
from datetime import date
import dash_table
import numpy as np

from server import server

from dbconn import querydb, querydbtopandas 

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css 5", 
                        'https://codepen.io/amyoshino/pen/jzXypZ.css']

App_1 = dash.Dash(__name__, server=server, url_base_pathname='/calificaciones/', external_stylesheets=external_stylesheets )

path = "parametros_calificaciones/items_encuestas.xlsx"

items_encuestas = str(pd.read_excel(path).item_id.tolist()).strip("[").strip("]")

dict_id = {3: 'Atención Médica',
 2: 'Trato y Cordialidad',
 4: 'Disponibilidad de Turno',
 1: 'Puntualidad',
 5: 'Limpieza y Confort'}   

colors = {
    'background': '#111111',
    'text': 'grey'
}

App_1.layout = html.Div([
    html.Div([html.H1(
            children='Calificaciones',
            style={
                'textAlign': 'center',
                'color': colors['text']
        })
    ]),
    html.Div([
        html.P('Seleccione un período')
    ]),

    html.Div([
    dcc.DatePickerRange(
        id='my-date-picker-range',
        min_date_allowed=dt(1995, 8, 5),
        max_date_allowed=dt(2030, 9, 19),
        start_date=dt(2019,11,30),
        end_date=dt(2019, 12, 30).date()
    ),
        html.Div(id='output-container-date-picker-range')
            ], style = {"margin-top":"2px","margin-bottom":"4px"}
    ),

        html.Div([
        dash_table.DataTable(id='otros', 
                    sort_action='native',
                    filter_action='native',
                    style_cell={'fontSize':12, 'font-family':'sans-serif'},
                    style_table={'overflowX': 'scroll', 'maxHeight': '500px', 'overflowY': 'scroll' },
                    style_data_conditional=[
                        {
                         'if': {'column_id': 'Promedio total',
                         'filter_query': "{Promedio total} < 3.5"   
                            },
                         'backgroundColor': '#cc0000',
                         'color': 'white',
                        },

                        {
                          'if': {'column_id': 'Promedio Calificación Atención Médica',
                         'filter_query': "{Promedio Calificación Atención Médica} < 3.5"
                             },
                         'backgroundColor': '#cc0000',
                         'color': 'white',
                        },
                        
                        {
                          'if': {'column_id': 'Promedio Calificación Disponibilidad de Turno',
                         'filter_query': "{Promedio Calificación Disponibilidad de Turno} < 3.5"
                             },
                         'backgroundColor': '#cc0000',
                         'color': 'white',
                        },
                    
                        {
                          'if': {'column_id': 'Promedio Calificación Limpieza y Confort',
                         'filter_query': "{Promedio Calificación Limpieza y Confort} < 3.5"     
                         },
                         'backgroundColor': '#cc0000',
                         'color': 'white',
                        },
                          
                        {
                          'if': {'column_id':'Promedio Calificación Puntualidad',
                         'filter_query': "{Promedio Calificación Puntualidad} < 3.5"     
                         },
                         'backgroundColor': '#cc0000',
                         'color': 'white',
                        },
                        
                        {
                          'if': {'column_id': 'Promedio Calificación Trato y Cordialidad',
                         'filter_query': "{Promedio Calificación Trato y Cordialidad} < 3.5"     
                         },
                         'backgroundColor': '#cc0000',
                         'color': 'white'
                        }]
               
                             
                     ),
    ],

    )


    ])


@App_1.callback(
    [Output('otros', 'data'),
    Output('otros', 'columns')],

     [Input('my-date-picker-range', 'start_date'),
      Input('my-date-picker-range', 'end_date')
])

def filtros(start_date, end_date):
    
    start_date = dt.strptime(start_date.split('T')[0], '%Y-%m-%d')
    menor = start_date.strftime('%Y-%m-%d')
    
    end_date = dt.strptime(end_date.split('T')[0], '%Y-%m-%d')
    mayor = end_date.strftime('%Y-%m-%d')
    
    
    
    df = querydbtopandas(f"""
select  a11.id_item  id,
       a11.id_encuesta  id_encuesta,
       a12.id_afiliado  id_afi_afiliado,
       a12.id_prestador  id_pre_prestador,
       a17.desc_pre_nombre  desc_pre_nombre_efector,
       a18.desc_pre_nombre  desc_pre_nombre,
       a18.id_pre_tipo,   
       a12.id_prest_efector,
       a11.i_R RESPUESTA
from        DBA.ft_d_prest_encuestas        a11
       join        DBA.ft_prest_encuestas        a12
         on        (a11.id_encuesta = a12.id_encuesta)
       join        DBA.d_pre_prestador        a17
         on        (a12.id_prest_efector = a17.id_pre_prestador)      
       join        DBA.d_pre_prestador        a18
         on        (a12.id_prestador = a18.id_pre_prestador)
where (cast(fec_encuesta as date) >= date("{menor}") and cast(fec_encuesta as date) < date("{mayor}")
and a11.id_item in ({items_encuestas})
and a18.id_pre_tipo in ("E","C","P","I"))
group by        a11.id_item,
       a11.i_R,
       a11.id_encuesta,
       a12.id_afiliado,
       a12.id_prestador,
       a17.desc_pre_nombre,    
       a18.id_pre_tipo,
       a18.desc_pre_nombre,
       a12.id_prest_efector""")
    
    df["id"] = df["id"].map(dict_id)

    df_part_equipos = df[df["id_pre_tipo"].isin(["P","E"])][["id","id_encuesta", "id_afi_afiliado", "id_pre_prestador", "desc_pre_nombre", "RESPUESTA" ]]

    df_inst_circ = df[df["id_pre_tipo"].isin(["I","C"])][["id","id_encuesta","id_afi_afiliado", "id_prest_efector", "desc_pre_nombre_efector", "RESPUESTA"]]

    df_inst_circ.rename(columns={"id_prest_efector": "id_pre_prestador", "desc_pre_nombre_efector":"desc_pre_nombre"},inplace=True)

    df = pd.concat([df_part_equipos, df_inst_circ])

    df = df[df["id_pre_prestador"] != 0]

    q_afiliados = df.groupby("id_pre_prestador")["id_afi_afiliado"].nunique().rename_axis('id_pre_prestador').reset_index(name='q_afiliados')

    prestadores_mas_5_afiliados = q_afiliados[q_afiliados.q_afiliados > 5].id_pre_prestador.tolist()

    df = df[df["id_pre_prestador"].isin(prestadores_mas_5_afiliados)]

    q_respuestas = df.groupby("id_pre_prestador")["id_encuesta"].nunique().rename_axis('id_pre_prestador').reset_index(name='q_respuestas')

    df = df.merge(q_respuestas).merge(q_afiliados)

    pivot = pd.pivot_table(df, 
                 index=["id_pre_prestador","desc_pre_nombre", "q_afiliados", "q_respuestas"], 
                 columns="id", 
                 values="RESPUESTA", aggfunc= ["mean", "sum"]).reset_index()
    pivot.columns = ["Prestador", 'Razón social', 'Q afiliados', "Q respuestas", 'Atención Médica m', 'Disponibilidad de Turno m',
               'Limpieza y Confort m', 'Puntualidad m', 'Trato y Cordialidad m',
               'Atención Médica s', 'Disponibilidad de Turno s', 'Limpieza y Confort s',
               'Puntualidad s', 'Trato y Cordialidad s']

    pivot.rename(columns={
                    'Atención Médica s':"Calificación Atención Médica",
                    'Disponibilidad de Turno s':"Calificación Disponibilidad de Turno",
                    'Limpieza y Confort s':"Calificación Limpieza y Confort",
                    'Puntualidad s': "Calificación Puntualidad", 
                    'Trato y Cordialidad s':"Calificación Trato y Cordialidad",
                    'Atención Médica m':"Promedio Calificación Atención Médica", 
                    'Disponibilidad de Turno m':"Promedio Calificación Disponibilidad de Turno", 
                    'Limpieza y Confort m':"Promedio Calificación Limpieza y Confort",
                    'Puntualidad m':"Promedio Calificación Puntualidad",
                    'Trato y Cordialidad m':"Promedio Calificación Trato y Cordialidad"}, inplace=True)

    pivot["Promedio total"] = (pivot["Promedio Calificación Atención Médica"]+
                                  pivot["Promedio Calificación Disponibilidad de Turno"]+
                                  pivot["Promedio Calificación Limpieza y Confort"]+
                                  pivot["Promedio Calificación Puntualidad"]+
                                  pivot["Promedio Calificación Trato y Cordialidad"]) / 5

    pivot= pivot[['Prestador', 'Razón social', 'Q respuestas', 'Q afiliados',
                         'Calificación Atención Médica', 'Promedio Calificación Atención Médica',
                         'Calificación Disponibilidad de Turno','Promedio Calificación Disponibilidad de Turno',
                         'Calificación Limpieza y Confort',   'Promedio Calificación Limpieza y Confort',
                         'Calificación Puntualidad',   'Promedio Calificación Puntualidad',
                         'Calificación Trato y Cordialidad',  'Promedio Calificación Trato y Cordialidad','Promedio total']]
    pivot = pivot.sort_values(by="Promedio total", ascending= True)
    pivot = pivot.round(2)

    
    data_ob_otros = pivot.to_dict('rows')
    columns_ob_otros = [{'name': i, 'id': i} for i in pivot.columns.tolist()]

    return data_ob_otros, columns_ob_otros

