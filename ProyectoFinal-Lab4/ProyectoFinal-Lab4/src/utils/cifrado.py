# Cifrar credenciales

def cifrar_data(credencial):
    caracteres = 'abcdefghijklmnopqrstuvwxyz'
    lista = list(caracteres)
    lista_cifrada = lista[::-1]

    credencial_cifrada = ''
    for char in credencial:
        if char in lista:
            indice = lista.index(char)
            credencial_cifrada += lista_cifrada[indice]
        else:
            credencial_cifrada += char
    return credencial_cifrada

# Descifrar credenciales

def descifrar_data(credencial):
    caracteres = 'abcdefghijklmnopqrstuvwxyz'
    lista = list(caracteres)
    lista_descifrada = lista[::-1]

    credencial_descifrada = ''
    for char in credencial:
        if char in lista:
            indice = lista.index(char)
            credencial_descifrada += lista_descifrada[indice]
        else:
            credencial_descifrada += char
    return credencial_descifrada


"""  testing de las funciones:

a= input('ingrese un usuario: ')
print('cifrando usuario...')
b = cifrar_data(a)
print(b)

print('descifrando usuario...')
c= descifrar_data(b)
print(c)

""" # funcionan correctamente-


