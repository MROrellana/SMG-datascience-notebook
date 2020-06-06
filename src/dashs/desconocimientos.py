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

App_2 = dash.Dash(__name__, server=server, url_base_pathname='/consultas_prestadores_modelo/', external_stylesheets=external_stylesheets )

prestadores_modelo = pd.read_csv("prestadores_modelo.csv",usecols= ["prestadores_modelo"])["prestadores_modelo"].tolist()
modelos = str(prestadores_modelo).strip("[").strip("]")
colors = {
    'background': '#111111',
    'text': 'grey'
}

App_2.layout = html.Div([
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


@App_2.callback(
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
    
    df = querydbtopandas()
    #df = querydbtopandas(f"""select a11.id_pres_prestacion  id_pres_prestacion,
    #   a16.desc_pres_prestacion  desc_pres_prestacion,
    #   a16.prestac_pres_prestacion  prestac_pres_prestacion,
    #   a11.id_pre_prestador  id_pre_prestador, 
    #   a13.desc_pre_nombre  desc_pre_nombre,
    #   a13.vigente  vigente,
    #   a11.id_afi_afiliado  id_afi_afiliado,    
    #   FLOOR(DATEDIFF(year, a14.naci_fecha, a11.id_tie_dia_consumo)) edad_afiliado,
    #   a19.desc_prof_especialidad desc_prof_especialidad,
    #   sum(a11.i_ft_importe_prestacion)  RDENES,
    #   sum(case  when (  i_ft_importe_prestacion *i_Ft_Cantidad <= 0) then 0  when  (i_ft_importe_prestacion *i_Ft_Cantidad <> 0 ) then i_Ft_Cantidad   end )  CANTIDADORDENES0
    #    from        DBA.ft_ordenes        a11
    #   join        DBA.d_pre_prestador        a13
    #     on        (a11.id_pre_prestador = a13.id_pre_prestador)
    #   join        DBA.afi_afiliados        a14
    #     on        (a11.id_afi_afiliado = a14.id_afiliado)
    #   join        DBA.d_pres_prestacion        a16
    #     on        (a11.id_pres_prestacion = a16.id_pres_prestacion)      
    #   join       DBA.d_prof_convertir_especialidad a19      
    #    on         (a13.id_pre_especialidad  = a19.id_prof_especialidad)
    #    where        (a13.id_pre_tipo in ('E', 'P')   
    #    and i_ft_importe_prestacion > 0
    #    and a11.id_nom_nomenclador in (5)
    #    and a11.id_pre_prestador in ({modelos}) 
    #    and cast(id_tie_dia_consumo as date) >= date("{start_date_string}") and cast(id_tie_dia_consumo as date) < date("{end_date_string}")
    #    and a13.id_afi_zona in (2, 3, 4, 5)
    #    and a13.id_afi_provincia in (1, 2)
    #    and a16.prestac_pres_prestacion not in ('42010101', '42010104', '42010109', '42010110', '42010114', '42010117', '42010118', '42010120', '42010125', '42010504', '42011001',         '42011002', '42011203', '42011903', '42013102', '42013501', '42013605', '42013606', '42013607', '42013608', '42020100', '42020102', '42020103', '42020104', '42020105',             '42020106', '42020107', '42020108', '42020109', '42020110', '42020111', '42020112', '42020200', '42020202', '42020203', '42020300', '42020301', '42020302', '42021900',             '42021901', '42023200', '42040100', '42040101', '42040102', '42040103', '42040105', '42040106', '42041200', '42041201', '42041300', '42041301', '42041701', '42041702',             '42042301','42043000', '42043001', '42043101', '42043201', '42420101', '42420103', '42420104'))
    #    group by        a11.id_pres_prestacion,   
    #           a16.desc_pres_prestacion,
    #           a16.prestac_pres_prestacion,
    #           a11.id_pre_prestador,
    #           a13.desc_pre_nombre,     
    #           a19.desc_prof_especialidad,
    #           a13.vigente,
    #           a11.id_afi_afiliado,
    #           edad_afiliado""")
    
    total_consultas_prestador = df.groupby(["id_pre_prestador"])["CANTIDADORDENES0"].sum()
    mas_de_40_consultas = total_consultas_prestador[total_consultas_prestador > 40].index
    df = df[df["id_pre_prestador"].isin(mas_de_40_consultas)]
    reconsultas = df.groupby(["id_pre_prestador", "desc_pre_nombre", "desc_prof_especialidad", "id_afi_afiliado"])["CANTIDADORDENES0"].sum().reset_index()
    reconsultas["uno"] = 1
    pivot_1 = pd.pivot_table(reconsultas, values='uno', index=['id_pre_prestador', "desc_pre_nombre", "desc_prof_especialidad"],
                 columns=['CANTIDADORDENES0'], aggfunc=np.sum).fillna(0)
    pivot_1["Más de 4 - Q afiliados"] = pivot_1[pivot_1.columns.tolist()[4:]].sum(axis=1)
    pivot_1.drop(pivot_1.columns.tolist()[4:-1], axis=1,inplace=True)
    #calculo la edad promedio de los afiliados 
    edad_promedio_afiliados = pd.DataFrame(df.groupby(["id_pre_prestador",  "desc_pre_nombre", "desc_prof_especialidad"])["edad_afiliado"].mean())
    #el total de consultas del prestador 
    total_consultas_prestador = df.groupby(["id_pre_prestador",  "desc_pre_nombre", "desc_prof_especialidad"])["CANTIDADORDENES0"].sum()
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
    "desc_prof_especialidad": "Especialidad","id_pre_prestador": "Prestador", "edad_afiliado": "Promedio edad de afiliados", "CANTIDADORDENES0": "Total Consultas" },inplace=True)    
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

