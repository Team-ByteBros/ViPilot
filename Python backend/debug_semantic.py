from sentence_transformers import SentenceTransformer, util
import torch

model = SentenceTransformer('all-MiniLM-L6-v2')
jd_skill = "kubernetes"
sentence = "Deployed microservices on Kubernetes using Helm charts."

jd_emb = model.encode(jd_skill, convert_to_tensor=True)
sent_emb = model.encode(sentence, convert_to_tensor=True)

score = util.cos_sim(jd_emb, sent_emb)[0]
print(f"Similarity: {score.item()}")
