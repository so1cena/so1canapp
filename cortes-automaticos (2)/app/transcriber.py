"""
transcriber.py
Transcreve o áudio do vídeo localmente usando faster-whisper (sem custo,
sem enviar nada pra internet). Detecta GPU automaticamente e cai pra CPU
se não tiver.
"""

from faster_whisper import WhisperModel

_modelo = None


def _carregar_modelo():
    global _modelo
    if _modelo is not None:
        return _modelo

    device = "cpu"
    compute_type = "int8"
    try:
        import torch
        if torch.cuda.is_available():
            device = "cuda"
            compute_type = "float16"
    except ImportError:
        pass

    # "small" é um bom equilíbrio entre velocidade e qualidade pra CPU/GPU comuns.
    # Troque para "medium" ou "large-v3" se tiver GPU forte e quiser mais precisão.
    _modelo = WhisperModel("small", device=device, compute_type=compute_type)
    return _modelo


def transcrever(caminho_video: str, progress_callback=None):
    """
    Retorna uma lista de segmentos:
    [{"start": 0.0, "end": 3.2, "text": "...", "words": [{"start":..,"end":..,"word":".."}]}]
    """
    if progress_callback:
        progress_callback("Transcrevendo áudio (isso pode demorar alguns minutos)...")

    modelo = _carregar_modelo()

    segmentos, _info = modelo.transcribe(
        caminho_video,
        language="pt",
        word_timestamps=True,
        vad_filter=True,
    )

    resultado = []
    for seg in segmentos:
        palavras = []
        if seg.words:
            for w in seg.words:
                palavras.append({"start": w.start, "end": w.end, "word": w.word})
        resultado.append({
            "start": seg.start,
            "end": seg.end,
            "text": seg.text.strip(),
            "words": palavras,
        })

    if progress_callback:
        progress_callback("Transcrição concluída.")

    return resultado
