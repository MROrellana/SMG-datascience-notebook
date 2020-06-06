import dash
from datetime import datetime as dt
import dash_html_components as html
import dash_core_components as dcc
import pandas as pd
from dash.dependencies import Input, Output
from datetime import datetime
import datetime
import dash_table
import numpy as np

from server import server

from dbconn import querydb, querydbtopandas 

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css 5", 
                        'https://codepen.io/amyoshino/pen/jzXypZ.css']

App_1 = dash.Dash(__name__, server=server, url_base_pathname='/observatorio/', external_stylesheets=external_stylesheets )

prov_zonas = pd.read_csv("provincias_zonas.csv")
zonas = prov_zonas[["codigo_zona","zona"]].drop_duplicates()

colors = {
    'background': '#111111',
    'text': 'grey'
}

App_1.layout = html.Div([
    html.Div([html.H1(
            children='Observatorio de precios',
            style={
                'textAlign': 'center',
                'color': colors['text']
        })
    ]),
    
    html.Div([
            html.P('Inserte un código de prestación')
    ]),
    html.Div([
        dcc.Input(id="prestacion", type="text", placeholder=""),
    ]),
    
    html.Div(id="prestacion_nombre"),
    
        html.Div([
            html.P('Inserte el id del prestador de referencia')
    ]),
    html.Div([
        dcc.Input(id="prestador_ref", type="number", placeholder=""),
    ]),
    
    html.Div(id="prestador_nombre"),
    
            html.Div([
            html.P('Ambulatorio o Internación')
    ]),
        html.Div([
        dcc.Dropdown(
            id='ambu_inte',
            options=[{'label': "Ambulatorio", 'value': "Ambulatorio"},
                     {"label": "Internación", "value": "Internación"}],
            multi=False
    ),
    ], style = {"margin-top":"2px","margin-bottom":"4px"}),
    

        html.Div([
            html.P('Seleccione una provincia')
    ]),
        html.Div([
        dcc.Dropdown(
            id='provincia',
            options=[{'label': i, 'value': j} for i,j in zip(prov_zonas.provincia,prov_zonas["codigo_provincia "])],
            value=[1,2],
            multi=True
    ),
    ], style = {"margin-top":"2px","margin-bottom":"4px"}),
    
        html.Div([
            html.P('Seleccione una zona')
    ]),
        html.Div([
        dcc.Dropdown(
            id='zona',
            options=[{'label': i, 'value': j} for i,j in zip(zonas.zona,zonas.codigo_zona)],
            value=[1,2,3,4,5],
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
     Output('otros', 'columns'),
     Output('prestacion_nombre', 'children'),
     Output('prestador_nombre', 'children')
    ],

     [Input('prestacion', 'value'),
        Input('prestador_ref', 'value'),
      Input('provincia', 'value'),
       Input('zona', 'value'),
      Input('ambu_inte',"value")
])

def filtros(prestacion,prestador,provincia,zona,ambu_inte):

     # "Ambulatorio"  "Internación"
    
    print(prestacion,prestador,provincia,zona,ambu_inte)
    menor = str(datetime.date.today() - datetime.timedelta(days=180))
    provincia = str(provincia).strip("]").strip("[")
    zona = str(zona).strip("]").strip("[")
    
    df = querydbtopandas()
    #df = querydbtopandas(f"""select  a13.id_pre_prestador  id_pre_prestador,
    #max(a17.desc_pre_nombre)  desc_pre_nombre,
    #max(a17.vigente)  vigente,
    #a11.id_pres_prestacion  id_pres_prestacion,
    #max(a16.desc_pres_prestacion)  desc_pres_prestacion,
    #max(a16.prestac_pres_prestacion)  prestac_pres_prestacion,
    #a11.conve  conve,
    #max(a14.tipo)  tipo,
    #id_afi_zona,
    #id_afi_provincia,
    #a11.vigencia vigencia, 
    #max(a14.denominacion)  denominacion,
    #sum(a11.Valor_Unitario_Total_Vigente)  VALORCONVENIDO
    #from    DBA.ft_maestro_convenios    a11
    #join    DBA.d_conv_prestador    a13
    #  on     (a11.conve = a13.convenio)
    #join    DBA.d_conv_convenios    a14
    #  on     (a11.conve = a14.conve)
    #join    DBA.d_pres_prestacion    a16
    #  on     (a11.id_pres_prestacion = a16.id_pres_prestacion)
    #join    DBA.d_pre_prestador    a17
    #  on     (a13.id_pre_prestador = a17.id_pre_prestador)
    #where  vigencia >= date("{menor}")
    #and  RTRIM(a16.prestac_pres_prestacion) in ("{prestacion}")
    #and id_afi_provincia in ({provincia})
    #and id_afi_zona in ({zona})
    #group by    a13.id_pre_prestador,
    #a11.id_pres_prestacion,
    #a11.vigencia,
    #id_afi_zona,
    #id_afi_provincia,
    #a11.conve""")
    
    if ambu_inte == "Ambulatorio":
        df = df[~df.denominacion.str.contains("SIMECO")]
        df = df[~df.denominacion.str.contains("QAP")]
        df = df[~df.denominacion.str.contains("BLACK")]
        df = df[~df.denominacion.str.contains("qualitas")]
    elif ambu_inte == "Internación": 
        df_internacion1 = df[df.denominacion.str.contains("Internación")] #407257 
        df = df[~df.denominacion.str.contains("Internación")] 

        df_internacion2 = df[df.denominacion.str.contains("Internados")]
        df = df[~df.denominacion.str.contains("Internados")] 

        df = pd.concat([df_internacion1, df_internacion2])
    
    for i in df.id_pre_prestador:
        if i == prestador:
            data = df[df["id_pre_prestador"]== i]
            max_date = data.vigencia.max()
            referencia = data[data["vigencia"]==max_date].VALORCONVENIDO
            nombre_referencia = data[data["vigencia"]==max_date].desc_pre_nombre

    referencia = referencia.values[0]

    ultimas_fechas = []
    for i,j in zip(df[["id_pre_prestador","denominacion"]].drop_duplicates().id_pre_prestador,df[["id_pre_prestador","denominacion"]].drop_duplicates().denominacion):
        ultimas_fechas.append(df[(df["id_pre_prestador"]==i) & (df["denominacion"]==j)].vigencia.max())
    unicos = df[["id_pre_prestador","denominacion"]].drop_duplicates()
    unicos["vigencia"] = ultimas_fechas
    df = unicos.merge(df,how="left")
    df["Porcentaje en propios"] =(df["VALORCONVENIDO"]/referencia)-1
    final = df[["id_pre_prestador","desc_pre_nombre","conve","denominacion", "VALORCONVENIDO","Porcentaje en propios"]]
    final = final.round(2)
    data_ob_otros = final.to_dict('rows')
    columns_ob_otros = [{'name': i, 'id': i} for i in final.columns.tolist()]
    prestacion_nombre = "Este código corresponde a " + df.desc_pres_prestacion.unique()[0]
    prestador_nombre = "Este id corresponde al prestador " + nombre_referencia.values[0]
    return data_ob_otros, columns_ob_otros, prestacion_nombre,prestador_nombre

