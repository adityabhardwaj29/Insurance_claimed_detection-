from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def text_similarity(text_a, text_b):
    matrix=TfidfVectorizer().fit_transform([str(text_a), str(text_b)])
    return float(cosine_similarity(matrix[0:1], matrix[1:2])[0,0])
