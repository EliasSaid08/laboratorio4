import os

# Actua como capa entidad
#---mejora la comunicacion entre archivos de diferentes rutas
#---evita problemas de ruteo al ejecutar desde diferentes PC

RUTA_BASE = os.path.dirname(os.path.dirname(__file__))

DATA_PATH_REGLAS = os.path.join(RUTA_BASE, 'data', 'reglas.pl')
DATA_PATH_USUARIOS = os.path.join(RUTA_BASE, 'data', 'usuarios.txt')
ASSETS_PATH_LOGIN_IMG = os.path.join(RUTA_BASE, 'assets','img','login-image.jpeg')