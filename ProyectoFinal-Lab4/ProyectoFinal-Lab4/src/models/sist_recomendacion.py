from .logica_fuzzy import FuzzyRecommender
from .sist_experto import ExpertRecommender
from .ma_learning import MLRecommender
from .red_neuronal import NeuralRecommender
import numpy as np
from datetime import datetime
import pandas as pd

class RecommendationManager:
    def __init__(self):
        self.fuzzy_recommender = FuzzyRecommender()
        self.expert_recommender = ExpertRecommender()
        self.ml_recommender = MLRecommender()
        self.neural_recommender = None  # Se inicializará cuando se conozca el tamaño de características
        
    def prepare_data(self, watched_movies, movie_data):
        # Preparar datos para ML
        self.ml_recommender.prepare_data(movie_data)

        # Preparar datos para sistema experto
        for movie_id, movie_info in watched_movies.items():
            full_movie_info = movie_data.get(movie_id, {})
            
            # Extraer rating
            rating = float(movie_info.get('rating', 0) if isinstance(movie_info, dict) else movie_info)
            
            # Obtener géneros y limpiarlos
            genres = [g.strip() for g in full_movie_info.get('Genre', '').split(',') if g.strip()]
            director = full_movie_info.get('Director', '').strip()
            
            # Añadir datos al sistema experto
            try:
                # Añadir información de la película
                self.expert_recommender.add_movie_fact(
                    movie_id,
                    full_movie_info.get('Title', ''),
                    director,
                    genres
                )
                
                # Añadir preferencia del usuario
                if rating > 0:
                    self.expert_recommender.add_user_preference(movie_id, movie_id, rating)
                    
                    # Añadir preferencias de género explícitamente
                    for genre in genres:
                        self.expert_recommender.prolog.assertz(
                            f"user_likes_genre('{movie_id}', '{genre.lower()}')"
                        )
            except Exception as e:
                print(f"Error al procesar película {movie_id} para sistema experto: {e}")

        # Añadir todas las películas disponibles al sistema experto
        for movie_id, data in movie_data.items():
            if movie_id not in watched_movies:
                try:
                    genres = [g.strip() for g in data.get('Genre', '').split(',') if g.strip()]
                    director = data.get('Director', '').strip()
                    self.expert_recommender.add_movie_fact(
                        movie_id,
                        data.get('Title', ''),
                        director,
                        genres
                    )
                except Exception as e:
                    print(f"Error al añadir película {movie_id} al sistema experto: {e}")

        # Inicializar red neuronal si es necesario
        if self.neural_recommender is None:
            feature_size = 19
            self.neural_recommender = NeuralRecommender(feature_size)
    
    def get_recommendations(self, watched_movies, target_movie, movie_features):
        recommendations = {
            'fuzzy': [],
            'sist experto': [],
            'machine learning': [],
            'red neural': []
      }
        
        try:
            # Debug prints
            #print("Procesando recomendaciones...")
            
            # Fuzzy
            #print("Obteniendo recomendaciones fuzzy...")
            fuzzy_recs = []
            for movie_id, movie_info in watched_movies.items():
                rating = (movie_info.get('rating') if isinstance(movie_info, dict) 
                        else movie_info)
                similarity = self.calculate_similarity(target_movie, movie_info)
                score = self.fuzzy_recommender.get_recommendation_score(
                    float(rating),
                    similarity
                )
                fuzzy_recs.append({
                    'movie_id': movie_id,
                    'score': score
                })
            recommendations['fuzzy'] = fuzzy_recs
            
            # Expert System
            #print("Obteniendo recomendaciones del sistema experto...")
            expert_recs = self.expert_recommender.get_recommendations(target_movie['imdbID'])
            recommendations['sist experto'] = expert_recs
            #print(f"Recomendaciones expert: {expert_recs}")
            
            # Machine Learning
            #print("Obteniendo recomendaciones ML...")
            ml_recs = self.ml_recommender.get_recommendations(watched_movies)
            recommendations['machine learning'] = ml_recs
            #print(f"Recomendaciones ML: {ml_recs}")
            
            # Neural Network
            if self.neural_recommender is not None and movie_features:
                #print("Obteniendo recomendaciones neurales...")
                neural_recs = self.neural_recommender.get_recommendations(movie_features)
                recommendations['red neural'] = neural_recs
                #print(f"Recomendaciones neural: {neural_recs}")
                
        except Exception as e:
            print(f"Error en get_recommendations: {str(e)}")
            import traceback
            print(traceback.format_exc())
            
        return recommendations

    def calculate_similarity(self, movie1, movie2):
        return np.random.uniform(0, 100)
    
    def format_recommendations(self, recommendations, movie_data):
        """Formatea las recomendaciones para mostrarlas en la interfaz"""
        text = "Recomendaciones basadas en diferentes sistemas:\n\n"
    
        for system, recs in recommendations.items():
            if recs:  # Si hay recomendaciones para este sistema
                text += f"\n{system.upper()}:\n"
                
                # Ordenar recomendaciones por score
                sorted_recs = sorted(recs, key=lambda x: float(x.get('score', 0)), reverse=True)
                
                # Mostrar top 5 recomendaciones
                for rec in sorted_recs[:5]:
                    movie_id = rec.get('movie_id')
                    score = float(rec.get('score', 0))
                    
                    # Obtener información de la película
                    movie_info = movie_data.get(movie_id, {})
                    title = movie_info.get('Title', f'ID: {movie_id}')
                    
                    text += f"- {title} (Score: {score:.2f})\n"
        
        return text