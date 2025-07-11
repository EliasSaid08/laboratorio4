##esta funcion es para poder centrar las ventanas de la interfaz grafica

## en resumen lo que hace es calcular cual seria el sobrante o margin segun el tamaño de la pantalla
## y aplicarlo en el metodo geometry
def centrar_ventana(ventana, altura, ancho):
    ventana.geometry(f'{ancho}x{altura}')
    ventana.update_idletasks()

    pantalla_ancho = ventana.winfo_screenwidth()
    pantalla_alto = ventana.winfo_screenheight()

    x = (pantalla_ancho - ancho) // 2
    y = (pantalla_alto - altura) // 2

    ventana.geometry(f'{altura}x{ancho}+{x}+{y}')