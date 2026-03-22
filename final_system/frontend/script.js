//const API_URL    = 'http://localhost:8000';
//const API_URL = 'https://exsufflicate-rudolph-squamate.ngrok-free.dev';
const API_URL = 'https://exsufflicate-rudolph-squamate.ngrok-free.dev';
let selectedFile = null;
let currentTab   = 'video';

// Emotion colors and labels
const EMOTION_CONFIG = {
    angry:   { color: '#f43f5e', label: 'Angry',    deceptive: true  },
    fear:    { color: '#f97316', label: 'Fear',     deceptive: true  },
    disgust: { color: '#a855f7', label: 'Disgust',  deceptive: true  },
    sad:     { color: '#6366f1', label: 'Sad',      deceptive: true  },
    neutral: { color: '#00f5c4', label: 'Neutral',  deceptive: false },
    happy:   { color: '#22c55e', label: 'Happy',    deceptive: false },
    surprise:{ color: '#0ea5e9', label: 'Surprise', deceptive: false }
};

// ── TAB SWITCHING ─────────────────────────────────────────────
function switchTab(tab) {
    currentTab = tab;
    document.querySelectorAll('.type-btn').forEach(b => b.classList.remove('active'));
    document.getElementById(`tab-${tab}`).classList.add('active');

    const config = {
        video: { accept: 'video/*', emoji: '📹', hint: 'Supports MP4, AVI, MOV — max 500MB' },
        image: { accept: 'image/*', emoji: '🖼️', hint: 'Supports JPG, PNG, WEBP, BMP'       },
        audio: { accept: 'audio/*', emoji: '🎙️', hint: 'Supports MP3, WAV, M4A, OGG'        }
    };
    const c = config[tab];
    document.getElementById('fileInput').accept        = c.accept;
    document.getElementById('uploadEmoji').textContent = c.emoji;
    document.getElementById('uploadHint').textContent  = c.hint;
    resetUpload();
}

// ── DRAG AND DROP ─────────────────────────────────────────────
const uploadZone = document.getElementById('uploadZone');
const fileInput  = document.getElementById('fileInput');

uploadZone.addEventListener('dragover', (e) => { e.preventDefault(); uploadZone.classList.add('dragover'); });
uploadZone.addEventListener('dragleave', () => uploadZone.classList.remove('dragover'));
uploadZone.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadZone.classList.remove('dragover');
    if (e.dataTransfer.files[0]) handleFile(e.dataTransfer.files[0]);
});
uploadZone.addEventListener('click', (e) => {
    if (e.target.classList.contains('upload-btn') || e.target === fileInput) return;
    fileInput.click();
});
fileInput.addEventListener('change', (e) => { if (e.target.files[0]) handleFile(e.target.files[0]); });

// ── HANDLE FILE ───────────────────────────────────────────────
function handleFile(file) {
    selectedFile = file;
    const url    = URL.createObjectURL(file);
    const sizeMB = (file.size / 1024 / 1024).toFixed(2);

    uploadZone.style.display = 'none';
    document.getElementById('previewZone').style.display  = 'flex';
    document.getElementById('resultsZone').style.display  = 'none';

    ['previewVideo','previewImage'].forEach(id =>
        document.getElementById(id).style.display = 'none'
    );

    if (currentTab === 'video') {
        const v = document.getElementById('previewVideo');
        v.src = url; v.style.display = 'block';
    } else if (currentTab === 'image') {
        const i = document.getElementById('previewImage');
        i.src = url; i.style.display = 'block';
    } else {
        document.getElementById('previewAudio').style.display = 'flex';
        document.getElementById('audioPlayer').src = url;
    }

    document.getElementById('fileChip').textContent = `${file.name}  ·  ${sizeMB} MB`;
}

// ── ANALYZE ───────────────────────────────────────────────────
async function analyzeFile() {
    if (!selectedFile) return;

    const btn = document.getElementById('analyzeBtn');
    btn.disabled = true;
    btn.querySelector('.btn-text').textContent = 'Analyzing...';

    const msgs = {
        video: 'Running deepfake detection and emotion analysis...',
        image: 'Scanning image for AI manipulation...',
        audio: 'Analyzing vocal stress patterns...'
    };
    document.getElementById('loadingMsg').textContent = msgs[currentTab];

    document.getElementById('resultsZone').style.display  = 'block';
    document.getElementById('loadingState').style.display = 'flex';
    document.getElementById('verdictZone').style.display  = 'none';
    document.getElementById('resultsZone').scrollIntoView({ behavior: 'smooth' });

    // Animate loading steps
    const steps = ['ls1','ls2','ls3','ls4'];
    let si = 0;
    const stepTimer = setInterval(() => {
        if (si < steps.length) {
            document.getElementById(steps[si]).classList.add('done');
            si++;
        } else {
            clearInterval(stepTimer);
        }
    }, 800);

    try {
        const formData = new FormData();
        formData.append('file', selectedFile);

        const resp = await fetch(`${API_URL}/analyze/${currentTab}`, {
            method: 'POST', body: formData,
            headers: { 'ngrok-skip-browser-warning': 'true' }
        });
        const data = await resp.json();
        clearInterval(stepTimer);
        steps.forEach(s => document.getElementById(s).classList.add('done'));
        setTimeout(() => displayResults(data), 400);

    } catch (err) {
        clearInterval(stepTimer);
        displayError(err.message);
    }

    btn.disabled = false;
    btn.querySelector('.btn-text').textContent = 'Run Analysis';
}

// ── DISPLAY RESULTS ───────────────────────────────────────────
function displayResults(data) {
    document.getElementById('loadingState').style.display = 'none';
    document.getElementById('verdictZone').style.display  = 'block';

    // ── Verdict card ──
    const card   = document.getElementById('verdictCard');
    const status = document.getElementById('verdictStatus');
    const detail = document.getElementById('verdictDetail');
    const meta   = document.getElementById('verdictMeta');
    const badge  = document.getElementById('verdictBadge');

    card.className = 'verdict-card';
    if (data.status === 'AUTHENTICATED') {
        card.classList.add('authenticated');
        badge.textContent  = '✅';
        status.textContent = 'AUTHENTICATED';
    } else if (data.status === 'SUSPICIOUS') {
        card.classList.add('suspicious');
        badge.textContent  = '⚠️';
        status.textContent = 'SUSPICIOUS';
    } else if (data.status === 'REJECTED') {
        card.classList.add('rejected');
        badge.textContent  = '❌';
        status.textContent = 'REJECTED';
    } else {
        card.classList.add('rejected');
        badge.textContent  = '⚠️';
        status.textContent = 'ERROR';
    }
    detail.textContent = data.final_verdict || data.message || '';
    meta.textContent   = data.processing_time
        ? `⏱ Processed in ${data.processing_time}s  ·  Input: ${(data.input_type||'').toUpperCase()}`
        : `Input: ${(data.input_type||'').toUpperCase()}`;

    // ── Trust ring ──
    const trustScore = data.trust_score || 0;
    document.getElementById('trustNum').textContent = `${Math.round(trustScore)}%`;
    const offset = 201 - (trustScore / 100) * 201;
    setTimeout(() => {
        const circle = document.getElementById('trustCircle');
        circle.style.strokeDashoffset = offset;
        circle.style.transition = 'stroke-dashoffset 1.2s ease';
        // Color ring based on score
        circle.style.stroke = trustScore >= 70 ? '#10b981'
                            : trustScore >= 45 ? '#f59e0b' : '#f43f5e';
    }, 100);

    // ── Layer 1 — Deepfake ──
    const l1Card = document.getElementById('layer1Card');
    const df     = data.deepfake;
    if (df && df.result !== 'ERROR') {
        l1Card.style.opacity = '1';
        const color = df.result === 'REAL' ? 'var(--success)' : 'var(--danger)';
        document.getElementById('l1Result').innerHTML = `<span style="color:${color}">${df.result}</span>`;
        document.getElementById('l1Fill').style.width = `${df.confidence}%`;
        document.getElementById('l1Conf').textContent = `${df.confidence}%`;
        document.getElementById('l1Stats').textContent = df.total_frames
            ? `${df.real_frames} real / ${df.fake_frames} fake out of ${df.total_frames} frames`
            : `Real: ${df.real_prob}%  ·  Fake: ${df.fake_prob}%`;
    } else {
        l1Card.style.opacity = '0.3';
        document.getElementById('l1Result').textContent = 'N/A';
        document.getElementById('l1Stats').textContent  =
            currentTab === 'audio' ? 'Not applicable for audio input' : 'Skipped';
    }

    // ── Layer 2 — Behavior ──
    const l2Card = document.getElementById('layer2Card');
    const beh    = data.behavior;
    if (beh && beh.result !== 'ERROR') {
        l2Card.style.opacity = '1';
        const color = beh.result === 'TRUTHFUL' ? 'var(--success)' : 'var(--warn)';
        document.getElementById('l2Result').innerHTML = `<span style="color:${color}">${beh.result}</span>`;
        document.getElementById('l2Fill').style.width = `${beh.confidence}%`;
        document.getElementById('l2Conf').textContent = `${beh.confidence}%`;
        document.getElementById('l2Stats').textContent =
            `Truthful: ${beh.truthful_prob}%  ·  Deceptive: ${beh.deceptive_prob}%`;
    } else {
        l2Card.style.opacity = '0.3';
        document.getElementById('l2Result').textContent = 'N/A';
        document.getElementById('l2Stats').textContent  =
            data.status === 'REJECTED' ? 'Skipped — Deepfake detected at Layer 1'
            : currentTab === 'image'   ? 'Not applicable for image input' : 'Skipped';
    }

    // ── Emotion breakdown ──
    const emo = beh?.emotion_summary;
    if (emo) {
        document.getElementById('emotionSection').style.display = 'block';
        renderEmotionBreakdown(emo, beh);
    } else {
        document.getElementById('emotionSection').style.display = 'none';
    }

    // ── Frame analysis ──
    const frames = data.deepfake?.frame_details;
    if (frames && frames.length > 0) {
        document.getElementById('frameAnalysis').style.display = 'block';
        document.getElementById('faSummary').textContent =
            `${frames.filter(f => f.result === 'REAL').length}/${frames.length} frames authentic`;
        document.getElementById('framesRow').innerHTML = frames.map(f =>
            `<div class="frame-chip ${f.result.toLowerCase()}">F${f.frame} · ${f.result} · ${f.confidence}%</div>`
        ).join('');
    } else {
        document.getElementById('frameAnalysis').style.display = 'none';
    }

    // Process time
    if (data.processing_time) {
        document.getElementById('processTime').textContent = `⏱ ${data.processing_time}s processing time`;
    }
}

// ── RENDER EMOTION BREAKDOWN ──────────────────────────────────
function renderEmotionBreakdown(emo, beh) {
    // Sub text
    document.getElementById('emotionSub').textContent =
        `Based on ${emo.dominant_emotions.length} frames analyzed`;

    // Frame summary
    document.getElementById('emotionFrameSummary').innerHTML =
        `<span style="color:var(--danger)">${emo.deceptive_frames} deceptive frames</span><br>
         <span style="color:var(--success)">${emo.truthful_frames} truthful frames</span>`;

    // Emotion bars
    const barsEl = document.getElementById('emotionBars');
    const emotionData = [
        { key: 'angry',   val: emo.avg_angry   || 0 },
        { key: 'fear',    val: emo.avg_fear     || 0 },
        { key: 'sad',     val: emo.avg_sad      || 0 },
        { key: 'neutral', val: emo.avg_neutral  || 0 },
        { key: 'happy',   val: emo.avg_happy    || 0 },
    ];

    // Sort by value descending
    emotionData.sort((a, b) => b.val - a.val);

    barsEl.innerHTML = emotionData.map(e => {
        const cfg = EMOTION_CONFIG[e.key];
        return `
        <div class="emotion-bar-row">
            <div class="emotion-bar-label">${cfg.label}</div>
            <div class="emotion-bar-track">
                <div class="emotion-bar-fill"
                     style="width:0%;background:${cfg.color}"
                     data-target="${Math.min(e.val, 100)}">
                </div>
            </div>
            <div class="emotion-bar-val">${e.val.toFixed(1)}%</div>
        </div>`;
    }).join('');

    // Animate bars after render
    setTimeout(() => {
        document.querySelectorAll('.emotion-bar-fill').forEach(el => {
            el.style.transition = 'width 1s ease';
            el.style.width = el.dataset.target + '%';
        });
    }, 100);

    // Emotion timeline
    const timelineEl = document.getElementById('emotionTimeline');
    if (emo.dominant_emotions && emo.dominant_emotions.length > 0) {
        timelineEl.innerHTML = emo.dominant_emotions.map((emotion, i) => {
            const cfg = EMOTION_CONFIG[emotion] || { color: '#64748b', label: emotion };
            const shortLabel = emotion.substring(0, 3).toUpperCase();
            return `<div class="emotion-frame-dot"
                         style="background:${cfg.color}22;border:1px solid ${cfg.color}55;color:${cfg.color}"
                         title="Frame ${i+1}: ${cfg.label}">
                        ${shortLabel}
                    </div>`;
        }).join('');
    }
}

// ── ERROR ─────────────────────────────────────────────────────
function displayError(message) {
    document.getElementById('loadingState').style.display = 'none';
    document.getElementById('verdictZone').style.display  = 'block';
    const card = document.getElementById('verdictCard');
    card.className = 'verdict-card rejected';
    document.getElementById('verdictBadge').textContent  = '⚠️';
    document.getElementById('verdictStatus').textContent = 'ERROR';
    document.getElementById('verdictDetail').textContent =
        `Cannot connect to backend: ${message}. Make sure the server is running on port 8000.`;
}

// ── RESET ─────────────────────────────────────────────────────
function resetUpload() {
    selectedFile = null;
    uploadZone.style.display = 'block';
    document.getElementById('previewZone').style.display  = 'none';
    document.getElementById('resultsZone').style.display  = 'none';
    document.getElementById('fileInput').value            = '';
    document.getElementById('previewVideo').src = '';
    document.getElementById('previewImage').src = '';
    //document.getElementById('audioPlayer').src  = '';
    ['ls1','ls2','ls3','ls4'].forEach(id =>
        document.getElementById(id).classList.remove('done')
    );
}

function resetAll() {
    resetUpload();
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ── LAYER ANIMATION ───────────────────────────────────────────
setInterval(() => {
    const items = document.querySelectorAll('.layer-item');
    items.forEach(i => i.classList.remove('active'));
    const active = Math.floor(Date.now() / 1500) % items.length;
    if (items[active]) items[active].classList.add('active');
}, 1500);