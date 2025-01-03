import os
import pickle
import requests
import pandas as pd
from PIL import Image
from io import BytesIO
import torch
import torchvision.transforms as T
from torchvision import models
from tqdm import tqdm

from config import PRODUCT_DATA_CSV, PRODUCT_IMAGES_DIR, EMBEDDINGS_PATH

def download_images_if_needed(csv_path=PRODUCT_DATA_CSV, output_dir=PRODUCT_IMAGES_DIR):
    """
    Download product images from URLs in CSV if not already downloaded.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    df = pd.read_csv(csv_path)
    for _, row in tqdm(df.iterrows(), total=len(df), desc="Downloading images"):
        img_url = row["img_url"]
        product_id = row["id"]
        file_ext = img_url.split('.')[-1].lower()
        local_path = os.path.join(output_dir, f"{product_id}.{file_ext}")
        
        if not os.path.exists(local_path):
            try:
                response = requests.get(img_url, timeout=10)
                response.raise_for_status()
                with open(local_path, 'wb') as f:
                    f.write(response.content)
            except Exception as e:
                print(f"Error downloading {img_url} - {e}")


def build_embeddings(csv_path=PRODUCT_DATA_CSV,
                     images_dir=PRODUCT_IMAGES_DIR,
                     output_path=EMBEDDINGS_PATH):
    """
    Build embeddings for each product image using a pre-trained model.
    Save the embeddings along with product metadata into a pickle file.
    """
    df = pd.read_csv(csv_path)
    
    # Use a pre-trained model (ResNet50 as example)
    model = models.resnet50(pretrained=True)
    model.eval()  # set model to inference mode

    # Remove the final classification layer so we can extract features
    # (Alternatively, just apply global pooling on the penultimate layer)
    model.fc = torch.nn.Identity()

    # Define a transform to match what the model expects
    transform = T.Compose([
        T.Resize((224, 224)),
        T.ToTensor(),
        T.Normalize(
            mean=[0.485, 0.456, 0.406], 
            std=[0.229, 0.224, 0.225]
        )
    ])

    product_embeddings = []

    for _, row in tqdm(df.iterrows(), total=len(df), desc="Creating embeddings"):
        product_id = row["id"]
        name = row["name"]
        price = row["price"]
        url = row["url"]
        
        # Attempt to load the local image
        # The CSV might have different file extensions, so let's find it
        # by searching the images directory
        possible_exts = ["jpg", "jpeg", "png", "gif"]
        local_image_path = None
        for ext in possible_exts:
            candidate_path = os.path.join(images_dir, f"{product_id}.{ext}")
            if os.path.exists(candidate_path):
                local_image_path = candidate_path
                break
        
        if not local_image_path:
            print(f"Warning: No local image found for product ID: {product_id}")
            continue
        
        # Load image
        image = Image.open(local_image_path).convert("RGB")
        image_tensor = transform(image).unsqueeze(0)  # shape: (1, 3, 224, 224)
        
        # Generate embedding
        with torch.no_grad():
            embedding = model(image_tensor).squeeze().numpy()  # shape: (2048,)
        
        product_embeddings.append({
            "id": product_id,
            "name": name,
            "price": price,
            "url": url,
            "embedding": embedding
        })
    
    # Save embeddings
    with open(output_path, "wb") as f:
        pickle.dump(product_embeddings, f)

    print(f"Embeddings saved to {output_path}")