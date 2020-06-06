import dash
from datetime import datetime as dt
import dash_html_components as html
import dash_core_components as dcc
app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.DatePickerRange(
        id='my-date-picker-range',
        min_date_allowed=dt(1995, 8, 5),
        max_date_allowed=dt(2030, 9, 19),
        initial_visible_month=dt(2019, 8, 1),
        end_date=dt(2019, 12, 30).date()
    ),
    html.Div(id='output-container-date-picker-range')
])

@app.callback(
    dash.dependencies.Output('output-container-date-picker-range', 'children'),
    [dash.dependencies.Input('my-date-picker-range', 'start_date'),
     dash.dependencies.Input('my-date-picker-range', 'end_date')])
def update_output(start_date, end_date):
    start_date = dt.strptime(start_date.split('T')[0], '%Y-%m-%d')
    start_date_string = start_date.strftime('%Y-%m-%d')
    
    return start_date_string


if __name__ == '__main__':
	app.run_server(debug = True, host='0.0.0.0',port=8050)
