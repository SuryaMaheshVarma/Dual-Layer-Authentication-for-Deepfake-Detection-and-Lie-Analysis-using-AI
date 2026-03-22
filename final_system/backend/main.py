from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import shutil, os, uuid, time
from model1 import DeepfakeDetector
from model2 import LieDetector

# Auto download models if not present
from download_models import download_models
download_models()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

deepfake_model = DeepfakeDetector(os.path.join(MODELS_DIR, "best_model_v2.pth"))
#lie_model      = LieDetector(os.path.join(MODELS_DIR, "best_lie_model_v2.pth"))
lie_model = LieDetector()

@app.get("/")
def root():
    return {"status": "DeepGuard API running"}

# ── VIDEO ─────────────────────────────────────────────────────
@app.post("/analyze/video")
async def analyze_video(file: UploadFile = File(...)):
    start_time = time.time()
    ext        = os.path.splitext(file.filename)[1]
    filename   = f"{uuid.uuid4()}{ext}"
    filepath   = os.path.join(UPLOAD_DIR, filename)

    with open(filepath, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        deepfake_result = deepfake_model.predict(filepath)

        if deepfake_result["result"] == "FAKE":
            os.remove(filepath)
            processing_time = round(time.time() - start_time, 2)
            return {
                "status"          : "REJECTED",
                "input_type"      : "video",
                "trust_score"     : 0,
                "processing_time" : processing_time,
                "deepfake"        : deepfake_result,
                "behavior"        : None,
                "final_verdict"   : "REJECTED — Video is a deepfake"
            }

        lie_result      = lie_model.predict(filepath)
        os.remove(filepath)

        deceptive_prob  = lie_result.get("deceptive_prob", 0)
        truthful_prob   = lie_result.get("truthful_prob", 50)

        if lie_result["result"] == "DECEPTIVE" and deceptive_prob >= 60:
            status  = "SUSPICIOUS"
            verdict = "SUSPICIOUS — Real video but deceptive behavior detected"
        elif lie_result["result"] == "DECEPTIVE" and deceptive_prob >= 45:
            status  = "SUSPICIOUS"
            verdict = "SUSPICIOUS — Mild deceptive behavioral patterns detected"
        else:
            status  = "AUTHENTICATED"
            verdict = "AUTHENTICATED — Real video with truthful behavior"

        deepfake_conf = deepfake_result.get("confidence", 0)
        trust_score   = round(0.6 * deepfake_conf + 0.4 * truthful_prob, 2)
        processing_time = round(time.time() - start_time, 2)

        return {
            "status"          : status,
            "input_type"      : "video",
            "trust_score"     : trust_score,
            "processing_time" : processing_time,
            "deepfake"        : deepfake_result,
            "behavior"        : lie_result,
            "final_verdict"   : verdict
        }

    except Exception as e:
        if os.path.exists(filepath):
            os.remove(filepath)
        return {"status": "ERROR", "message": str(e)}

# ── IMAGE ─────────────────────────────────────────────────────
@app.post("/analyze/image")
async def analyze_image(file: UploadFile = File(...)):
    start_time = time.time()
    ext        = os.path.splitext(file.filename)[1]
    filename   = f"{uuid.uuid4()}{ext}"
    filepath   = os.path.join(UPLOAD_DIR, filename)

    with open(filepath, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        result  = deepfake_model.predict_image(filepath)
        os.remove(filepath)

        status  = "REJECTED"      if result["result"] == "FAKE" else "AUTHENTICATED"
        verdict = "REJECTED — Image appears to be AI generated or manipulated" \
                  if result["result"] == "FAKE" \
                  else "AUTHENTICATED — Image appears to be genuine"

        trust_score     = result.get("real_prob", 0) if result["result"] == "REAL" else 0
        processing_time = round(time.time() - start_time, 2)

        return {
            "status"          : status,
            "input_type"      : "image",
            "trust_score"     : trust_score,
            "processing_time" : processing_time,
            "deepfake"        : result,
            "behavior"        : None,
            "final_verdict"   : verdict
        }

    except Exception as e:
        if os.path.exists(filepath):
            os.remove(filepath)
        return {"status": "ERROR", "message": str(e)}

# ── AUDIO ─────────────────────────────────────────────────────
@app.post("/analyze/audio")
async def analyze_audio(file: UploadFile = File(...)):
    start_time = time.time()
    ext        = os.path.splitext(file.filename)[1]
    filename   = f"{uuid.uuid4()}{ext}"
    filepath   = os.path.join(UPLOAD_DIR, filename)

    with open(filepath, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        result  = lie_model.predict_audio_only(filepath)
        os.remove(filepath)

        status  = "SUSPICIOUS"    if result["result"] == "DECEPTIVE" else "AUTHENTICATED"
        verdict = "SUSPICIOUS — Deceptive vocal patterns detected" \
                  if result["result"] == "DECEPTIVE" \
                  else "AUTHENTICATED — Truthful vocal patterns detected"

        trust_score     = result.get("truthful_prob", 0)
        processing_time = round(time.time() - start_time, 2)

        return {
            "status"          : status,
            "input_type"      : "audio",
            "trust_score"     : trust_score,
            "processing_time" : processing_time,
            "deepfake"        : None,
            "behavior"        : result,
            "final_verdict"   : verdict
        }

    except Exception as e:
        if os.path.exists(filepath):
            os.remove(filepath)
        return {"status": "ERROR", "message": str(e)}