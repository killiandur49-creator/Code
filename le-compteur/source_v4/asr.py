import sys, wave, numpy as np, sherpa_onnx
M = "/tmp/claude-0/-home-user-Code/15234d1e-2166-55a3-99cd-98630da7c6b2/scratchpad/dl/asr/sherpa-onnx-whisper-base/"
def load(p):
    w = wave.open(p); sr = w.getframerate(); x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    if w.getnchannels() == 2: x = x.reshape(-1, 2).mean(1)
    return x, sr
def recognizer(lang=""):
    return sherpa_onnx.OfflineRecognizer.from_whisper(encoder=M + "base-encoder.int8.onnx", decoder=M + "base-decoder.int8.onnx", tokens=M + "base-tokens.txt",
                                                      language=lang, task="transcribe", num_threads=4)
if __name__ == "__main__":
    path = sys.argv[1]; lang = sys.argv[2] if len(sys.argv) > 2 else ""; step = float(sys.argv[3]) if len(sys.argv) > 3 else 15
    x, sr = load(path); rec = recognizer(lang)
    n = int(step * sr)
    for i in range(0, len(x), n):
        s = rec.create_stream(); s.accept_waveform(sr, x[i:i + n]); rec.decode_stream(s)
        print(f"[{i / sr:6.1f}] {s.result.text.strip()}  ({getattr(s.result, 'lang', '')})")
