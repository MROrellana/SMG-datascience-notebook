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

App_1 = dash.Dash(__name__, server=server, url_base_pathname='/farmacia/', external_stylesheets=external_stylesheets )


colors = {
    'background': '#111111',
    'text': 'grey'
}

App_1.layout = html.Div([
    html.Div([html.H1(
            children='Métrica Farmacia',
            style={
                'textAlign': 'center',
                'color': colors['text']
        })
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
]),

        html.Hr(),
        html.H1(
            children='Tabla de prestadores',
            style={
                'textAlign': 'center',
                'color': colors['text'],
                "fontSize" : 25
        }),


        html.Div([
        dash_table.DataTable(id='otros', 
                    sort_action='native',
                    filter_action='native',
                    style_cell={'fontSize':12, 'font-family':'sans-serif'},
                    style_table={'overflowX': 'scroll', 'maxHeight': '800px', 'overflowY': 'scroll' },
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

def filtros_ordenes(start_date, end_date):
    start_date = dt.strptime(start_date.split('T')[0], '%Y-%m-%d')
    start_date_string = start_date.strftime('%Y-%m-%d')
    
    end_date = dt.strptime(end_date.split('T')[0], '%Y-%m-%d')
    end_date_string = end_date.strftime('%Y-%m-%d')
    
    df = querydbtopandas()   
    #df = querydbtopandas(f"""select id_prestador_efector, 
    #a14.id_afiliado,
    #desc_pre_nombre, 
    #desc_prof_especialidad, 
    #sum(i_ft_cantidad) cantidad,
    #sum(i_ft_importe) importe,
    #id_medicamento
    #from dba.ft_costo_medico A
    #left JOIN dba.d_pre_prestador B
    #    ON a.id_prestador_efector = b.id_pre_prestador
    #LEFT JOIN dba.d_prof_especialidad C
    #    ON B.id_pre_especialidad = C.id_prof_especialidad
    #LEFT JOIN dba.fecha_mes D
    #    ON a.id_tie_fecha_liquidacion = d.id_Tie_mes
    #left join DBA.afi_afiliados a14
    #     on a.id_afiliado = a14.id_afiliado
    #where CONVERT(DATETIME,d.exp_mes, "mm-YYYY") >= date("{start_date_string}") and CONVERT(DATETIME,d.exp_mes, "mm-YYYY") < date("{end_date_string}")
    #and id_prestador_efector not in (0)
    #and tbl_origen = 'receta_medicamento'
    #group by id_prestador_efector, desc_pre_nombre, desc_prof_especialidad, a14.id_afiliado,
    #id_medicamento,i_ft_cantidad, i_ft_importe""")
    
    
    df = df[df["id_prestador_efector"] != 0]

    importe = df.groupby(["id_prestador_efector","desc_pre_nombre", "desc_prof_especialidad" ])["importe"].sum()

    cantidad_ordenes = df.groupby(["id_prestador_efector","desc_pre_nombre", "desc_prof_especialidad" ])["cantidad"].sum()

    cantidad_afiliados = df.groupby(["id_prestador_efector","desc_pre_nombre", "desc_prof_especialidad" ])["id_afiliado"].nunique()

    df = pd.concat([importe,cantidad_ordenes,cantidad_afiliados],axis=1).reset_index()

    df["promedio por afiliado"] = df["importe"] / df["id_afiliado"]
    df["promedio por receta"] = df["importe"] / df["cantidad"]

    suma_especialidad = df.groupby("desc_prof_especialidad")["promedio por afiliado"].sum()

    num_prestador_esp = df.groupby("desc_prof_especialidad")["desc_pre_nombre"].nunique()

    media_especialidad = (suma_especialidad/num_prestador_esp).reset_index().rename(columns= {0: "media por especialidad"})

    df = df.merge(media_especialidad)

    df["Diferencia respecto de la media"] = ((df["promedio por afiliado"] / df["media por especialidad"]) -1 )*100

    df = df.round(2)

    df = df[['id_prestador_efector', 'desc_pre_nombre', 'desc_prof_especialidad',  'media por especialidad',  'Diferencia respecto de la media',
            'id_afiliado', 'cantidad', 'promedio por afiliado',
           'promedio por receta', 'importe' ]]

    df.columns = ["N° Prestador", "Médico", "Especialidad", "Media por especialidad", "Diferencia respecto de la media", "Afil. Usuarios", "Recetas", "Promedio por afiliado", "Promedio por receta", "A cargo de SMMP"]
    data_ob = df.to_dict('rows')
    columns_ob = [{'name': i, 'id': i} for i in df.columns.tolist()]

    return data_ob, columns_ob

