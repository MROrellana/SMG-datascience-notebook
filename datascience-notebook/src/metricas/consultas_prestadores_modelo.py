import dash
from datetime import datetime as dt
import dash_html_components as html
import dash_core_components as dcc
import pandas as pd
from dash.dependencies import Input, Output

from datetime import date
import dash_table
import numpy as np

from server import server

from dbconn import querydb, querydbtopandas 


external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css 5", 
                        'https://codepen.io/amyoshino/pen/jzXypZ.css']

App_1 = dash.Dash(__name__, server=server, url_base_pathname='/consultas_prestadores_modelo/', external_stylesheets=external_stylesheets )

path = "parametros_consultas/prestadores_modelo.csv"

prestadores_modelo = pd.read_csv(path ,usecols= ["prestadores_modelo"])["prestadores_modelo"].tolist()
modelos = str(prestadores_modelo).strip("[").strip("]")

path1 = "parametros_consultas/prestaciones_excluidas.xlsx"

prestaciones_excluidas = pd.read_excel(path1 ,usecols = ["prestac_pres_prestacion"], dtype=str )["prestac_pres_prestacion"].tolist()
prestaciones_excluidas = str(prestaciones_excluidas).strip("[").strip("\"]")

zona = "2,3,4,5"
provincia = "1,2"


colors = {
    'background': '#111111',
    'text': 'grey'
}

App_1.layout = html.Div([
    html.Div([html.H1(
            children='Consultas por período por prestador',
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
            children='Tabla de prestadores modelo',
            style={
                'textAlign': 'center',
                'color': colors['text'],
                "fontSize" : 25
        }),


        html.Div([
        dash_table.DataTable(id='modelos', 
                    sort_action='native',
                    filter_action='native',
                    style_cell={'fontSize':12, 'font-family':'sans-serif'},
                    style_table={'overflowX': 'scroll', 'maxHeight': '500px', 'overflowY': 'scroll' },
                    style_data_conditional=[     
                       {
                          'if': {'column_id': '2 consultas - participación %',
                         'filter_query': "{2 consultas - participación %} >= 40"
                             },
                         'backgroundColor': '#cb3234',
                         'color': 'white',
                        },


                        {
                          'if': {'column_id': '2 consultas - participación %',
                         'filter_query': "{2 consultas - participación %} < 40 and {2 consultas - participación %} > 20",
                             },
                         'backgroundColor': '#f8f32b',  
                         'color': 'white',
                        },


                         {
                          'if': {'column_id': '2 consultas - participación %',
                         'filter_query': "{2 consultas - participación %} <= 20"
                             },
                         'backgroundColor': '#008f39',
                         'color': 'white',
                        },
               
                        
                         {
                          'if': {'column_id': '3 consultas - participación %',
                         'filter_query': "{3 consultas - participación %} >= 20"
                             },
                         'backgroundColor': '#cb3234',
                         'color': 'white',
                        },
                         {
                          'if': {'column_id': '3 consultas - participación %',
                         'filter_query': "{3 consultas - participación %} < 20 and {3 consultas - participación %} > 10"
                             },
                         'backgroundColor': '#f8f32b',
                         'color': 'white',
                        },

                         {
                          'if': {'column_id': '3 consultas - participación %',
                         'filter_query': "{3 consultas - participación %} <= 10"
                             },
                         'backgroundColor': '#008f39',
                         'color': 'white',
                        },
                         {
                          'if': {'column_id': '4 consultas - participación %',
                         'filter_query': "{4 consultas - participación %} >= 10"
                             },
                         'backgroundColor': '#cb3234',
                         'color': 'white',
                        },
                         {
                          'if': {'column_id': '4 consultas - participación %',
                         'filter_query': "{4 consultas - participación %} < 10 and {4 consultas - participación %} > 2"
                             },
                         'backgroundColor': '#f8f32b',
                         'color': 'white',
                        },

                         {
                          'if': {'column_id': '4 consultas - participación %',
                         'filter_query': "{4 consultas - participación %} <= 2"
                             },
                         'backgroundColor': '#008f39',
                         'color': 'white',
                        },
                         {
                          'if': {'column_id': 'Más de 4 - participación %',
                         'filter_query': "{Más de 4 - participación %} > 0"
                             },
                         'backgroundColor': '#cb3234',
                         'color': 'white',
                        },

                         {
                          'if': {'column_id': 'Más de 4 - participación %',
                         'filter_query': "{Más de 4 - participación %} eq 0"
                             },
                         'backgroundColor': '#008f39',
                         'color': 'white',
                        },
                        {
                          'if': {'column_id': 'Participación %',
                         'filter_query': "{Participación %} >= 50"
                             },
                         'backgroundColor': '#cb3234',
                         'color': 'white',
                        },
                         {
                          'if': {'column_id': 'Participación %',
                         'filter_query': "{Participación %} < 50 and {Participación %} >30"
                             },
                         'backgroundColor': '#f8f32b',
                         'color': 'white',
                        },

                         {
                          'if': {'column_id': 'Participación %',
                         'filter_query': "{Participación %} <= 30"
                             },
                         'backgroundColor': '#008f39',
                         'color': 'white',
                        },
                        
                        ]
                             
                             
                             
                     ),
    ],

    )


    ])


@App_1.callback(
    [Output('modelos', 'data'),
    Output('modelos', 'columns')],

     [Input('my-date-picker-range', 'start_date'),
      Input('my-date-picker-range', 'end_date')
      ])

def filtros_ordenes(start_date, end_date):
    start_date = dt.strptime(start_date.split('T')[0], '%Y-%m-%d')
    start_date_string = start_date.strftime('%Y-%m-%d')
    
    end_date = dt.strptime(end_date.split('T')[0], '%Y-%m-%d')
    end_date_string = end_date.strftime('%Y-%m-%d')
    
    df = querydbtopandas(f"""select a11.id_pres_prestacion,
       a16.prestac_pres_prestacion,
       a11.id_pre_prestador,
       a13.desc_pre_nombre,
       a11.id_afi_afiliado ,  
       Q.deno,
       a11.id_tie_dia_consumo,   
       FLOOR(DATEDIFF(year, a14.naci_fecha, a11.id_tie_dia_consumo)) edad_afiliado 
       from        DBA.ft_ordenes        a11
       join        DBA.d_pre_prestador        a13
         on        (a11.id_pre_prestador = a13.id_pre_prestador)
       join        DBA.afi_afiliados        a14
         on        (a11.id_afi_afiliado = a14.id_afiliado)
       join        DBA.d_pres_prestacion        a16
         on        (a11.id_pres_prestacion = a16.id_pres_prestacion)     
       join       DBA.d_prof_convertir_especialidad a19  
        on         (a13.id_pre_especialidad  = a19.id_prof_especialidad)
       LEFT JOIN dba.prestad_costo_centros E
        ON a11.id_pre_prestador = E.prestad and E.baja_fecha is null and e.prepaga = ( select min(PCC1.prepaga) from dba.prestad_costo_centros PCC1 where PCC1.prestad =  e.prestad )   
       LEFT JOIN dba.costo_centros Q
        ON E.centro = Q.centro
where        (a13.id_pre_tipo in ('E', 'P')            
and a11.id_nom_nomenclador in (5)            
and cast(id_tie_dia_consumo as date) >= date("{menor}") and cast(id_tie_dia_consumo as date) < date("{mayor}")
and a13.id_afi_zona in ({zona})
and a13.id_afi_provincia in ({provincia})
       and a11.id_pre_prestador in ({modelos})

and RTRIM(a16.prestac_pres_prestacion) not in ({prestaciones_excluidas}))
group by a11.id_pres_prestacion,
       a16.prestac_pres_prestacion,
       a11.id_pre_prestador,
       a13.desc_pre_nombre,
       Q.deno,
       a11.id_afi_afiliado,
       a11.id_tie_dia_consumo,
       edad_afiliado""")
    
    total_consultas_prestador = df["id_pre_prestador"].value_counts()
    mas_de_40_consultas = total_consultas_prestador[total_consultas_prestador >= 30].index

    df = df[df["id_pre_prestador"].isin(mas_de_40_consultas)]
    reconsultas = df.groupby(["id_pre_prestador", "desc_pre_nombre", "deno", "id_afi_afiliado"])["id_afi_afiliado"].count().rename("CANTIDADORDENES0").reset_index()
    reconsultas["uno"] = 1

    pivot_1 = pd.pivot_table(reconsultas, values='uno', index=['id_pre_prestador', "desc_pre_nombre", "deno"],
                 columns=['CANTIDADORDENES0'], aggfunc=np.sum).fillna(0)
    pivot_1["Más de 4 - Q afiliados"] = pivot_1[pivot_1.columns.tolist()[4:]].sum(axis=1)
    edad_promedio_afiliados = pd.DataFrame(df.groupby(["id_pre_prestador",  "desc_pre_nombre", "deno"])["edad_afiliado"].mean())
    total_consultas_prestador = reconsultas.groupby(["id_pre_prestador",  "desc_pre_nombre", "deno"])["CANTIDADORDENES0"].sum()
    pivot = pd.concat([total_consultas_prestador,edad_promedio_afiliados, pivot_1],axis=1)
    pivot.reset_index(inplace=True)

    pivot["Consultas - participación %"] =  (pivot[1]/pivot["CANTIDADORDENES0"])*100
    pivot["2 consultas - participación %"] =  ((pivot[2]*2)/pivot["CANTIDADORDENES0"])*100
    pivot["3 consultas - participación %"] =  ((pivot[3]*3)/pivot["CANTIDADORDENES0"])*100
    pivot["4 consultas - participación %"] =  ((pivot[4]*4)/pivot["CANTIDADORDENES0"])*100
    pivot["Participación %"] = 100 - pivot["Consultas - participación %"]
    pivot["Más de 4 - participación %"] = pivot["Participación %"] - (pivot["2 consultas - participación %"]+pivot["3 consultas - participación %"]+pivot["4 consultas - participación %"])
    pivot["Total de reconsultas"] = pivot[2] + pivot[3] + pivot[4] + pivot["Más de 4 - Q afiliados"]
    pivot.rename(columns= {1: "Consultas - Q afiliados", 2: "2 consultas - Q afiliados", 3: "3 consultas - Q afiliados", 4: "4 consultas - Q afiliados", "desc_pre_nombre": "Razon social",
    "deno": "Especialidad","id_pre_prestador": "Prestador", "edad_afiliado": "Promedio edad de afiliados", "CANTIDADORDENES0": "Total Consultas" },inplace=True)    
    pivot = pivot.sort_values("Participación %", ascending=False).round(2)
    pivot = pivot.reset_index(drop=True)
    pivot = pivot[['Prestador', 'Razon social', 'Especialidad', 'Total Consultas',
           'Promedio edad de afiliados', 'Consultas - Q afiliados','Consultas - participación %',
           '2 consultas - Q afiliados', '2 consultas - participación %',
           '3 consultas - Q afiliados', '3 consultas - participación %',
           '4 consultas - Q afiliados',  '4 consultas - participación %',
           'Más de 4 - Q afiliados',  'Más de 4 - participación %',
           'Total de reconsultas','Participación %']]

    data_ob_otros = pivot.to_dict('rows')
    columns_ob_otros = [{'name': i, 'id': i} for i in pivot.columns.tolist()]
    return data_ob_otros, columns_ob_otros

