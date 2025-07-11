% Declarar predicados dinámicos
:- dynamic movie/2.
:- dynamic movie_director/2.
:- dynamic movie_has_genre/2.
:- dynamic user_rating/3.
:- dynamic user_likes_genre/2.

% Declarar que similar_genre y recommend pueden estar en cualquier parte del archivo
:- discontiguous similar_genre/2, recommend/3.

% Reglas para géneros similares
similar_genre(action, adventure).
similar_genre(drama, romance).
similar_genre(horror, thriller).
similar_genre(comedy, family).
similar_genre(documentary, biography).

% Hacer las relaciones bidireccionales
similar_genre(X, Y) :- similar_genre(Y, X).

% Regla básica de recomendación por género
recommend(Movie, User, Score) :-
    movie_has_genre(Movie, Genre),
    user_likes_genre(User, Genre),
    Score is 8.5.

% Regla de recomendación por director
recommend(Movie, User, Score) :-
    movie_director(Movie, Director),
    user_rating(User, OtherMovie, Rating),
    movie_director(OtherMovie, Director),
    Rating >= 6,
    Score is Rating * 1.2.