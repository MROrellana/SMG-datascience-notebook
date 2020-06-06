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

App_1 = dash.Dash(__name__, server=server, url_base_pathname='/cirugias/', external_stylesheets=external_stylesheets )

path1 = "parametros_cirugias/cirugias_validas.xlsx"
path2 = "parametros_cirugias/centros_propios.xlsx"

cirugias_validas = pd.read_excel(path1,index_col=0,dtype=str).prestac_pres_prestacion.tolist()
cirugias_validas = str(cirugias_validas).strip("[").strip("]")

centros_propios = pd.read_excel(path2,index_col=0).id_pre_prestador.tolist()

colors = {'text': 'grey'}

App_1.layout = html.Div([
    html.Div([html.H1(
            children='Cirugías',
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
    
    df = querydbtopandas(f"""select 
                a11.id_pre_prestador  id_pre_prestador,
                max(a15.desc_pre_nombre)  desc_pre_nombre,
                max(a15.vigente)  vigente,
                a12.id_pre_prestador  id_pre_prestador0,
                max(a16.desc_pre_nombre)  desc_pre_nombre0,
                sum(a11.i_ft_importe_prestacion)  RDENES,
                sum(case  when (  i_ft_importe_prestacion *i_Ft_Cantidad <= 0) then 0  when  (i_ft_importe_prestacion *i_Ft_Cantidad <> 0 ) then   i_Ft_Cantidad   end )  CANTIDADORDENES0
from      DBA.ft_ordenes               a11
                join        DBA.d_auto_autorizacion     a12
                  on        (((a11.id_auto_sucursal * 10000000) + a11.i_ft_autorizacion) = ((a12.id_auto_sucursal * 10000000) + a12.id_auto_autorizacion))
                join        DBA.d_exp_expediente a13
                  on        (((a11.id_ofi_oficina * 10000000) + a11.id_exp_expediente) = ((a13.ofi * 10000000) + a13.id_exp_expediente))
                join        DBA.d_pre_prestador   a15
                  on        (a11.id_pre_prestador = a15.id_pre_prestador)
                join        DBA.d_pre_prestador_autoriza a16
                  on        (a12.id_pre_prestador = a16.id_pre_prestador)
                join        DBA.d_pres_prestacion a17
                  on        (a11.id_pres_prestacion = a17.id_pres_prestacion)
where (CONVERT(DATETIME,a13.exp_mes, "mm-YYYY") >= date("{menor}") and CONVERT(DATETIME,a13.exp_mes, "mm-YYYY") < date("{mayor}")
and a15.id_pre_tipo in ('E','P')
and a11.id_nom_nomenclador in (1,11)
and (not a11.id_pre_prestador in (154688))
and (a12.id_pre_prestador <> 0)
and RTRIM(a17.prestac_pres_prestacion) in ({cirugias_validas}))
group by             a11.id_pres_prestacion,
                a11.id_nom_nomenclador,
                a11.id_pre_prestador,
                a12.id_pre_prestador""")
    
    df_propios = df[df["id_pre_prestador0"].isin(centros_propios)]

    df_no_propios = df[~df["id_pre_prestador0"].isin(centros_propios)]

    propios = df_propios.groupby(["id_pre_prestador", "desc_pre_nombre"])["CANTIDADORDENES0"].sum().reset_index().rename(columns = {"CANTIDADORDENES0": "propios"})

    no_propios = df_no_propios.groupby(["id_pre_prestador", "desc_pre_nombre"])["CANTIDADORDENES0"].sum().reset_index().rename(columns = {"CANTIDADORDENES0": "no_propios"})

    final = pd.merge(propios, no_propios,how="outer")

    final.fillna(0,inplace=True)

    final["total"]  = final["propios"] + final["no_propios"]

    final["porcentaje en propios"] = (final["propios"] /final["total"])

    final = final.round(2)

    final.rename(columns= {"id_pre_prestador": "Prestador", "desc_pre_nombre": "Razón Social", "propios": "Propias", "no_propios": "No propias", "total": "Total general","porcentaje en propios":"% en Propias" },inplace=True)
    
    
    data_ob_otros = final.to_dict('rows')
    columns_ob_otros = [{'name': i, 'id': i} for i in final.columns.tolist()]

    return data_ob_otros, columns_ob_otros

