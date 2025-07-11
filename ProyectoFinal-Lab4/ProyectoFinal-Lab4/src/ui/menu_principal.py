import customtkinter as ctk
from tkinter import ttk
from PIL import Image, ImageTk
import requests
from io import BytesIO
import json
import os
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
from dotenv import load_dotenv
from config import RUTA_BASE
from models.sist_recomendacion import RecommendationManager

load_dotenv()
key = os.getenv('omdb_key')

class MovieCatalog(ctk.CTkToplevel):
    def __init__(self, parent ,username):
        super().__init__(parent)

        # Configuración de la API OMDB
        self.api_key = key
        self.base_url = "http://www.omdbapi.com/"
        
        # Datos del usuario
        self.recommendation_manager = RecommendationManager()
        self.username = username
        self.watched_movies = self.load_user_data()
        
        # Configuración de la ventana principal
        self.title("Catálogo de Películas")
        self.geometry("1200x800")
        self.attributes('-fullscreen', True)
        self.bind('<Escape>', self.exit_fullscreen)
        
        # Configuración del tema
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Variables de estado
        self.current_page = 1
        self.movies = []
        self.search_results = []
        self.current_search = ""
        
        # Crear el layout principal
        self.create_navbar()
        self.create_main_content()

    def exit_fullscreen(self, event = None):
                self.attributes('-fullscreen', False)

    def create_navbar(self):
        # Frame para la barra de navegación
        self.navbar = ctk.CTkFrame(self, height=50)
        self.navbar.pack(fill="x", padx=10, pady=5)
        
        # Logo o título de la aplicación
        ctk.CTkLabel(
            self.navbar,
            text="🎬 Moviebox - Catálogo",
            font=("Arial", 16, "bold")
        ).pack(side="left", padx=10)
        
        # Frame para elementos del lado derecho
        right_items = ctk.CTkFrame(self.navbar, fg_color="transparent")
        right_items.pack(side="right", padx=10)
        
        # Mostrar nombre de usuario
        self.user_label = ctk.CTkLabel(
            right_items,
            text=f"👤 {self.username}",
            font=("Arial", 12),
            bg_color='green',
            height=20
        )
        self.user_label.pack(side="left", padx=10)
        
        # Botón para ver películas vistas
        self.watched_button = ctk.CTkButton(
            right_items,
            text="📋 Mis Películas",
            command=self.show_watched_movies
        )
        self.watched_button.pack(side="left", padx=10)
        
        dark_red = '#800000'

        # Botón de logout
        self.logout_button = ctk.CTkButton(
            right_items,
            text="🚪 Cerrar Sesión",
            fg_color= dark_red,
            command=self.logout
        )
        self.logout_button.pack(side="left", padx=10)

    def create_main_content(self):
 # Frame principal
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Frame superior para búsqueda
        self.search_frame = ctk.CTkFrame(self.main_frame)
        self.search_frame.pack(fill="x", padx=10, pady=10)

        self.search_entry = ctk.CTkEntry(
            self.search_frame, 
            placeholder_text="Buscar películas...",
            width=300
        )
        self.search_entry.pack(side="left", padx=10)
        self.search_entry.bind('<Return>', lambda e: self.search_movies())

        self.search_button = ctk.CTkButton(
            self.search_frame,
            text="Buscar",
            command=self.search_movies
        )
        self.search_button.pack(side="left", padx=10)

        # Frame para mostrar estado de búsqueda
        self.status_label = ctk.CTkLabel(
            self.search_frame,
            text=""
        )
        self.status_label.pack(side="left", padx=10)

        # Frame izquierdo para la lista de películas
        self.left_frame = ctk.CTkFrame(self.main_frame)
        self.left_frame.pack(side="left", fill="y", padx=10)

        # Lista de películas
        self.movie_listbox = ctk.CTkScrollableFrame(
            self.left_frame,
            width=300,
            height=600
        )
        self.movie_listbox.pack(fill="both", expand=True)

        # Frame de paginación
        self.pagination_frame = ctk.CTkFrame(self.left_frame)
        self.pagination_frame.pack(fill="x", pady=10)

        self.prev_button = ctk.CTkButton(
            self.pagination_frame,
            text="Anterior",
            command=self.prev_page,
            width=70
        )
        self.prev_button.pack(side="left", padx=5)

        self.page_label = ctk.CTkLabel(
            self.pagination_frame,
            text="Página 1"
        )
        self.page_label.pack(side="left", padx=5)

        self.next_button = ctk.CTkButton(
            self.pagination_frame,
            text="Siguiente",
            command=self.next_page,
            width=70
        )
        self.next_button.pack(side="left", padx=5)

        # Frame derecho para los detalles de la película
        self.right_frame = ctk.CTkFrame(self.main_frame)
        self.right_frame.pack(side="left", fill="both", expand=True, padx=10)

    def search_movies(self):
        search_term = self.search_entry.get()
        if not search_term:
            self.status_label.configure(text="Por favor ingrese un término de búsqueda")
            return

        self.current_search = search_term
        self.current_page = 1
        self.load_movies()

    def load_movies(self):
        # Mostrar estado de carga
        self.status_label.configure(text="Buscando películas...")
        
        # Limpiar lista actual
        for widget in self.movie_listbox.winfo_children():
            widget.destroy()

        # Realizar búsqueda en OMDB
        params = {
            'apikey': self.api_key,
            's': self.current_search,
            'page': self.current_page,
            'type': 'movie'
        }
        
        try:
            response = requests.get(self.base_url, params=params)
            data = response.json()

            if data.get('Response') == 'True':
                self.search_results = data.get('Search', [])
                total_results = int(data.get('totalResults', 0))
                
                # Actualizar estado
                self.status_label.configure(
                    text=f"Encontradas {total_results} películas"
                )
                
                # Mostrar resultados
                for movie in self.search_results:
                    btn = ctk.CTkButton(
                        self.movie_listbox,
                        text=f"{movie['Title']} ({movie['Year']})",
                        command=lambda m=movie: self.show_movie_details(m['imdbID'])
                    )
                    btn.pack(pady=5, padx=10, fill="x")
                
                # Actualizar controles de paginación
                total_pages = (total_results + 9) // 10
                self.page_label.configure(text=f"Página {self.current_page} de {total_pages}")
                self.prev_button.configure(state="normal" if self.current_page > 1 else "disabled")
                self.next_button.configure(state="normal" if self.current_page < total_pages else "disabled")
            else:
                self.status_label.configure(text=f"Error: {data.get('Error', 'No se encontraron resultados')}")
        
        except Exception as e:
            self.status_label.configure(text=f"Error al buscar películas: {str(e)}")
   
    def show_movie_details(self, imdb_id):
    # Limpiar frame de detalles
        for widget in self.right_frame.winfo_children():
            widget.destroy()

        # Crear un frame scrollable para los detalles
        details_scroll = ctk.CTkScrollableFrame(
            self.right_frame,
            width=500,
            height=600
        )
        details_scroll.pack(fill="both", expand=True, padx=10, pady=10)

        # Para asegurar que el contenido use todo el ancho disponible
        details_scroll.grid_columnconfigure(0, weight=1)

        try:
            # Obtener detalles completos de la película
            params = {
                'apikey': self.api_key,
                'i': imdb_id,
                'plot': 'full'
            }
            response = requests.get(self.base_url, params=params)
            movie = response.json()

            if movie.get('Response') == 'True':
                # Título
                title_label = ctk.CTkLabel(
                    details_scroll,
                    text=movie['Title'],
                    font=("Arial", 24, "bold"),
                    bg_color='Navyblue',
                    width=200,
                    height=50
                )
                title_label.pack(pady=10)

                # Cargar póster si está disponible
                if movie.get('Poster') and movie['Poster'] != 'N/A':
                    try:
                        response = requests.get(movie['Poster'])
                        img = Image.open(BytesIO(response.content))
                        
                        # Redimensionar imagen manteniendo proporción
                        width, height = img.size
                        new_height = 450
                        new_width = int(width * (new_height / height))
                        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                        
                        # Convertir a CTkImage
                        ctk_image = ctk.CTkImage(
                            light_image=img,
                            dark_image=img,
                            size=(new_width, new_height)
                        )
                        
                        # Crear y mostrar el label con la imagen
                        poster_label = ctk.CTkLabel(
                            details_scroll,
                            image=ctk_image,
                            text=""
                        )
                        poster_label.pack(pady=10)
                    except Exception as e:
                        print(f"Error cargando imagen: {e}")

                # Frame para los detalles
                info_frame = ctk.CTkFrame(details_scroll)
                info_frame.pack(fill="x", padx=20, pady=10)

                # Detalles en formato de grid
                details = [
                    ("Año", movie.get('Year', 'N/A')),
                    ("Director", movie.get('Director', 'N/A')),
                    ("Género", movie.get('Genre', 'N/A')),
                    ("Duración", movie.get('Runtime', 'N/A')),
                    ("Calificación", movie.get('Rated', 'N/A')),
                    ("IMDb Rating", movie.get('imdbRating', 'N/A')),
                    ("País", movie.get('Country', 'N/A')),
                    ("Idioma", movie.get('Language', 'N/A')),
                    ("Premios", movie.get('Awards', 'N/A')),
                    ("Reparto", movie.get('Actors', 'N/A'))
                ]

                for i, (label, value) in enumerate(details):
                    # Frame para cada fila de detalles
                    row_frame = ctk.CTkFrame(info_frame)
                    row_frame.pack(fill="x", pady=2)
                    
                    # Label
                    ctk.CTkLabel(
                        row_frame,
                        text=f"{label}:",
                        font=("Arial", 12, "bold"),
                        width=100
                    ).pack(side="left", padx=5)
                    
                    # Valor
                    ctk.CTkLabel(
                        row_frame,
                        text=value,
                        wraplength=300,
                        justify="left"
                    ).pack(side="left", padx=5, fill="x", expand=True)

                # Sinopsis
                synopsis_frame = ctk.CTkFrame(details_scroll)
                synopsis_frame.pack(fill="x", padx=20, pady=10)

                ctk.CTkLabel(
                    synopsis_frame,
                    text="Sinopsis:",
                    font=("Arial", 12, "bold")
                ).pack(anchor="w", padx=5, pady=5)

                synopsis_text = ctk.CTkTextbox(
                    synopsis_frame,
                    height=150,
                    wrap="word"
                )
                synopsis_text.pack(fill="x", padx=5, pady=5)
                synopsis_text.insert("1.0", movie.get('Plot', 'N/A'))
                synopsis_text.configure(state="disabled")

                # Ratings de diferentes fuentes si están disponibles
                if movie.get('Ratings'):
                    ratings_frame = ctk.CTkFrame(details_scroll)
                    ratings_frame.pack(fill="x", padx=20, pady=10)

                    ctk.CTkLabel(
                        ratings_frame,
                        text="Calificaciones:",
                        font=("Arial", 12, "bold")
                    ).pack(anchor="w", padx=5, pady=5)

                    for rating in movie['Ratings']:
                        rating_text = f"{rating['Source']}: {rating['Value']}"
                        ctk.CTkLabel(
                            ratings_frame,
                            text=rating_text
                        ).pack(anchor="w", padx=5, pady=2)

                # Frame para calificación personal
                user_rating_frame = ctk.CTkFrame(details_scroll)
                user_rating_frame.pack(fill="x", padx=20, pady=10)

                ctk.CTkLabel(
                    user_rating_frame,
                    text="Tu Calificación:",
                    font=("Arial", 12, "bold")
                ).pack(anchor="w", padx=5, pady=5)

                # Obtener calificación guardada si existe
                saved_rating = self.watched_movies.get(imdb_id, {})
                
                # Slider para calificación
                rating_value = ctk.DoubleVar(value=saved_rating.get('rating', 5.0))
                rating_slider = ctk.CTkSlider(
                    user_rating_frame,
                    from_=0,
                    to=10,
                    number_of_steps=20,
                    variable=rating_value
                )
                rating_slider.pack(fill="x", padx=5, pady=5)

                # Label para mostrar valor actual
                rating_label = ctk.CTkLabel(
                    user_rating_frame,
                    text=f"Calificación: {rating_value.get()}/10"
                )
                rating_label.pack(pady=5)

                # Actualizar label cuando cambie el slider
                def update_rating_label(value):
                    rating_label.configure(text=f"Calificación: {float(value):.1f}/10")
                
                rating_slider.configure(command=update_rating_label)

                # Checkbox para marcar como vista
                watched_var = ctk.BooleanVar(value=imdb_id in self.watched_movies)
                watched_check = ctk.CTkCheckBox(
                    user_rating_frame,
                    text="Marcar como vista",
                    variable=watched_var,
                    command=lambda: self.toggle_watched(
                        imdb_id,
                        movie['Title'],
                        watched_var.get(),
                        rating_value.get()
                    )
                )
                watched_check.pack(pady=10)

                # Si hay una nota guardada, mostrarla
                if saved_rating.get('note'):
                    note_textbox.insert("1.0", saved_rating['note'])

                # Área para notas personales
                ctk.CTkLabel(
                    user_rating_frame,
                    text="Notas personales:",
                    font=("Arial", 12, "bold")
                ).pack(anchor="w", padx=5, pady=5)

                note_textbox = ctk.CTkTextbox(
                    user_rating_frame,
                    height=100,
                    wrap="word"
                )
                note_textbox.pack(fill="x", padx=5, pady=5)

                # Botón para guardar cambios
                save_button = ctk.CTkButton(
                    user_rating_frame,
                    text="Guardar cambios",
                    command=lambda: self.save_movie_rating(
                        imdb_id,
                        movie['Title'],
                        rating_value.get(),
                        note_textbox.get("1.0", "end-1c")
                    )
                )
                save_button.pack(pady=10)

                # Agregar frame para recomendaciones
                recommendations_frame = ctk.CTkFrame(details_scroll)
                recommendations_frame.pack(fill='x', padx=20, pady=10)

                # Titulo de recomendaciones
                ctk.CTkLabel(
                    recommendations_frame,
                    text='Recomendaciones Personalizadas',
                    font=('Arial', 14, 'bold')
                ).pack(anchor='w', padx=5, pady=5)

                # Inicializar recomendaciones con los datos actuales de la película y calificación
                self.update_recommendations(
                    recommendations_frame,
                    movie,
                    rating_value.get()
                )

        except Exception as e:
            error_label = ctk.CTkLabel(
                details_scroll,
                text=f"Error al cargar detalles: {str(e)}"
            )
            error_label.pack(pady=10)
            print("Error completo:", e)
            print("Tipo de error:", type(e))
            import traceback
            print("Traceback:", traceback.format_exc())

    def extract_movie_features(self, movie_data):
            """
            Extrae y normaliza las características relevantes de una película.
            """
            features = []
            
            # Características numéricas
            features.append(float(movie_data.get('imdbRating', '0').replace('N/A', '0')))
            features.append(float(movie_data.get('Metascore', '0').replace('N/A', '0')) / 100)
            
            # Año de la película (normalizado)
            year = movie_data.get('Year', '2000').replace('N/A', '2000')
            try:
                year = float(year)
            except ValueError:
                year = 2000
            features.append((year - 1900) / 200)  # Normalizar entre 0 y 1
            
            # Duración (normalizada)
            runtime = movie_data.get('Runtime', '0 min').replace('N/A', '0 min')
            runtime = float(runtime.split()[0] or 0) / 300  # Normalizar por 300 minutos
            features.append(runtime)
            
            # Géneros (one-hot encoding)
            all_genres = ['Action', 'Adventure', 'Animation', 'Biography', 'Comedy', 
                        'Crime', 'Documentary', 'Drama', 'Family', 'Fantasy', 
                        'Horror', 'Mystery', 'Romance', 'Sci-Fi', 'Thriller']
            movie_genres = movie_data.get('Genre', '').split(',')
            for genre in all_genres:
                features.append(1.0 if genre in movie_genres else 0.0)
            
            return features   

    def toggle_watched(self, imdb_id, title, is_watched, rating=5.0):
        if is_watched:
            if imdb_id not in self.watched_movies:
                self.watched_movies[imdb_id] = {
                    'title': title,
                    'rating': rating,
                    'watched_date': datetime.now().strftime("%Y-%m-%d"),
                    'note': ''
                }
        else:
            self.watched_movies.pop(imdb_id, None)
        self.save_user_data()

    def save_movie_rating(self, imdb_id, title, rating, note):
        self.watched_movies[imdb_id] = {
            'title': title,
            'rating': rating,
            'watched_date': datetime.now().strftime("%Y-%m-%d"),
            'note': note
        }
        self.save_user_data()
        
        # Mostrar confirmación
        confirmation = ctk.CTkToplevel(self)
        confirmation.transient(self)
        confirmation.geometry("300x100")
        confirmation.title("Confirmación")
        
        confirmation.grab_set()
        confirmation.focus_set()

        ctk.CTkLabel(
            confirmation,
            text="¡Cambios guardados correctamente!"
        ).pack(pady=20)
        
        ctk.CTkButton(
            confirmation,
            text="OK",
            command=confirmation.destroy
        ).pack()

    def show_watched_movies(self):
        # Crear ventana para mostrar películas vistas
        watched_window = ctk.CTkToplevel(self)
        watched_window.transient(self)
        watched_window.geometry("600x400")
        watched_window.title("Mis Películas Vistas")
        watched_window.geometry(f"+{self.winfo_x() + 50}+{self.winfo_y() + 50}")
        
        # Frame principal
        main_frame = ctk.CTkFrame(watched_window)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Frame scrollable para la lista
        scroll_frame = ctk.CTkScrollableFrame(main_frame)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Encabezado
        headers = ["Película", "Calificación", "Fecha vista"]
        for i, header in enumerate(headers):
            ctk.CTkLabel(
                scroll_frame,
                text=header,
                font=("Arial", 12, "bold")
            ).grid(row=0, column=i, padx=5, pady=5, sticky="w")

        # Mostrar películas
        for i, (imdb_id, data) in enumerate(self.watched_movies.items(), 1):
            ctk.CTkLabel(
                scroll_frame,
                text=data['title']
            ).grid(row=i, column=0, padx=5, pady=2, sticky="w")
            
            ctk.CTkLabel(
                scroll_frame,
                text=f"{data['rating']}/10"
            ).grid(row=i, column=1, padx=5, pady=2)
            
            ctk.CTkLabel(
                scroll_frame,
                text=data['watched_date']
            ).grid(row=i, column=2, padx=5, pady=2)

        # Frame para el botón
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", padx=10, pady=5)

        # Agregar botón de análisis
        analyze_button = ctk.CTkButton(
            button_frame,
            text="Ver Análisis",
            command=self.show_analytics
        )
        analyze_button.pack(pady=5)

    def get_movies_by_search(self, query):
        """
        Busca películas en la API de OMDB usando un término de búsqueda
        """
        movies_data = {}
        params = {
            'apikey': self.api_key,
            's': query,  # término de búsqueda
            'type': 'movie'
        }
        try:
            response = requests.get(self.base_url, params=params)
            search_results = response.json()
            
            if search_results.get('Response') == 'True':
                # Por cada resultado básico, obtener detalles completos
                for movie in search_results.get('Search', []):
                    movie_id = movie['imdbID']
                    # Obtener detalles completos de la película
                    detail_params = {
                        'apikey': self.api_key,
                        'i': movie_id,
                        'plot': 'full'
                    }
                    detail_response = requests.get(self.base_url, params=detail_params)
                    if detail_response.status_code == 200:
                        movie_details = detail_response.json()
                        if movie_details.get('Response') == 'True':
                            movies_data[movie_id] = movie_details
                    
        except Exception as e:
            print(f"Error en la búsqueda de películas: {e}")
        
        return movies_data

    def update_recommendations(self, recommendations_frame, movie_data, current_rating):
        # Limpiar el contenido existente del frame de recomendaciones
        for widget in recommendations_frame.winfo_children():
            widget.destroy()

        # Formatear los datos de la película
        formatted_movie = {
            'imdbID': movie_data['imdbID'],
            'Title': movie_data['Title'],
            'Genre': movie_data.get('Genre', ''),
            'Director': movie_data.get('Director', ''),
            'rating': current_rating
        }

        # Crear una copia temporal de las películas vistas con la calificación actual
        temp_data = self.watched_movies.copy()
        temp_data[movie_data['imdbID']] = {
            'title': movie_data['Title'],
            'rating': current_rating,
            'watched_date': datetime.now().strftime('%Y-%m-%d')
        }

        # Inicializar diccionario de todas las películas
        all_movies_data = {}
            
        # Añadir la película actual
        all_movies_data[movie_data['imdbID']] = movie_data
            
        # Obtener películas relacionadas basadas en diferentes criterios
        search_terms = [
            movie_data.get('Title', '').split()[0],  # Primera palabra del título
            movie_data.get('Genre', '').split(',')[0].strip(),  # Primer género
            movie_data.get('Director', '').split(',')[0].strip()  # Primer director
        ]
            
        # Buscar películas relacionadas
        for term in search_terms:
            if term and len(term) > 2:  # Evitar términos muy cortos
                related_movies = self.get_movies_by_search(term)
                all_movies_data.update(related_movies)
            
        # Añadir películas vistas que no estén ya incluidas
        for movie_id in self.watched_movies:
            if movie_id not in all_movies_data:
                params = {
                    'apikey': self.api_key,
                    'i': movie_id,
                    'plot': 'full'
                }
                try:
                    response = requests.get(self.base_url, params=params)
                    movie_info = response.json()
                    if movie_info.get('Response') == 'True':
                        all_movies_data[movie_id] = movie_info
                except Exception as e:
                    print(f"Error al obtener información de la película {movie_id}: {e}")

        # Crear diccionario de características
        movie_features = {}
        for movie_id, movie_info in all_movies_data.items():
            try:
                movie_features[movie_id] = self.extract_movie_features(movie_info)
            except Exception as e:
                print(f"Error extrayendo características de {movie_id}: {e}")

        # Preparar datos y obtener recomendaciones
        self.recommendation_manager.prepare_data(
            self.watched_movies,  # Usar watched_movies original
            all_movies_data  # Pasar todas las películas disponibles
        )
            
        recommendations = self.recommendation_manager.get_recommendations(
            self.watched_movies,  # Usar watched_movies original
            formatted_movie,
            movie_features
        )

        # Imprimir información de debug
        #print("Recomendaciones obtenidas:", recommendations)
       # print("Películas disponibles:", len(all_movies_data))
        #for system, recs in recommendations.items():
            #print(f"Sistema {system}: {len(recs)} recomendaciones")

        recommendation_text = self.recommendation_manager.format_recommendations(
            recommendations,
            all_movies_data  # Pasar el diccionario completo de películas
        )

        # Crear frame desplazable para las recomendaciones
        rec_scroll_frame = ctk.CTkScrollableFrame(
            recommendations_frame,
            height=200
        )
        rec_scroll_frame.pack(fill='x', padx=5, pady=5)

        # Agregar texto de recomendaciones al frame desplazable
        rec_label = ctk.CTkLabel(
            rec_scroll_frame,
            text=recommendation_text,
            wraplength=450,  # Ajusta este valor según tu interfaz
            justify="left"
        )
        rec_label.pack(fill='x', padx=5, pady=5)

        # Agregar botón de actualizar debajo del frame desplazable
        update_rec_button = ctk.CTkButton(
            recommendations_frame,
            text='Actualizar Recomendaciones',
            command=lambda: self.update_recommendations(
                recommendations_frame,
                movie_data,
                current_rating
            )
        )
        update_rec_button.pack(pady=10)
    
    def show_analytics(self):
        # Convertir datos a DataFrame
        movies_list = []
        for imdb_id, movie_data in self.watched_movies.items():
            movie_dict = {
                'imdb_id': imdb_id,
                'title': movie_data['title'],
                'rating': float(movie_data['rating']),
                'watched_date': pd.to_datetime(movie_data['watched_date']),
                'note': movie_data.get('note', '')
            }
            movies_list.append(movie_dict)
        
        df = pd.DataFrame(movies_list)
        
        # Crear ventana de análisis
        analytics_window = ctk.CTkToplevel(self)
        analytics_window.transient(self)
        analytics_window.geometry("1000x800")
        analytics_window.title("Análisis de Películas")
        analytics_window.geometry(f"+{self.winfo_x() + 50}+{self.winfo_y() + 50}")

        # Crear scrollable frame principal
        scrollable_frame = ctk.CTkScrollableFrame(analytics_window)
        scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Frame principal que contendrá todo
        main_frame = ctk.CTkFrame(scrollable_frame)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Configurar el estilo del Notebook
        style = ttk.Style()
        style.configure('Custom.TNotebook', background='#2b2b2b')
        style.configure('Custom.TNotebook.Tab', padding=[10, 2], background='#3b3b3b', foreground='black')
        
        # Crear notebook para pestañas con el estilo personalizado
        notebook = ttk.Notebook(main_frame, style='Custom.TNotebook')
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Pestaña de Estadísticas Básicas
        stats_frame = ctk.CTkFrame(notebook)
        notebook.add(stats_frame, text="Estadísticas")

        # Calcular estadísticas básicas
        stats = {
            'Total de películas': len(df),
            'Calificación promedio': f"{df['rating'].mean():.2f}/10",
            'Calificación más alta': f"{df['rating'].max():.2f}/10",
            'Calificación más baja': f"{df['rating'].min():.2f}/10",
            'Película mejor calificada': df.loc[df['rating'].idxmax(), 'title'],
            'Película peor calificada': df.loc[df['rating'].idxmin(), 'title']
        }

        # Mostrar estadísticas
        for i, (stat, value) in enumerate(stats.items()):
            ctk.CTkLabel(
                stats_frame,
                text=f"{stat}:",
                font=("Arial", 12, "bold")
            ).pack(anchor="w", padx=20, pady=5)
            
            ctk.CTkLabel(
                stats_frame,
                text=str(value)
            ).pack(anchor="w", padx=40, pady=2)

        # Pestaña de Gráficos
        graphs_frame = ctk.CTkFrame(notebook)
        notebook.add(graphs_frame, text="Gráficos")

        # Frame para los gráficos
        plot_frame = ctk.CTkFrame(graphs_frame)
        plot_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Configurar el estilo de los gráficos para modo oscuro
        plt.style.use('dark_background')
        
        # Crear figura para los gráficos
        fig = plt.Figure(figsize=(12, 8), dpi=100)
        fig.patch.set_facecolor('#2b2b2b')
        
        # Distribución de calificaciones
        ax1 = fig.add_subplot(221)
        sns.histplot(data=df, x='rating', bins=10, ax=ax1, color='skyblue')
        ax1.set_title('Distribución de Calificaciones')
        ax1.set_facecolor('#2b2b2b')
        
        # Películas por mes
        ax2 = fig.add_subplot(222)
        df['month'] = df['watched_date'].dt.strftime('%Y-%m')
        monthly_counts = df['month'].value_counts().sort_index()
        monthly_counts.plot(kind='bar', ax=ax2, color='skyblue')
        ax2.set_title('Películas por Mes')
        ax2.tick_params(axis='x', rotation=45)
        ax2.set_facecolor('#2b2b2b')
        
        # Tendencia de calificaciones
        ax3 = fig.add_subplot(223)
        df_sorted = df.sort_values('watched_date')
        ax3.plot(df_sorted['watched_date'], df_sorted['rating'], 
                marker='o', color='skyblue', linestyle='-', 
                linewidth=2, markersize=8)
        ax3.set_title('Tendencia de Calificaciones')
        ax3.tick_params(axis='x', rotation=45)
        ax3.set_facecolor('#2b2b2b')
        ax3.grid(True, linestyle='--', alpha=0.3)
        ax3.set_ylim(0, 10)
        
        # Calificaciones por día de la semana
        ax4 = fig.add_subplot(224)
        df['weekday'] = df['watched_date'].dt.day_name()
        weekday_avg = df.groupby('weekday')['rating'].mean()
        
        # Ordenar los días de la semana
        dias_semana = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        weekday_avg = weekday_avg.reindex(dias_semana)
        
        weekday_avg.plot(kind='bar', ax=ax4, color='skyblue')
        ax4.set_title('Calificación Promedio por Día')
        ax4.tick_params(axis='x', rotation=45)
        ax4.set_facecolor('#2b2b2b')
        ax4.set_ylim(0, 10)

        # Ajustar layout
        fig.tight_layout(pad=2.0)
        
        # Crear canvas y agregar al frame de gráficos
        canvas = FigureCanvasTkAgg(fig, master=plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        # Frame para el botón de exportar
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", pady=10)

        # Botón para exportar datos
        export_button = ctk.CTkButton(
            button_frame,
            text="Exportar a Excel",
            command=lambda: self.export_to_excel(df)
        )
        export_button.pack(pady=5)

    def export_to_excel(self, df):
                try:
                    filename = f"analisis_peliculas_{self.username}.xlsx"
                    
                    with pd.ExcelWriter(filename) as writer:
                        # Películas
                        df.to_excel(writer, sheet_name='Películas', index=False)
                        
                        # Estadísticas por mes
                        monthly_stats = df.groupby(df['watched_date'].dt.strftime('%Y-%m')).agg({
                            'title': 'count',
                            'rating': ['mean', 'min', 'max']
                        }).round(2)
                        monthly_stats.to_excel(writer, sheet_name='Estadísticas por Mes')
                        
                        # Estadísticas por día de la semana
                        weekly_stats = df.groupby(df['watched_date'].dt.day_name()).agg({
                            'title': 'count',
                            'rating': ['mean', 'min', 'max']
                        }).round(2)
                        weekly_stats.to_excel(writer, sheet_name='Estadísticas por Día')
                    
                    # Mostrar confirmación
                    confirmation = ctk.CTkToplevel(self)
                    confirmation.transient(self)
                    confirmation.geometry("300x100")
                    confirmation.title("Exportación Exitosa")
                    
                    ctk.CTkLabel(
                        confirmation,
                        text=f"Datos exportados a {filename}"
                    ).pack(pady=20)
                    
                    ctk.CTkButton(
                        confirmation,
                        text="OK",
                        command=confirmation.destroy
                    ).pack()
                    
                except Exception as e:
                    # Mostrar error
                    error_window = ctk.CTkToplevel(self)
                    error_window.transient(self)
                    error_window.geometry("300x100")
                    error_window.title("Error")
                    
                    ctk.CTkLabel(
                        error_window,
                        text=f"Error al exportar: {str(e)}"
                    ).pack(pady=20)
                    
                    ctk.CTkButton(
                        error_window,
                        text="OK",
                        command=error_window.destroy
                    ).pack()

    def next_page(self):
        self.current_page += 1
        self.load_movies()

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.load_movies()

    def load_user_data(self):
        try:
            file_path = os.path.join(RUTA_BASE,'data', f'user_data_{self.username}.json')

            with open(file_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_user_data(self):
        file_path = os.path.join(RUTA_BASE,'data', f'user_data_{self.username}.json')

        #Asegurar que la carpeta destino exista
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "w") as f:
            json.dump(self.watched_movies, f)

    def logout(self):
        self.save_user_data()
        self.quit()
