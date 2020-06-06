import dash
import dash_html_components as html
from server import server
# Set-up endpoint 1
App_3 = dash.Dash(__name__, server=server, url_base_pathname='/app3/')
App_3.layout = html.H1('App 3')