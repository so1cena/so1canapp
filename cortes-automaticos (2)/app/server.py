"""
server.py
Servidor local (Flask) que serve a interface e roda o pipeline completo:
baixar -> transcrever -> escolher melhores momentos (IA local) -> cortar/legendar.

Rodar com: python app/server.py
Depois abrir: http://localhost:5000
"""

import os
import threading
import uuid

from flask import Flask, request, jsonify, send_from_directory

from downloader import baixar_video, DownloadError
from transcriber import transcrever
from highlighter import escolher_melhores_momentos, HighlighterError
from cutter import cortar_clipe, CutterError, OUTPUT_DIR

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

app = Flask(__name__, static_folder=STATIC_DIR, static_url_path="")

# Guarda o progresso/resultado de cada job em memória (uso local, um usuário só)
JOBS = {}


def _rodar_pipeline(job_id, url):
    def progresso(msg):
        JOBS[job_id]["status"] = msg

    try:
        caminho_video = baixar_video(url, progresso)
        segmentos = transcrever(caminho_video, progresso)
        momentos = escolher_melhores_momentos(segmentos, progresso)

        clipes = []
        for i, momento in enumerate(momentos, start=1):
            caminho = cortar_clipe(caminho_video, momento, segmentos, i, progresso)
            clipes.append({
                "arquivo": os.path.basename(caminho),
                "titulo": momento.get("titulo", f"Clipe {i}"),
                "inicio": momento["inicio"],
                "fim": momento["fim"],
            })

        JOBS[job_id]["status"] = "Concluído!"
        JOBS[job_id]["clipes"] = clipes
        JOBS[job_id]["concluido"] = True

    except (DownloadError, HighlighterError, CutterError) as e:
        JOBS[job_id]["erro"] = str(e)
        JOBS[job_id]["concluido"] = True
    except Exception as e:
        JOBS[job_id]["erro"] = f"Erro inesperado: {e}"
        JOBS[job_id]["concluido"] = True


@app.route("/")
def index():
    return send_from_directory(STATIC_DIR, "index.html")


@app.route("/api/gerar-cortes", methods=["POST"])
def gerar_cortes():
    dados = request.get_json(force=True)
    url = (dados or {}).get("url", "").strip()

    if not url:
        return jsonify({"erro": "Cole uma URL válida."}), 400

    job_id = str(uuid.uuid4())
    JOBS[job_id] = {"status": "Iniciando...", "concluido": False, "erro": None, "clipes": []}

    thread = threading.Thread(target=_rodar_pipeline, args=(job_id, url), daemon=True)
    thread.start()

    return jsonify({"job_id": job_id})


@app.route("/api/status/<job_id>")
def status(job_id):
    job = JOBS.get(job_id)
    if not job:
        return jsonify({"erro": "Job não encontrado."}), 404
    return jsonify(job)


@app.route("/clipes/<path:nome_arquivo>")
def servir_clipe(nome_arquivo):
    return send_from_directory(OUTPUT_DIR, nome_arquivo)


if __name__ == "__main__":
    print("\n Cortes Automáticos rodando em: http://localhost:5000\n")
    app.run(host="127.0.0.1", port=5000, debug=False)
