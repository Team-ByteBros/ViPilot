import json
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from model_utils import ModelManager

# Get shared model instance
model = ModelManager().get_model()

with open("roles.json") as f:
    roles = json.load(f)

# Compute embeddings if model is available
if model:
    role_embeddings = model.encode([r["skills"] for r in roles])
else:
    role_embeddings = []


def recommend_roles(resume_text, top_k=3):
    resume_embedding = model.encode([resume_text])
    scores = cosine_similarity(resume_embedding, role_embeddings)[0]

    ranked = sorted(
        zip(roles, scores),
        key=lambda x: x[1],
        reverse=True
    )

    return [
        {"role": r["role"], "score": round(float(score), 2)}
        for r, score in ranked[:top_k]
    ]
