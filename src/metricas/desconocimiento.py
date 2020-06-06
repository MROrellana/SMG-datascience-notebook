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

App_1 = dash.Dash(__name__, server=server, url_base_pathname='/desconocimiento/', external_stylesheets=external_stylesheets )

path = "parametros_desconocimiento/centros_propios_swiss.xlsx"

clinicas_propias_id = pd.read_excel(path,index_col=0).id_pre_prestador.to_list()


colors = {
    'background': '#111111',
    'text': 'grey'
}

App_1.layout = html.Div([
    html.Div([html.H1(
            children='Desconocimiento',
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
                    style_table={'overflowX': 'scroll', 'maxHeight': '500px', 'overflowY': 'scroll' }
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
    
    
    
    df = querydbtopandas(f"""select    a11.id_encuesta  id_encuesta,    
                a11.id_afiliado  id_afi_afiliado,
                a11.id_prestador  id_pre_prestador,                   
                max(a13.desc_pre_nombre)  desc_pre_nombre,
                max(a13.vigente)  vigente,
                a11.id_transac_tipo  id_transac_tipo,            
                a11.id_prest_prestacion  id_pres_prestacion,
                max(a18.desc_pres_prestacion)  desc_pres_prestacion,
                max(a18.prestac_pres_prestacion)  prestac_pres_prestacion,
                sum(distinct a11.i_CNT_desc)  QDESCONOCIDAS
from      DBA.ft_prest_encuestas              a11
                join        DBA.d_pre_prestador   a13
                  on        (a11.id_prestador = a13.id_pre_prestador)
                join        DBA.d_pres_prestacion a18
                  on        (a11.id_prest_prestacion = a18.id_pres_prestacion)
where (cast(a11.fec_encuesta as date) >= date("{menor}") and cast(a11.fec_encuesta as date) < date("{mayor}")
and a11.id_moti_desconoc <> 1
and a11.id_prestador <> 0)
group by             a11.id_encuesta,
                a11.id_afiliado,
                a11.id_prestador,         
                a13.id_pre_especialidad,
                a11.id_transac_tipo,
                a11.id_prest_prestacion,
                DATE(a11.fec_consumo),
                a11.id_tie_mes_c""")
    
    
    cma = df[df["id_pre_prestador"].isin(clinicas_propias_id)][["id_pre_prestador", "desc_pre_nombre"]].rename(columns={"desc_pre_nombre": "cma"})
    df = pd.merge(df, cma, how="outer").fillna("No aplica")
    encuestas_desconocidas = df.groupby(["id_pre_prestador","desc_pre_nombre","cma"])["id_encuesta"].nunique()
    afiliados_desconocidos = df.groupby(["id_pre_prestador","desc_pre_nombre", "cma"])["id_afi_afiliado"].nunique()
    df = pd.concat([encuestas_desconocidas, afiliados_desconocidos],axis=1).reset_index()
    df.rename(columns = {"id_pre_prestador":"Prestador",
                     "desc_pre_nombre":"Razón Social",
                     "id_encuesta":"Q desconocidas",
                     "id_afi_afiliado":"Q afiliados"},inplace=True)
    df = df[['Prestador', 'Razón Social', 'cma', 'Q afiliados', 'Q desconocidas']]

    data_ob_otros = df.to_dict('rows')
    columns_ob_otros = [{'name': i, 'id': i} for i in df.columns.tolist()]

    return data_ob_otros, columns_ob_otros

