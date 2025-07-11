from config import DATA_PATH_USUARIOS

def cargar_datos():
    usuarios = []
    try:
        with open(DATA_PATH_USUARIOS, 'r') as f:
            lineas = f.read().splitlines()
            for i in range(0, len(lineas), 2):
                usuario = {
                    'usuario': lineas[i],
                    'contraseña': lineas[i+1]
                }
                usuarios.append(usuario)
    except FileNotFoundError:
        return []
    return usuarios

def guardar_datos(datos):
    with open(DATA_PATH_USUARIOS, 'w') as f:
        for user in datos:
            f.write(f'{user['usuario']}\n')
            f.write(f'{user['contraseña']}\n')