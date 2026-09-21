"""
highlighter.py
Usa o Ollama (IA rodando local, grátis) pra ler a transcrição e escolher os
melhores trechos para virarem clipes curtos.

Pré-requisito: ter o Ollama instalado e rodando (https://ollama.com) com o
modelo baixado, ex: `ollama pull llama3.2`.
"""

import json
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODELO_PADRAO = "llama3.2"

DURACAO_MIN_CLIPE = 20   # segundos
DURACAO_MAX_CLIPE = 90   # segundos


class HighlighterError(Exception):
    pass


def _montar_prompt(segmentos):
    texto_com_tempo = "\n".join(
        f"[{s['start']:.1f}-{s['end']:.1f}] {s['text']}" for s in segmentos
    )

    return f"""Você é um editor de vídeo especialista em cortes virais para TikTok/Reels/Shorts.
Abaixo está a transcrição de uma live/podcast, com o tempo (em segundos) de cada fala.

Escolha entre 3 e 8 trechos que tenham mais potencial de viralizar como clipe curto
(momentos engraçados, polêmicos, emocionantes, ou com uma ideia completa e impactante).

Cada trecho deve durar entre {DURACAO_MIN_CLIPE} e {DURACAO_MAX_CLIPE} segundos.

Responda APENAS com um JSON válido, sem nenhum texto antes ou depois, no formato:
[{{"inicio": 12.3, "fim": 45.0, "titulo": "título curto e chamativo do clipe"}}]

Transcrição:
{texto_com_tempo}
"""


def escolher_melhores_momentos(segmentos, progress_callback=None, modelo=MODELO_PADRAO):
    if progress_callback:
        progress_callback("Pedindo pra IA local escolher os melhores momentos...")

    prompt = _montar_prompt(segmentos)

    try:
        resp = requests.post(
            OLLAMA_URL,
            json={"model": modelo, "prompt": prompt, "stream": False, "format": "json"},
            timeout=300,
        )
        resp.raise_for_status()
    except requests.exceptions.ConnectionError:
        raise HighlighterError(
            "Não consegui falar com o Ollama. Verifique se ele está instalado e "
            "rodando (abra o app Ollama ou rode 'ollama serve')."
        )

    texto_resposta = resp.json().get("response", "").strip()

    try:
        momentos = json.loads(texto_resposta)
    except json.JSONDecodeError:
        inicio = texto_resposta.find("[")
        fim = texto_resposta.rfind("]")
        if inicio == -1 or fim == -1:
            raise HighlighterError("A IA local não retornou um JSON válido.")
        momentos = json.loads(texto_resposta[inicio:fim + 1])

    momentos_validos = [
        m for m in momentos
        if isinstance(m, dict) and "inicio" in m and "fim" in m and m["fim"] > m["inicio"]
    ]

    if not momentos_validos:
        raise HighlighterError("A IA local não encontrou momentos válidos nesse vídeo.")

    if progress_callback:
        progress_callback(f"{len(momentos_validos)} momentos escolhidos.")

    return momentos_validos
