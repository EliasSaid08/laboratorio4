from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import numpy as np

class MLRecommender:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.movie_features = None
        self.movie_ids = None
        
    def prepare_data(self, movies_data):
        # Preparar características de las películas
        movie_texts = []
        self.movie_ids = []
    
        for movie_id, movie_data in movies_data.items():
            # Los nombres de las claves no coinciden con la API de OMDB
            movie_text = f"{movie_data.get('Title', '')} {movie_data.get('Genre', '')} {movie_data.get('Director', '')} {movie_data.get('Actors', '')}"  # Cambiar a mayúsculas
            movie_texts.append(movie_text)
            self.movie_ids.append(movie_id)
            
        # Crear matriz TF-IDF
        self.movie_features = self.vectorizer.fit_transform(movie_texts)
        
    def get_recommendations(self, user_ratings, n_recommendations=5):
         # Calcular similitud de contenido
        sim_scores = cosine_similarity(self.movie_features)
        
        # Calcular predicciones para películas no vistas
        predictions = {}
        for i, movie_id in enumerate(self.movie_ids):
            if movie_id not in user_ratings:
                weighted_sum = 0
                similarity_sum = 0
                
                for j, rated_movie in enumerate(self.movie_ids):
                    if rated_movie in user_ratings:
                        sim = sim_scores[i][j]
                        # Extraer el rating del diccionario
                        rating = float(user_ratings[rated_movie].get('rating', 0) 
                                    if isinstance(user_ratings[rated_movie], dict) 
                                    else user_ratings[rated_movie])
                        weighted_sum += sim * rating
                        similarity_sum += sim
                
                if similarity_sum > 0:
                    predictions[movie_id] = weighted_sum / similarity_sum
                    
        # Ordenar predicciones
        sorted_predictions = sorted(predictions.items(), key=lambda x: x[1], reverse=True)
    
        # Convertir al formato estándar de recomendaciones
        formatted_recommendations = [
            {'movie_id': movie_id, 'score': float(score)} 
            for movie_id, score in sorted_predictions[:n_recommendations]
        ]
        
        return formatted_recommendations