from tkinter import messagebox
import customtkinter as customtk
from PIL import Image
from config import ASSETS_PATH_LOGIN_IMG
from data.manejo_users import cargar_datos, guardar_datos
from utils.cifrado import cifrar_data
from utils.funciones_ui import centrar_ventana
import bcrypt

class Registro(customtk.CTkToplevel):
    def __init__(self, login):
        super().__init__(login)

         #config. de ventana
        self.title('MOVIEBOX')

        self.login = login

        ancho_vent = 350
        altura_vent = 500

        #imagen y contenido del frame izq
        frame_izq = customtk.CTkFrame(
            master=self,
            width= 250,
            height=350
            )
        frame_izq.pack(
            side= 'left',
            fill='both'
            )
        frame_izq.pack_propagate(False)

        img = Image.open(ASSETS_PATH_LOGIN_IMG)
        img = img.resize((250, 350))
        ctk_img = customtk.CTkImage(
            light_image=img,
            dark_image=img,
            size=(250, 350)
            )

        img_label = customtk.CTkLabel(
            master=frame_izq,
            image= ctk_img,
            text=''
            )
        img_label.image = ctk_img
        img_label.pack(
            side='top',
            pady=(5,10)
            )

         #Etiquetas y campos de entrada
        frame_der = customtk.CTkFrame(
            master=self,
            width=250,
            height=350
            )
        frame_der.pack(
            side='right',
            fill= 'both',
            expand=True,
            padx= (10,10),
            pady =(10,10)
            )

        label = customtk.CTkLabel(
            master=frame_der,
            text='CREAR NUEVA CUENTA',
            font=('Roboto', 15, 'bold'),
            bg_color='Navyblue',
            width= 200,
            corner_radius=15
            )
        label.pack(pady=10)

        label = customtk.CTkLabel(
            master=frame_der,
            text='Nuevo usuario',
            font=('Roboto', 10, 'bold')
            )
        label.pack(
            pady=(5,0),
            padx= (5,130)
            )
        usuario_entry = customtk.CTkEntry(
            master=frame_der,
            placeholder_text='Usuario',
            width=200
            )
        usuario_entry.pack(
            pady=(5,0),
            padx=10
            )

        label = customtk.CTkLabel(
            master=frame_der,
            text='Contraseña',
            font=('Roboto', 10, 'bold')
            )
        label.pack(
            pady=(5,0),
            padx= (5,140)
            )
        contraseña_entry = customtk.CTkEntry(
            master=frame_der,
            placeholder_text='Contraseña',
            show= '*',
            width= 200
            )
        contraseña_entry.pack(
            pady=(5,0),
            padx=10
            )

        label = customtk.CTkLabel(
            master=frame_der,
            text='Confirmar contraseña',
            font=('Roboto', 10, 'bold')
            )
        label.pack(
            pady=(5,0),
            padx= (5,90)
        )
        rep_contraseña_entry = customtk.CTkEntry(
            master=frame_der,
            placeholder_text='Contraseña',
            show= '*',
            width=200
            )
        rep_contraseña_entry.pack(
            pady=(5,10),
            padx=10
            )

        def new_usuario():
            try:
                usuario = usuario_entry.get()
                contraseña = contraseña_entry.get()
                conf_contraseña = rep_contraseña_entry.get()
                
                # Validaciones
                if not usuario or not contraseña or not conf_contraseña:
                    messagebox.showerror('Error', 'Todos los campos son obligatorios')
                    return

                usuarios = cargar_datos()
                
                if contraseña != conf_contraseña:
                    messagebox.showerror('Error', 'Confirme la contraseña de manera correcta')
                    return
                    
                # Procesamiento de datos
                nombre_usuario = cifrar_data(usuario)
                contra = cifrar_data(contraseña)
                contra_bytes = contra.encode('utf-8')  # Convertimos a bytes antes de hashear
                hashed_contraseña = bcrypt.hashpw(contra_bytes, bcrypt.gensalt())

                nuevo_usuario = {
                    'usuario': nombre_usuario,
                    'contraseña': hashed_contraseña.decode('utf-8')
                }

                usuarios.append(nuevo_usuario)
                guardar_datos(usuarios)

                messagebox.showinfo('Éxito', 'Usuario registrado correctamente')
                self.destroy()
                self.login.deiconify()
                
            except Exception as e:
                messagebox.showerror('Error', f'Error al registrar usuario: {str(e)}')

        sign_btn = customtk.CTkButton(
            master=frame_der,
            text='Registrarme',
            font=('Roboto',12, 'bold'),
            width=180,
            hover_color= 'NavajoWhite',
            command=new_usuario
            )
        sign_btn.pack(pady=20)

        centrar_ventana(self, altura_vent, ancho_vent)