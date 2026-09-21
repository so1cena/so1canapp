"""
downloader.py
Baixa o vídeo/live/podcast a partir de uma URL do YouTube ou Twitch usando yt-dlp.

Por que cookies.txt e não --cookies-from-browser:
navegadores recentes (Chrome/Edge) usam uma criptografia de cookies que o
yt-dlp nem sempre consegue ler direto do navegador, mesmo com ele fechado.
Usar um arquivo cookies.txt exportado manualmente é mais estável.
"""

import os
import subprocess
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COOKIES_PATH = os.path.join(BASE_DIR, "..", "cookies.txt")
TEMP_DIR = os.path.join(BASE_DIR, "temp")

os.makedirs(TEMP_DIR, exist_ok=True)


class DownloadError(Exception):
    pass


def baixar_video(url: str, progress_callback=None) -> str:
    """
    Baixa o vídeo da URL informada e retorna o caminho do arquivo .mp4 salvo.
    progress_callback(mensagem: str) é chamado para reportar progresso.
    """
    saida_template = os.path.join(TEMP_DIR, "%(id)s.%(ext)s")

    comando = [
        "yt-dlp",
        "-f", "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
        "--merge-output-format", "mp4",
        "-o", saida_template,
        "--no-playlist",
        "--print", "after_move:filepath",
        url,
    ]

    # Só usa cookies.txt se o arquivo existir (vídeos públicos não precisam)
    if os.path.exists(COOKIES_PATH):
        comando.insert(1, "--cookies")
        comando.insert(2, COOKIES_PATH)

    if progress_callback:
        progress_callback("Baixando vídeo...")

    processo = subprocess.run(
        comando,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore",
    )

    if processo.returncode != 0:
        erro = processo.stderr.strip().splitlines()[-1] if processo.stderr else "erro desconhecido"

        if "Sign in to confirm" in processo.stderr or "cookies" in processo.stderr.lower():
            raise DownloadError(
                "Este vídeo pede login no YouTube. Exporte um cookies.txt atualizado "
                "(extensão 'Get cookies.txt LOCALLY') e salve como cookies.txt na pasta "
                "principal do projeto."
            )
        raise DownloadError(f"Falha ao baixar o vídeo: {erro}")

    caminho_arquivo = processo.stdout.strip().splitlines()[-1]

    if not os.path.exists(caminho_arquivo):
        raise DownloadError("O download terminou mas o arquivo não foi encontrado.")

    if progress_callback:
        progress_callback("Download concluído.")

    return caminho_arquivo
