import asyncio
import torch
from faster_whisper import WhisperModel
from ws_manager import WSConnectionManager
from concurrent.futures import ThreadPoolExecutor

audio_queue: asyncio.Queue = asyncio.Queue(maxsize=100)  # Backpressure limit

ws_manager = WSConnectionManager()

device = "cuda" if torch.cuda.is_available() else "cpu"
compute_type = "float16" if device == "cuda" else "int8"
executor = ThreadPoolExecutor(max_workers=4 if device == "cuda" else 1)  # Parallel if GPU

model = WhisperModel(
    "base.en",
    device=device,
    compute_type=compute_type
)

# Per-connection state
STATE = {}  # {'buffer': list[np.array], 'prev_text': '', 'transcription': '', 'timer': None, 'last_time': float, 'version': int, 'silence_backoff': float, 'rate_limit': {'last_chunk': float, 'chunks_per_sec': 0}, 'last_segments': [], 'last_audio_len': 0, 'session_id': str | None}

MAX_BUFFER_SECONDS = 30
MAX_BUFFER_SAMPLES = MAX_BUFFER_SECONDS * 16000
BASE_SILENCE_TIMEOUT = 1.0
MAX_SILENCE_BACKOFF = 3.0
ENERGY_THRESHOLD = 0.01  # For noise rejection
SAMPLE_RATE = 16000
CHUNKS_PER_SECOND_LIMIT = 10  # Rate limit