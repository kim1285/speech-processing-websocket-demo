import asyncio
import time
import numpy as np
import re
from global_state import audio_queue, ws_manager, model, executor, STATE, MAX_BUFFER_SAMPLES, BASE_SILENCE_TIMEOUT, \
    MAX_SILENCE_BACKOFF, ENERGY_THRESHOLD, SAMPLE_RATE, CHUNKS_PER_SECOND_LIMIT


def cleanup(cid: str):
    if cid in STATE:
        if STATE[cid]['timer']:
            STATE[cid]['timer'].cancel()
        del STATE[cid]


ws_manager.on_disconnect = cleanup


async def transcribe_async(audio, **kwargs):
    loop = asyncio.get_event_loop()

    def sync_transcribe():
        segments, info = model.transcribe(audio, **kwargs)
        return list(segments), info

    return await loop.run_in_executor(executor, sync_transcribe)


def is_noise_only(audio_np: np.ndarray) -> bool:
    energy = np.sqrt(np.mean(audio_np ** 2))
    return energy < ENERGY_THRESHOLD


def detect_sentence_boundary(text: str) -> bool:
    return bool(re.search(r'[.!?]\s*$', text))


async def ml_worker():
    from collections import deque
    transcription_times = deque(maxlen=100)

    while True:
        try:
            cid, chunk = await audio_queue.get()
        except asyncio.CancelledError:
            break

        if cid not in STATE:
            STATE[cid] = {
                'buffer': [],
                'prev_text': '',
                'transcription': '',
                'timer': None,
                'last_time': time.time(),
                'version': 0,
                'silence_backoff': BASE_SILENCE_TIMEOUT,
                'rate_limit': {'last_chunk': 0, 'chunks_per_sec': 0},
                'last_segments': [],
                'last_audio_len': 0,
                'session_id': None  # For reconnection; set via client message if needed
            }

        s = STATE[cid]

        # Rate limiting
        now = time.time()
        if now - s['rate_limit']['last_chunk'] < 1:
            s['rate_limit']['chunks_per_sec'] += 1
            if s['rate_limit']['chunks_per_sec'] > CHUNKS_PER_SECOND_LIMIT:
                continue  # Drop chunk
        else:
            s['rate_limit']['chunks_per_sec'] = 1
        s['rate_limit']['last_chunk'] = now

        audio_np = np.frombuffer(chunk, dtype=np.int16).astype(np.float32) / 32768.0

        # Audio validation: sample rate implicit (assume 16k), reject noise
        if len(audio_np) == 0 or is_noise_only(audio_np):
            continue

        s['buffer'].append(audio_np)
        s['last_time'] = now
        s['version'] += 1
        current_version = s['version']

        # Limit buffer size (sliding window)
        audio = np.concatenate(s['buffer'])
        while len(audio) > MAX_BUFFER_SAMPLES:
            s['buffer'].pop(0)
            audio = np.concatenate(s['buffer'])

        start = time.time()
        # Partial transcription (fast)
        segments, _ = await transcribe_async(
            audio,
            beam_size=5,
            initial_prompt=s['prev_text'],
            vad_filter=True,
            language="en"
        )
        text = ' '.join(seg.text for seg in segments).strip()
        duration = time.time() - start
        transcription_times.append(duration)

        conn = ws_manager.get(cid)
        if conn and text != s['prev_text']:
            await conn.send({
                "type": "partial",
                "text": text
            })
            s['prev_text'] = text
            s['transcription'] = text
            s['last_segments'] = segments
            s['last_audio_len'] = len(audio)

        # Cancel timer
        if s['timer']:
            s['timer'].cancel()

        async def check_silence():
            timeout = s['silence_backoff']
            await asyncio.sleep(timeout)
            if s['version'] != current_version:
                return  # Race: new audio arrived
            if time.time() - s['last_time'] < timeout:
                return

            # Check for sentence boundary first
            if detect_sentence_boundary(s['transcription']):
                # Full transcription (optimized: only if significant new audio)
                if len(audio) - s['last_audio_len'] > 8000:  # >0.5s new
                    segments, _ = await transcribe_async(
                        audio,
                        beam_size=7,
                        initial_prompt=s['transcription'],
                        vad_filter=True,
                        language="en"
                    )
                else:
                    segments = s['last_segments']  # Reuse

                new_text = ' '.join(seg.text for seg in segments).strip()
                if conn and new_text != s['transcription']:
                    await conn.send({
                        "type": "final",
                        "text": new_text
                    })
                    s['transcription'] = new_text
                    s['prev_text'] = new_text
                s['buffer'] = []  # Reset buffer
                s['silence_backoff'] = BASE_SILENCE_TIMEOUT  # Reset backoff
            else:
                # Exponential backoff to prevent flip-flop
                s['silence_backoff'] = min(s['silence_backoff'] * 1.5, MAX_SILENCE_BACKOFF)

        s['timer'] = asyncio.create_task(check_silence())


async def metrics_loop():
    while True:
        print(f"Queue size: {audio_queue.qsize()}")
        await asyncio.sleep(10)