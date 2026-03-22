import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image
import cv2
import numpy as np
import os

class DeepfakeDetector:
    def __init__(self, model_path):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model  = self._build_model().to(self.device)
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model.eval()
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406],
                                 [0.229, 0.224, 0.225])
        ])
        print("✅ Deepfake model loaded!")

    def _build_model(self):
        model = models.efficientnet_b0(weights=None)
        for param in model.parameters():
            param.requires_grad = False
        model.classifier = nn.Sequential(
            nn.Dropout(p=0.4),
            nn.Linear(1280, 512),
            nn.ReLU(),
            nn.BatchNorm1d(512),
            nn.Dropout(p=0.3),
            nn.Linear(512, 128),
            nn.ReLU(),
            nn.Linear(128, 2)
        )
        return model

    def extract_frames(self, video_path, num_frames=10):
        cap          = cv2.VideoCapture(video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if total_frames == 0:
            cap.release()
            return []
        indices   = [int(i * total_frames / num_frames) for i in range(num_frames)]
        frames    = []
        frame_idx = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            if frame_idx in indices:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frames.append(Image.fromarray(frame_rgb))
            frame_idx += 1
        cap.release()
        return frames

    def predict(self, video_path):
        frames = self.extract_frames(video_path)
        if not frames:
            return {"result": "ERROR", "confidence": 0, "message": "No frames extracted"}

        predictions  = []
        confidences  = []
        frame_details = []

        with torch.no_grad():
            for i, frame in enumerate(frames):
                tensor = self.transform(frame).unsqueeze(0).to(self.device)
                output = self.model(tensor)
                probs  = torch.softmax(output, dim=1)
                pred   = output.argmax(dim=1).item()
                conf   = probs[0][pred].item()
                predictions.append(pred)
                confidences.append(conf)
                frame_details.append({
                    "frame"     : i + 1,
                    "result"    : "REAL" if pred == 0 else "FAKE",
                    "confidence": round(conf * 100, 2)
                })

        fake_count = sum(predictions)
        real_count = len(predictions) - fake_count
        avg_conf   = float(np.mean(confidences))
        result     = "FAKE" if fake_count > real_count else "REAL"

        return {
            "result"       : result,
            "confidence"   : round(avg_conf * 100, 2),
            "fake_frames"  : fake_count,
            "real_frames"  : real_count,
            "total_frames" : len(predictions),
            "frame_details": frame_details
        }

    def predict_image(self, image_path):
        try:
            img    = Image.open(image_path).convert("RGB")
            tensor = self.transform(img).unsqueeze(0).to(self.device)
            with torch.no_grad():
                output = self.model(tensor)
                probs  = torch.softmax(output, dim=1)
                pred   = output.argmax(dim=1).item()
                conf   = probs[0][pred].item()
            label = "REAL" if pred == 0 else "FAKE"
            return {
                "result"    : label,
                "confidence": round(conf * 100, 2),
                "real_prob" : round(probs[0][0].item() * 100, 2),
                "fake_prob" : round(probs[0][1].item() * 100, 2)
            }
        except Exception as e:
            return {"result": "ERROR", "confidence": 0, "message": str(e)}