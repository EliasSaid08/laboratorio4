import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np

class MovieDataset(Dataset):
    def __init__(self, user_ratings, movie_features):
        self.user_ratings = user_ratings
        self.movie_features = movie_features
        self.movie_ids = list(user_ratings.keys())
        
    def __len__(self):
        return len(self.user_ratings)
    
    def __getitem__(self, idx):
        movie_id = self.movie_ids[idx]
        features = self.movie_features[movie_id]
        rating = self.user_ratings[movie_id]
        return torch.FloatTensor(features), torch.FloatTensor([rating])

class MovieRecommenderNN(nn.Module):
    def __init__(self, input_size):
        super(MovieRecommenderNN, self).__init__()
        self.layers = nn.Sequential(
            nn.Linear(input_size, 128),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
        
    def forward(self, x):
        return self.layers(x) * 10  # Escalar salida a rango 0-10

class NeuralRecommender:
    def __init__(self, feature_size):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        input_size = 19
        self.model = MovieRecommenderNN(input_size).to(self.device)
        self.optimizer = optim.Adam(self.model.parameters())
        self.criterion = nn.MSELoss()
        
    def train(self, train_loader, epochs=10):
        self.model.train()
        for epoch in range(epochs):
            total_loss = 0
            for features, ratings in train_loader:
                features = features.to(self.device)
                ratings = ratings.to(self.device)
                
                self.optimizer.zero_grad()
                predictions = self.model(features)
                loss = self.criterion(predictions, ratings)
                loss.backward()
                self.optimizer.step()
                
                total_loss += loss.item()
                
            avg_loss = total_loss / len(train_loader)
            print(f"Epoch {epoch+1}/{epochs}, Loss: {avg_loss:.4f}")
            
    def predict(self, features):
        self.model.eval()
        with torch.no_grad():
            features = torch.FloatTensor(features).to(self.device)
            predictions = self.model(features)
            return predictions.cpu().numpy()
        
    def get_recommendations(self, movie_features, n_recommendations=5):
            """
            Obtiene recomendaciones usando la red neuronal
            
            Args:
                movie_features: Diccionario con movie_id como clave y features como valor
                n_recommendations: Número de recomendaciones a devolver
            """
            recommendations = []
            self.model.eval()
            
            with torch.no_grad():
                for movie_id, features in movie_features.items():
                    features_tensor = torch.FloatTensor([features]).to(self.device)
                    prediction = self.model(features_tensor)
                    score = float(prediction.cpu().numpy()[0][0])
                    
                    recommendations.append({
                        'movie_id': movie_id,
                        'score': score
                    })
            
            # Ordenar por score y devolver las top n recomendaciones
            sorted_recommendations = sorted(recommendations, 
                                        key=lambda x: x['score'], 
                                        reverse=True)
            return sorted_recommendations[:n_recommendations]