import pickle
import numpy as np
import torch
import torchvision.transforms as T
from torchvision import models
from PIL import Image

from config import EMBEDDINGS_PATH

# Load model once globally (optional)
model = models.resnet50(pretrained=True)
model.eval()
model.fc = torch.nn.Identity()

# Define the same transform used in building embeddings
transform = T.Compose([
    T.Resize((224, 224)),
    T.ToTensor(),
    T.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

# Load precomputed embeddings from file
with open(EMBEDDINGS_PATH, "rb") as f:
    PRODUCT_EMBEDDINGS = pickle.load(f)

def get_image_embedding(image_path_or_bytes):
    """
    Given an image file path or raw bytes, return its embedding using the pre-trained model.
    """
    if isinstance(image_path_or_bytes, str):
        # It's a file path
        image = Image.open(image_path_or_bytes).convert("RGB")
    else:
        # It's raw image bytes from Telegram
        image = Image.open(image_path_or_bytes).convert("RGB")

    tensor = transform(image).unsqueeze(0)
    with torch.no_grad():
        embedding = model(tensor).squeeze().numpy()
    return embedding

def find_closest_product(user_embedding, top_k=1):
    """
    Find the closest product(s) in the embedding space using cosine similarity.
    Returns a list of product metadata sorted by similarity.
    """
    results = []
    
    # Cosine similarity: A dot B / (|A|*|B|)
    # We can compute norms once
    user_norm = np.linalg.norm(user_embedding)
    
    for item in PRODUCT_EMBEDDINGS:
        product_vector = item["embedding"]
        product_norm = np.linalg.norm(product_vector)
        similarity = np.dot(user_embedding, product_vector) / (user_norm * product_norm)
        
        results.append({
            "id": item["id"],
            "name": item["name"],
            "price": item["price"],
            "url": item["url"],
            "similarity": similarity
        })
    
    # Sort descending by similarity
    results.sort(key=lambda x: x["similarity"], reverse=True)
    
    # Return top_k results
    return results[:top_k]