# 🛡️ DeepGuard — Dual-Layer AI Media Authentication System

<div align="center">

![DeepGuard Banner](https://img.shields.io/badge/DeepGuard-AI%20Authentication-00f5c4?style=for-the-badge&logo=shield&logoColor=white)

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Netlify-00C7B7?style=for-the-badge&logo=netlify&logoColor=white)](https://preeminent-meringue-ffde50.netlify.app)
[![Model 1 Accuracy](https://img.shields.io/badge/Deepfake%20Accuracy-97.05%25-success?style=for-the-badge)](https://preeminent-meringue-ffde50.netlify.app)
[![Model 2 Accuracy](https://img.shields.io/badge/Behavior%20Accuracy-87.06%25-blue?style=for-the-badge)](https://preeminent-meringue-ffde50.netlify.app)


**Detect deepfakes. Expose deception. Authenticate media.**

[🌐 Live Demo](https://preeminent-meringue-ffde50.netlify.app) • [📖 Documentation](#documentation) • [🚀 Quick Start](#quick-start) • [📊 Results](#results)

</div>

---

## 📌 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [System Architecture](#system-architecture)
- [Datasets](#datasets)
- [Models](#models)
- [Results](#results)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Deployment](#deployment)
- [Limitations](#limitations)
- [Future Work](#future-work)

---

## 🔍 Overview

DeepGuard is a **dual-layer AI authentication system** that analyzes video and image media through two independent AI models:

1. **Layer 1 — Deepfake Detection**: EfficientNet-B0 CNN trained on Celeb-DF v2 dataset to detect face-swapped or AI-generated videos with **97.05% accuracy**
2. **Layer 2 — Behavioral Analysis**: DeepFace pretrained emotion recognition that detects deceptive behavioral patterns across 7 emotions

The system produces one of three verdicts:

| Verdict | Icon | Meaning |
|---|---|---|
| AUTHENTICATED | ✅ | Real media with truthful behavior |
| SUSPICIOUS | ⚠️ | Real media but deceptive patterns detected |
| REJECTED | ❌ | Deepfake detected |

---

## ✨ Features

- 🎥 **Video Analysis** — Deepfake detection + behavioral analysis + frame-by-frame breakdown
- 🖼️ **Image Analysis** — AI-generated or manipulated image detection
- 😐 **Emotion Breakdown** — Visual bar charts showing 7 emotions detected per frame
- 🔄 **Trust Score** — Combined authenticity score (0-100%)
- 👤 **User Authentication** — Email/password + GitHub OAuth via Supabase
- 📊 **Analysis History** — All past analyses saved per user in PostgreSQL
- 🌐 **Web Accessible** — No installation required, works in any browser

---

## 🏗️ System Architecture

```
Input Media (Video/Image)
         │
         ▼
┌─────────────────────┐
│  Layer 1            │
│  EfficientNet-B0    │──── FAKE ──→ ❌ REJECTED
│  Deepfake Detection │
└─────────┬───────────┘
          │ REAL
          ▼
┌─────────────────────┐
│  Layer 2            │──── DECEPTIVE ──→ ⚠️ SUSPICIOUS
│  DeepFace Emotion   │
│  Behavior Analysis  │──── TRUTHFUL ──→ ✅ AUTHENTICATED
└─────────────────────┘
          │
          ▼
   Trust Score Formula:
   0.7 × deepfake_confidence + 0.3 × truthful_probability
```

---

## 📦 Datasets

### Dataset 1 — Celeb-DF v2 (Model 1)
| Folder | Content | Count |
|---|---|---|
| Celeb-real | Real celebrity videos | 158 videos |
| Celeb-synthesis | Deepfake videos | 795 videos |
| YouTube-real | Real YouTube videos | 250 videos |
| **After extraction** | **Total frames** | **12,030 images** |

### Dataset 2 — Real-Life Deception Detection 2016 (Model 2)
| Category | Count | Source |
|---|---|---|
| Truthful videos | 60 | Real courtroom testimony |
| Deceptive videos | 61 | Real courtroom testimony |

### Dataset 3 — RAVDESS Audio Speech (Augmentation)
| Category | Count | Mapping |
|---|---|---|
| Calm/Neutral/Happy/Sad | 672 | → Truthful (label 0) |
| Angry/Fearful/Disgust/Surprised | 768 | → Deceptive (label 1) |
| **Total after augmentation** | **1,561 samples** | — |

---

## 🧠 Models

### Model 1 — EfficientNet-B0

```python
Base Model   : EfficientNet-B0 (pretrained on ImageNet)
Parameters   : 23.06M
Input Size   : 224×224 RGB
Output       : 2 classes (Real / Fake)

Custom Classifier Head:
  Dropout(0.4) → Linear(1280→512) → ReLU → BatchNorm
  Dropout(0.3) → Linear(512→128)  → ReLU → Linear(128→2)

Training:
  Platform   : Google Colab T4 GPU
  Epochs     : 20
  Batch Size : 32
  Optimizer  : Adam (lr=0.0005)
  Scheduler  : CosineAnnealingLR
  Augmentation: RandomFlip, Rotation, ColorJitter
```

### Model 2 — DeepFace Emotion Analysis

```python
Library      : DeepFace (Facebook AI Research)
Emotions     : angry, fear, disgust, neutral, happy, sad, surprise
Frames       : 20 per video
Detector     : OpenCV backend

Deceptive emotion weights:
  angry   × 0.40
  fear    × 0.25
  disgust × 0.20
  sad     × 0.15

Final score = emotion_score × 0.65 + frame_ratio × 0.35
Threshold   : deceptive_prob ≥ 38% → SUSPICIOUS
```

> **Note**: An earlier BiLSTM model was trained from scratch achieving **87.06% mean accuracy** with 5-fold cross validation on the courtroom dataset. DeepFace was adopted for better generalization to casual everyday videos.

---

## 📊 Results

### Model 1 — Deepfake Detection

| Metric | Value |
|---|---|
| Validation Accuracy | **97.05%** |
| Real Precision | 97% |
| Real Recall | 94% |
| Fake Precision | 97% |
| Fake Recall | 98% |
| Live Inference Confidence | 99–100% per frame |

### Model 2 — BiLSTM (Original Training)

| Fold | Accuracy |
|---|---|
| Fold 1 | 90.7% |
| Fold 2 | 82.4% |
| Fold 3 | 86.9% |
| Fold 4 | 86.9% |
| Fold 5 | 88.5% |
| **Mean** | **87.06%** |
| **Std** | **2.74%** |

---
<img width="1506" height="803" alt="image" src="https://github.com/user-attachments/assets/b6b3b396-ca67-441b-9609-a6ecb09770a0" />


## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Frontend | HTML / CSS / JavaScript | Web UI |
| Backend | Python FastAPI | ML inference API |
| Model 1 | PyTorch + EfficientNet-B0 | Deepfake detection |
| Model 2 | DeepFace (TensorFlow) | Emotion analysis |
| Tunnel | ngrok | Expose Colab publicly |
| Hosting | Netlify | Frontend deployment |
| Database | Supabase (PostgreSQL) | User data + history |
| Auth | Supabase Auth | Email + GitHub OAuth |
| Model Storage | Google Drive | Store .pth files |
| Training | Google Colab T4 GPU | Model training |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Google Colab account (for backend)
- ngrok account (free)

### 1. Clone Repository
```bash
git clone https://github.com/varunMVP/deepguard-backend.git
cd deepguard-backend
```

### 2. Install Dependencies
```bash
pip install fastapi uvicorn python-multipart deepface tf-keras librosa
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

### 3. Download Models
Place these files in `backend/models/`:
- `best_model_v2.pth` — EfficientNet-B0 weights
- `best_lie_model_v2.pth` — BiLSTM weights (optional)

### 4. Run Backend
```bash
cd backend
uvicorn main:app --reload --port 8000
```

### 5. Open Frontend
Open `frontend/index.html` in your browser or deploy to Netlify.

---

## 📁 Project Structure

```
deepguard/
├── backend/
│   ├── main.py              # FastAPI server — video/image endpoints
│   ├── model1.py            # DeepfakeDetector class (EfficientNet-B0)
│   ├── model2.py            # LieDetector class (DeepFace)
│   ├── requirements.txt     # Python dependencies
│   ├── Dockerfile           # Container configuration
│   └── models/
│       ├── best_model_v2.pth         # Deepfake model weights
│       └── best_lie_model_v2.pth     # BiLSTM weights
└── frontend/
    ├── index.html           # Main application (protected)
    ├── login.html           # Login page
    ├── signup.html          # Registration page
    ├── history.html         # Analysis history page
    ├── auth.js              # Supabase authentication functions
    ├── script.js            # Main app logic + API calls
    └── style.css            # Dark technical theme
```

---

## 🌐 Deployment

### Frontend — Netlify
1. Drag and drop `frontend/` folder to [netlify.com](https://netlify.com)
2. Live at: **https://preeminent-meringue-ffde50.netlify.app**

### Backend — Google Colab + ngrok
```python
# Run all 6 cells in deepguard_server.ipynb
# Cell 1: Install libraries
# Cell 2: Download models from Drive
# Cell 3: Create model1.py
# Cell 4: Create model2.py
# Cell 5: Create main.py
# Cell 6: Start server + ngrok tunnel
```

### API Endpoints
| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Health check |
| POST | `/analyze/video` | Deepfake + behavior analysis |
| POST | `/analyze/image` | Deepfake detection only |

---

## ⚠️ Limitations

- **Domain dependency**: The behavioral model performs best on formal/interview-style videos. Casual videos may produce false positives due to domain mismatch between training data (courtroom) and test data.
- **AI art detection**: The system detects GAN-based face swaps (Celeb-DF type) but not diffusion model generated images (MidJourney, DALL-E).
- **Othello Error**: Stressed truthful people may show similar emotion patterns to deceptive individuals — a known limitation shared by professional polygraph systems (15–25% false positive rate).
- **24/7 availability**: Backend requires Google Colab session to be active.

---

## 🔮 Future Work

- [ ] Train diffusion model detector for MidJourney/DALL-E generated images
- [ ] Collect diverse casual video dataset to reduce domain mismatch
- [ ] Deploy on GPU cloud server for 24/7 availability
- [ ] Audio deepfake detection using voice cloning detection
- [ ] Mobile app for on-device inference
- [ ] Multi-face detection for group videos

---


## 🙏 Acknowledgements

- [Celeb-DF v2](https://github.com/yuezunli/celeb-deepfakeforensics) — Deepfake detection dataset
- [Real-Life Deception Detection 2016](https://web.eecs.umich.edu/~mihalcea/downloads.html) — University of Michigan
- [RAVDESS](https://zenodo.org/record/1188976) — Ryerson Audio-Visual Database
- [DeepFace](https://github.com/serengil/deepface) — Facebook AI Research
- [EfficientNet](https://arxiv.org/abs/1905.11946) — Google Brain

---

<div align="center">
Built with ❤️ | EfficientNet-B0 + DeepFace | Deployed on Netlify + Supabase

⭐ Star this repo if you found it useful!
</div>
