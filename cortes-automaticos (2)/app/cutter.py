"""
cutter.py
Corta os trechos escolhidos, transforma em vertical (9:16) e queima legenda
dinâmica (palavra por palavra, estilo karaokê) usando ffmpeg.
"""

import os
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
TEMP_DIR = os.path.join(BASE_DIR, "temp")

os.makedirs(OUTPUT_DIR, exist_ok=True)


class CutterError(Exception):
    pass


def _segundos_para_ass(t: float) -> str:
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t % 60
    return f"{h:d}:{m:02d}:{s:05.2f}"


def _gerar_legenda_ass(palavras, offset: float, caminho_ass: str):
    """Gera um arquivo .ass com legenda dinâmica (destaca a palavra atual)."""
    cabecalho = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial Black,72,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,4,2,2,60,60,180,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    linhas = []
    for palavra in palavras:
        inicio = max(0.0, palavra["start"] - offset)
        fim = max(0.0, palavra["end"] - offset)
        if fim <= inicio:
            continue
        texto = palavra["word"].strip().upper().replace("\n", " ")
        linhas.append(
            f"Dialogue: 0,{_segundos_para_ass(inicio)},{_segundos_para_ass(fim)},"
            f"Default,,0,0,0,,{texto}"
        )

    with open(caminho_ass, "w", encoding="utf-8") as f:
        f.write(cabecalho)
        f.write("\n".join(linhas))


def cortar_clipe(caminho_video: str, momento: dict, todos_segmentos: list, indice: int,
                  progress_callback=None) -> str:
    """
    Corta um clipe vertical com legenda dinâmica queimada.
    momento: {"inicio": float, "fim": float, "titulo": str}
    Retorna o caminho do arquivo final .mp4
    """
    inicio = float(momento["inicio"])
    fim = float(momento["fim"])
    duracao = fim - inicio

    if progress_callback:
        progress_callback(f"Cortando clipe {indice}: {momento.get('titulo', '')}")

    # Junta só as palavras que caem dentro desse intervalo
    palavras_do_clipe = []
    for seg in todos_segmentos:
        for w in seg.get("words", []):
            if inicio <= w["start"] <= fim:
                palavras_do_clipe.append(w)

    ass_path = os.path.join(TEMP_DIR, f"clipe_{indice}.ass")
    _gerar_legenda_ass(palavras_do_clipe, inicio, ass_path)

    nome_saida = f"clipe_{indice:02d}.mp4"
    caminho_saida = os.path.join(OUTPUT_DIR, nome_saida)

    # crop centralizado pra 9:16 + escala pra 1080x1920 + queima a legenda .ass
    ass_path_ffmpeg = ass_path.replace("\\", "/").replace(":", "\\:")
    filtro = (
        "crop='min(iw,ih*9/16)':'ih':(iw-min(iw,ih*9/16))/2:0,"
        "scale=1080:1920,"
        f"subtitles='{ass_path_ffmpeg}'"
    )

    comando = [
        "ffmpeg", "-y",
        "-ss", str(inicio),
        "-i", caminho_video,
        "-t", str(duracao),
        "-vf", filtro,
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-c:a", "aac", "-b:a", "160k",
        caminho_saida,
    ]

    processo = subprocess.run(comando, capture_output=True, text=True,
                               encoding="utf-8", errors="ignore")

    if processo.returncode != 0:
        raise CutterError(f"Falha ao cortar o clipe {indice}: {processo.stderr[-500:]}")

    return caminho_saida
