from consultas_prestadores import App_1
from consultas_prestadores_modelo import App_1
from farmacia import App_1
from dashapp3 import App_3
from server import server

if __name__ == '__main__':
    server.run(debug= True, host='0.0.0.0',port=8050)