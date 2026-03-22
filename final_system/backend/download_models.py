import gdown
import os

MODELS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
os.makedirs(MODELS_DIR, exist_ok=True)

MODELS = {
    "best_model_v2.pth"     : "1NNxMlELmMKUS0luyJCSYD8X9wAqp6GOC",
    "best_lie_model_v2.pth" : "1Q6YKjKA0Ixs5StFBymNxGix1guX6axP7"
}

def download_models():
    for filename, file_id in MODELS.items():
        path = os.path.join(MODELS_DIR, filename)
        if os.path.exists(path):
            print(f"✅ {filename} already exists — skipping")
        else:
            print(f"⬇️  Downloading {filename}...")
            url = f"https://drive.google.com/uc?id={file_id}"
            gdown.download(url, path, quiet=False)
            print(f"✅ {filename} downloaded!")

if __name__ == "__main__":
    download_models()