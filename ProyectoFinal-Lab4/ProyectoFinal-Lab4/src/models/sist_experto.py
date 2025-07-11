from pyswip import Prolog
from config import DATA_PATH_REGLAS

class ExpertRecommender:
    def __init__(self):
        self.prolog = Prolog()
        self.initialize_knowledge_base()

    def initialize_knowledge_base(self):
         file_path = DATA_PATH_REGLAS.replace("\\", "/")
         self.prolog.consult(file_path)

    def add_movie_fact(self, movie_id, title, director, genres):
        try:
            # Limpiar y normalizar los datos
            movie_id = str(movie_id)
            title = title.replace("'", "''")
            director = director.replace("'", "''")
            
            # Verificar si la película ya existe
            existing = list(self.prolog.query(f"movie('{movie_id}', _)"))
            if existing:
                print(f"Película {movie_id} ya existe en la base de conocimiento")
                return
            
            # Añadir hechos básicos de la película
            self.prolog.assertz(f"movie('{movie_id}', '{title}')")
            
            if director:
                self.prolog.assertz(f"movie_director('{movie_id}', '{director}')")
            
            # Añadir géneros
            for genre in genres:
                genre = genre.strip().lower()
                if genre:
                    self.prolog.assertz(f"movie_has_genre('{movie_id}', '{genre}')")
                    
            print(f"Añadidos hechos para película {title} ({movie_id})")
            
        except Exception as e:
            print(f"Error al añadir hechos para película {movie_id}: {e}")

    def add_user_preference(self, user_id, movie_id, rating):
       try:
            # Limpiar y normalizar los datos
            user_id = str(user_id)
            movie_id = str(movie_id)
            rating = float(rating)
            
            # Verificar si la preferencia ya existe
            existing = list(self.prolog.query(f"user_rating('{user_id}', '{movie_id}', _)"))
            if existing:
                print(f"Preferencia para {movie_id} ya existe")
                return
            
            # Añadir rating del usuario
            self.prolog.assertz(f"user_rating('{user_id}', '{movie_id}', {rating})")
            
            # Obtener y añadir preferencias de género
            genres = list(self.prolog.query(f"movie_has_genre('{movie_id}', Genre)"))
            
            for soln in genres:
                genre = str(soln['Genre'])
                self.prolog.assertz(f"user_likes_genre('{user_id}', '{genre}')")
                
            print(f"Añadida preferencia de usuario {user_id} para película {movie_id} con {len(genres)} géneros")
            
       except Exception as e:
            print(f"Error al añadir preferencia de usuario: {e}")
       finally:
            # Asegurar que la consulta se cierre
            self.prolog.query("true")

    def get_recommendations(self, user_id, max_recommendations=5):
        # Consultar recomendaciones
        recommendations = []
        seen_movies = set()
        
        try:
            print(f"Buscando recomendaciones para usuario {user_id}")
            
            # Verificar que existen datos en la base de conocimiento
            genres_query = list(self.prolog.query("movie_has_genre(_, Genre)"))
            print(f"Géneros encontrados: {len(genres_query)}")
            
            ratings_query = list(self.prolog.query("user_rating(_, _, _)"))
            print(f"Ratings encontrados: {len(ratings_query)}")
            
            # Obtener recomendaciones
            query = f"recommend(Movie, '{user_id}', Score)"
            print(f"Ejecutando consulta: {query}")
            
            results = list(self.prolog.query(query))
            print(f"Resultados encontrados: {len(results)}")
            
            for soln in results:
                movie_id = str(soln['Movie'])
                if movie_id not in seen_movies:
                    seen_movies.add(movie_id)
                    recommendations.append({
                        'movie_id': movie_id,
                        'score': float(soln['Score'])
                    })
                    
                    if len(recommendations) >= max_recommendations:
                        break
                        
        except Exception as e:
            print(f"Error al obtener recomendaciones: {e}")
            import traceback
            print(traceback.format_exc())
        finally:
            # Asegurar que la consulta se cierre
            self.prolog.query("true")
        
        print(f"Recomendaciones finales: {len(recommendations)}")
        return recommendations