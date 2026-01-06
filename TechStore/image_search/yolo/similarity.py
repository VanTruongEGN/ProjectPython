from sklearn.metrics.pairwise import cosine_similarity

def calc_similarity(f1, f2):
    return cosine_similarity([f1], [f2])[0][0]