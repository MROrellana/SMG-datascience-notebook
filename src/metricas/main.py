from main_page import app
from consultas_prestadores import App_1
from consultas_prestadores_modelo import App_1
from desconocimiento import App_1
from imagenes import App_1
from calificaciones import App_1
from cirugias import App_1
from quejas import App_1
from farmacia import App_1
from observatorio import App_1

from graficos import App_1
from grafico_cirugias import App_1


from grafico_ejemplo import app

from server import server

if __name__ == '__main__':
    server.run(debug= True, host='0.0.0.0',port=8050)