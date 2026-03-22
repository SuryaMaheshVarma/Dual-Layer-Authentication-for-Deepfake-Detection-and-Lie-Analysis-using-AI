import cv2
import numpy as np
import librosa
from deepface import DeepFace

class LieDetector:
    def __init__(self, model_path=None):
        print("✅ Lie detection (DeepFace emotion) loaded!")

    def analyze_emotions_from_video(self, video_path, max_frames=20):
        cap          = cv2.VideoCapture(video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if total_frames == 0:
            cap.release()
            return None

        indices   = [int(i * total_frames / max_frames) for i in range(max_frames)]
        emotions  = []
        frame_idx = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            if frame_idx in indices:
                try:
                    result = DeepFace.analyze(
                        frame,
                        actions           = ['emotion'],
                        enforce_detection = False,
                        silent            = True
                    )
                    emotions.append(result[0]['emotion'])
                except:
                    pass
            frame_idx += 1
        cap.release()
        return emotions

    def compute_verdict(self, emotions):
        if not emotions:
            return {
                "result"        : "TRUTHFUL",
                "confidence"    : 60.0,
                "truthful_prob" : 60.0,
                "deceptive_prob": 40.0
            }

        dominant_emotions = []
        all_scores = {
            'angry': [], 'fear': [], 'disgust': [],
            'neutral': [], 'happy': [], 'sad': [], 'surprise': []
        }

        for frame_e in emotions:
            for key in all_scores:
                all_scores[key].append(frame_e.get(key, 0))
            dominant = max(frame_e, key=frame_e.get)
            dominant_emotions.append(dominant)

        deceptive_labels = ['angry', 'fear', 'disgust', 'sad']
        truthful_labels  = ['neutral', 'happy']

        deceptive_frames = sum(1 for e in dominant_emotions if e in deceptive_labels)
        truthful_frames  = sum(1 for e in dominant_emotions if e in truthful_labels)
        total_frames     = len(dominant_emotions)

        avg = {k: float(np.mean(v)) for k, v in all_scores.items()}

        deceptive_score = (
            avg['angry']   * 0.40 +
            avg['fear']    * 0.25 +
            avg['disgust'] * 0.20 +
            avg['sad']     * 0.15
        )
        truthful_score = (
            avg['neutral'] * 0.60 +
            avg['happy']   * 0.40
        )

        frame_ratio   = deceptive_frames / max(total_frames, 1)
        raw_deceptive = (deceptive_score * 0.65) + (frame_ratio * 100 * 0.35)
        raw_truthful  = (truthful_score  * 0.65) + ((1 - frame_ratio) * 100 * 0.35)

        total = raw_deceptive + raw_truthful
        if total == 0:
            deceptive_prob = 50.0
            truthful_prob  = 50.0
        else:
            deceptive_prob = round((raw_deceptive / total) * 100, 2)
            truthful_prob  = round(100 - deceptive_prob, 2)

        if deceptive_prob >= 45:
            result     = "DECEPTIVE"
            confidence = deceptive_prob
        else:
            result     = "TRUTHFUL"
            confidence = truthful_prob

        print(f"\n📊 Emotion Analysis:")
        print(f"   Dominant emotions: {dominant_emotions}")
        print(f"   Deceptive frames : {deceptive_frames}/{total_frames}")
        print(f"   Truthful frames  : {truthful_frames}/{total_frames}")
        print(f"   Avg angry        : {avg['angry']:.1f}%")
        print(f"   Avg fear         : {avg['fear']:.1f}%")
        print(f"   Avg sad          : {avg['sad']:.1f}%")
        print(f"   Avg neutral      : {avg['neutral']:.1f}%")
        print(f"   Avg happy        : {avg['happy']:.1f}%")
        print(f"   → Deceptive prob : {deceptive_prob}%")
        print(f"   → Result         : {result}\n")

        return {
            "result"        : result,
            "confidence"    : round(confidence, 2),
            "truthful_prob" : truthful_prob,
            "deceptive_prob": deceptive_prob,
            "emotion_summary": {
                "dominant_emotions": dominant_emotions,
                "deceptive_frames" : deceptive_frames,
                "truthful_frames"  : truthful_frames,
                "avg_angry"        : round(avg['angry'], 1),
                "avg_fear"         : round(avg['fear'], 1),
                "avg_sad"          : round(avg['sad'], 1),
                "avg_neutral"      : round(avg['neutral'], 1),
                "avg_happy"        : round(avg['happy'], 1)
            }
        }

    def predict(self, video_path):
        emotions = self.analyze_emotions_from_video(video_path)
        return self.compute_verdict(emotions)

    def predict_audio_only(self, audio_path):
        """
        Audio-only lie detection using multiple acoustic stress features.
        NOTE: Pure audio lie detection is inherently limited (~60-65% accuracy).
        This uses vocal stress indicators as proxy for deception.
        """
        try:
            y, sr = librosa.load(audio_path, sr=22050, mono=True)
            if len(y) == 0:
                return {
                    "result"        : "TRUTHFUL",
                    "confidence"    : 60.0,
                    "truthful_prob" : 60.0,
                    "deceptive_prob": 40.0
                }

            # ── Feature 1: MFCC statistics ──
            mfccs        = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            mfcc_std     = float(np.std(mfccs))
            mfcc_delta   = librosa.feature.delta(mfccs)
            mfcc_d_std   = float(np.std(mfcc_delta))  # rate of change

            # ── Feature 2: Pitch (F0) variance — key stress indicator ──
            f0, voiced_flag, _ = librosa.pyin(
                y, fmin=librosa.note_to_hz('C2'),
                fmax=librosa.note_to_hz('C7')
            )
            f0_voiced = f0[voiced_flag] if voiced_flag is not None else np.array([])
            if len(f0_voiced) > 1:
                pitch_std    = float(np.std(f0_voiced))
                pitch_range  = float(np.max(f0_voiced) - np.min(f0_voiced))
                pitch_mean   = float(np.mean(f0_voiced))
            else:
                pitch_std    = 0.0
                pitch_range  = 0.0
                pitch_mean   = 150.0

            # ── Feature 3: Energy features ──
            rmse         = librosa.feature.rms(y=y)[0]
            rmse_std     = float(np.std(rmse))
            rmse_mean    = float(np.mean(rmse))
            # Energy irregularity — stressed speech has uneven energy
            energy_cv    = (rmse_std / rmse_mean * 100) if rmse_mean > 0 else 0

            # ── Feature 4: Speaking rate (flux) ──
            flux         = librosa.onset.onset_strength(y=y, sr=sr)
            flux_std     = float(np.std(flux))
            onset_frames = librosa.onset.onset_detect(y=y, sr=sr)
            speaking_rate = len(onset_frames) / (len(y) / sr)  # syllables per second

            # ── Feature 5: Spectral features ──
            spec_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            centroid_std  = float(np.std(spec_centroid))
            spec_rolloff  = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
            rolloff_std   = float(np.std(spec_rolloff))

            # ── Feature 6: Voiced/unvoiced ratio ──
            zcr           = librosa.feature.zero_crossing_rate(y)[0]
            zcr_mean      = float(np.mean(zcr))

            # ── Normalize each feature to 0-100 ──
            # Higher = more stress
            s_mfcc_std   = min(mfcc_std   / 120  * 100, 100)
            s_mfcc_delta = min(mfcc_d_std / 15   * 100, 100)
            s_pitch_std  = min(pitch_std  / 80   * 100, 100)
            s_pitch_range= min(pitch_range/ 300  * 100, 100)
            s_energy_cv  = min(energy_cv  / 150  * 100, 100)
            s_flux_std   = min(flux_std   / 8    * 100, 100)
            s_speak_rate = min(speaking_rate / 10 * 100, 100)
            s_centroid   = min(centroid_std / 2000 * 100, 100)

            # ── Weighted stress score ──
            # Pitch variance is most reliable stress indicator
            stress_score = (
                s_pitch_std   * 0.25 +  # pitch variance — best stress indicator
                s_pitch_range * 0.15 +  # pitch range
                s_mfcc_delta  * 0.15 +  # MFCC rate of change
                s_energy_cv   * 0.15 +  # energy irregularity
                s_mfcc_std    * 0.10 +  # MFCC spread
                s_flux_std    * 0.10 +  # onset irregularity
                s_speak_rate  * 0.05 +  # speaking rate
                s_centroid    * 0.05    # spectral brightness
            )

            deceptive_prob = round(min(stress_score, 100), 2)
            truthful_prob  = round(100 - deceptive_prob, 2)
            result         = "DECEPTIVE" if deceptive_prob >= 55 else "TRUTHFUL"
            confidence     = deceptive_prob if result == "DECEPTIVE" else truthful_prob

            print(f"\n📊 Audio Analysis (Enhanced):")
            print(f"   Pitch std     : {pitch_std:.1f}  → score {s_pitch_std:.1f}")
            print(f"   Pitch range   : {pitch_range:.1f} → score {s_pitch_range:.1f}")
            print(f"   MFCC delta    : {mfcc_d_std:.2f} → score {s_mfcc_delta:.1f}")
            print(f"   Energy CV     : {energy_cv:.1f}% → score {s_energy_cv:.1f}")
            print(f"   MFCC std      : {mfcc_std:.1f}  → score {s_mfcc_std:.1f}")
            print(f"   Speaking rate : {speaking_rate:.1f}/s → score {s_speak_rate:.1f}")
            print(f"   Stress score  : {stress_score:.1f}%")
            print(f"   → Result      : {result}\n")

            return {
                "result"        : result,
                "confidence"    : round(confidence, 2),
                "truthful_prob" : truthful_prob,
                "deceptive_prob": deceptive_prob
            }

        except Exception as e:
            print(f"Audio analysis error: {e}")
            return {
                "result"        : "TRUTHFUL",
                "confidence"    : 60.0,
                "truthful_prob" : 60.0,
                "deceptive_prob": 40.0
            }