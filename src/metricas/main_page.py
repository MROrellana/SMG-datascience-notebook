import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from server import server


external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css 5", 
                        'https://codepen.io/amyoshino/pen/jzXypZ.css']

app = dash.Dash(__name__, suppress_callback_exceptions=True, url_base_pathname='/base/', server=server, external_stylesheets=external_stylesheets)

style ={"margin-bottom": "10px", 
        "margin-left" : "15px",
        "font-size" : "25px",
        'textAlign': 'center',
        'color': "grey"
             }

app.layout =  html.Div(children=[
    html.H1('Profiling de prestadores', style ={ "margin-left" : "15px",  'textAlign': 'center', "color" : "#464E51" }),
    dcc.Link(' - Consultas de prestadores', href='/consultas_prestadores/', refresh=True, target="_blank",   style = style ),
    html.Br(),
    dcc.Link(' - Consultas de prestadores modelo', href='/consultas_prestadores_modelo/', refresh=True, target="_blank",  style = style  ),
    html.Br(),
    dcc.Link(' - Imágenes', href='/imagenes/', refresh=True, target="_blank",   style = style ),
    html.Br(),
    dcc.Link(' - Desconocimiento', href='/desconocimiento/', refresh=True, target="_blank",  style = style ),
    html.Br(),
    dcc.Link(' - Calificaciones', href='/calificaciones/', refresh=True, target="_blank",  style = style  ),
    html.Br(),
    dcc.Link(' - Cirugías', href='/cirugias/', refresh=True, target="_blank",   style = style ),
    html.Br(),
    dcc.Link(' - Presupuesto', href='/presupuesto/', refresh=True, target="_blank",  style = style ),
    html.Br(),
    dcc.Link(' - Observatorio de precios', href='/observatorio/', refresh=True, target="_blank",  style = style ),
    html.Br(),
    dcc.Link(' - Quejas', href='/quejas/', refresh=True, target="_blank",  style = style ),
    html.Br(),
    dcc.Link(' - Farmacia', href='/farmacia/', refresh=True, target="_blank",  style = style ),
])
