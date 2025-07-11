from tkinter import messagebox
import customtkinter as customtk
from PIL import Image
from config import ASSETS_PATH_LOGIN_IMG
from utils.funciones_ui import centrar_ventana
from utils.cifrado import descifrar_data
from data.manejo_users import cargar_datos
from .menu_principal import MovieCatalog
from .signIn import Registro
import bcrypt

customtk.set_appearance_mode('Dark')
customtk.set_default_color_theme('dark-blue')

class App(customtk.CTk):
    def __init__(self):
        super().__init__()

        #config. de ventana
        self.title('MOVIEBOX')

        self.ventana_menu = None
        self.ventana_registro = None

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
            height=350,
            corner_radius=10
            )
        
        frame_der.pack(
            side='right',
            fill= 'both',
            expand= True,
            padx= (10,10),
            pady =(10,10)
            )

        label = customtk.CTkLabel(
            master=frame_der,
            text='BIENVENIDO A MOVIEBOX',
            font=('Roboto', 15, 'bold'),
            bg_color='Navyblue',
            corner_radius=15,
            width=200
            )
        
        label.pack(
            pady=(20)
            )

        usuario_entry = customtk.CTkEntry(
            master=frame_der,
            placeholder_text='Usuario',
            width=200
            )
        
        usuario_entry.pack(
            pady=10,
            padx=10
            )

        contraseña_entry = customtk.CTkEntry(
            master=frame_der,
            placeholder_text='Contraseña',
            show= '*',
            width=200
            )
        
        contraseña_entry.pack(
            pady=5,
            padx=10
            )

        def login():
            username = usuario_entry.get()
            passoword = descifrar_data(contraseña_entry.get())

            if not username or not passoword:
                    messagebox.showerror('Error', 'Todos los campos son obligatorios')
                    return
            
            credenciales = cargar_datos()

            usuario = next((u for u in credenciales if descifrar_data(u['usuario']) == username), None)
            if usuario and bcrypt.checkpw(passoword.encode('utf-8'), usuario['contraseña'].encode('utf-8')):
                 #abrir menu_principal
                 self.open_movie_catalog(username)
            else:
                 messagebox.showerror('Error', 'Credenciales inválidas')

        login_btn = customtk.CTkButton(
            master=frame_der,
            text='Iniciar sesión',
            font=('Roboto',12, 'bold'),
            width=180,
            command=login
            )
        login_btn.pack(
            pady=20
            )

        label = customtk.CTkLabel(
            master=frame_der,
            text='¿No tienes una cuenta?',
            font=('Roboto', 12)
            )
        label.pack(
            pady=10
            )

        registro_btn = customtk.CTkButton(
            master=frame_der,
            text='Registrarme',
            font=('Roboto',12, 'bold'),
            width=180,
            fg_color='gray',
            command=self.abrir_registro
            )
        registro_btn.pack()

        centrar_ventana(self, altura_vent, ancho_vent)

    def open_movie_catalog(self, username):
        # Cerrar la ventana de inicio de sesión
        self.withdraw()  # Oculta la ventana de inicio de sesión
        if self.ventana_menu is None or not self.ventana_menu.winfo_exists():
            self.ventana_menu = MovieCatalog(self, username)
            self.ventana_menu.protocol('WM_DELETE_WINDOW', self.menu_cat_close)

    def menu_cat_close(self):
        if self.ventana_menu:
            self.ventana_menu.destroy()
            self.ventana_menu = None
        self.deiconify()
    
    def menu_reg_close(self):
        if self.ventana_registro:
            self.ventana_registro.destroy()
            self.ventana_registro = None
        self.deiconify()

    def abrir_registro(self):
        self.withdraw()

        if self.ventana_registro is None or not self.ventana_registro.winfo_exists():
            self.ventana_registro = Registro(self)
            self.ventana_registro.protocol('WM_DELETE_WINDOW', self.menu_reg_close)


