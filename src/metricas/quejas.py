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

gerencias = querydbtopandas(f"""select id_gerencia,ger_Descripcion from DBA.CRM_GERENCIAS """)

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css 5", 
                        'https://codepen.io/amyoshino/pen/jzXypZ.css']

App_1 = dash.Dash(__name__, server=server, url_base_pathname='/quejas/', external_stylesheets=external_stylesheets )


colors = {
    'background': '#111111',
    'text': 'grey'
}

App_1.layout = html.Div([
    html.Div([html.H1(
            children='Quejas',
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
            html.P('Seleccione una Gerencia')
    ]),
        html.Div([
        dcc.Dropdown(
            id='gerencia',
            options=[{'label': i, 'value': j} for i,j in zip(gerencias.ger_Descripcion,gerencias.id_gerencia )],
            value=[18, 19],
            multi=True
    ),
    ], style = {"margin-top":"2px","margin-bottom":"4px"}),

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
      Input('my-date-picker-range', 'end_date'),
      Input('gerencia',"value")
])

def filtros(start_date, end_date, gerencia):
    
    start_date = dt.strptime(start_date.split('T')[0], '%Y-%m-%d')
    menor = start_date.strftime('%Y-%m-%d')
    
    end_date = dt.strptime(end_date.split('T')[0], '%Y-%m-%d')
    mayor = end_date.strftime('%Y-%m-%d')
    
    gerencia = str(gerencia).strip("]").strip("[")
    
    df = querydbtopandas(f"""select a11.workflow_id  workflow_id,
       max(a113.detalle)  detalle3,
      a12.prestad  id_pre_prestador,
      a18.GERENCIA,
       max(a13.desc_pre_nombre)  desc_pre_nombre,
       sum(1.0)  CANTIDADETAPASMINNDISTINCT
       from   DBA.CRM_ETAPAS_MIN_MAX a11
       join   DBA.crm_quejas_categ_resol a12
         on   (a11.etapa_id_max = a12.ETAPA_ID)
      join   DBA.d_pre_prestador    a13
         on   (a12.prestad = a13.id_pre_prestador)         
       join   DBA.crm_atributo_quejas    a113
         on   (a12.atributo_id = a113.atributo_id)  
       join   DBA.ft_pad_padron_iq   a14
         on   (a11.ID_AFI_AFILIADO = a14.id_afiliados and
       a11.id_tie_mes_max = a14.MES)  
       join   DBA.CRM_SUBMOTIVOS a18
         on   (a12.SUBMOTIVO_ID = a18.SUBMOTIVO_ID and
       a12.motivo_llamado_id = a18.motivo_id)
    where  (a11.registro_fecha_max >= date("{menor}") and a11.registro_fecha_max < date("{mayor}")
    and a11.motivo_id = 8
    and a12.estado in (14)
    and a18.GERENCIA in ({gerencia})
    and a12.prestad <> 0)
    group by   a11.workflow_id,
       a18.GERENCIA,
       a12.finalizado,
       prestad,
       a12.ALTA_FECHA
       """)
    df_metrica = df[["workflow_id", "detalle3", "id_pre_prestador","desc_pre_nombre" ]]

    final = df_metrica.groupby([ "id_pre_prestador","desc_pre_nombre", "detalle3" ])["workflow_id"].nunique().reset_index()

    total_prestador = final.groupby([ "id_pre_prestador","desc_pre_nombre"])["workflow_id"].sum().rename("total_prestador")

    final = final.merge(total_prestador, left_on = "id_pre_prestador" , right_on="id_pre_prestador" )

    final = final.rename(columns= {"id_pre_prestador": "Prestador", "desc_pre_nombre": "Razón social", "detalle3": "Clasificación de casos", "workflow_id": "Q de quejas", "total_prestador": "Total de quejas prestador"})

    data_ob_otros = final.to_dict('rows')
    columns_ob_otros = [{'name': i, 'id': i} for i in final.columns.tolist()]

    return data_ob_otros, columns_ob_otros

