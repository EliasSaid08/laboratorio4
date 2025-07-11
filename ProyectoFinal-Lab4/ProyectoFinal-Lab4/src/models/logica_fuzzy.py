import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

class FuzzyRecommender:
    def __init__(self):
        # Universos de discurso
        self.rating_range = np.arange(0, 11, 1)
        self.similarity_range = np.arange(0, 101, 1)
        self.recommendation_range = np.arange(0, 101, 1)

        # Variables difusas
        self.user_rating = ctrl.Antecedent(self.rating_range, 'user_rating')
        self.content_similarity = ctrl.Antecedent(self.similarity_range, 'content_similarity')
        self.recommendation_score = ctrl.Consequent(self.recommendation_range, 'recommendation_score')

        # Conjuntos difusos para calificación
        self.user_rating['low'] = fuzz.trimf(self.rating_range, [0, 0, 5])
        self.user_rating['medium'] = fuzz.trimf(self.rating_range, [3, 5, 7])
        self.user_rating['high'] = fuzz.trimf(self.rating_range, [5, 10, 10])

        # Conjuntos difusos para similitud
        self.content_similarity['low'] = fuzz.trimf(self.similarity_range, [0, 0, 50])
        self.content_similarity['medium'] = fuzz.trimf(self.similarity_range, [30, 50, 70])
        self.content_similarity['high'] = fuzz.trimf(self.similarity_range, [50, 100, 100])

        # Conjuntos difusos para recomendación
        self.recommendation_score['low'] = fuzz.trimf(self.recommendation_range, [0, 0, 50])
        self.recommendation_score['medium'] = fuzz.trimf(self.recommendation_range, [30, 50, 70])
        self.recommendation_score['high'] = fuzz.trimf(self.recommendation_range, [50, 100, 100])

        # Reglas difusas
        self.rules = [
            ctrl.Rule(self.user_rating['high'] & self.content_similarity['high'], 
                     self.recommendation_score['high']),
            ctrl.Rule(self.user_rating['high'] & self.content_similarity['medium'], 
                     self.recommendation_score['medium']),
            ctrl.Rule(self.user_rating['medium'] & self.content_similarity['high'], 
                     self.recommendation_score['medium']),
            ctrl.Rule(self.user_rating['low'] | self.content_similarity['low'], 
                     self.recommendation_score['low'])
        ]

        # Sistema de control
        self.recommendation_ctrl = ctrl.ControlSystem(self.rules)
        self.recommendation_sim = ctrl.ControlSystemSimulation(self.recommendation_ctrl)

    def get_recommendation_score(self, user_rating, content_similarity):
        self.recommendation_sim.input['user_rating'] = user_rating
        self.recommendation_sim.input['content_similarity'] = content_similarity
        
        try:
            self.recommendation_sim.compute()
            return self.recommendation_sim.output['recommendation_score']
        except:
            return 0