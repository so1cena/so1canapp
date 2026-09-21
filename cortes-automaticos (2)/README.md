# 🎬 Cortes Automáticos

Cole a URL de uma live/podcast (YouTube ou Twitch) e deixe uma IA rodando
**100% local e grátis** no seu PC encontrar os melhores momentos e transformá-los
em clipes verticais prontos pra Shorts/Reels/TikTok, com legenda dinâmica queimada.

Nada é enviado para nenhum servidor externo — tudo roda na sua própria máquina.

## ✅ Requisitos (Windows)

- [Python 3.11](https://www.python.org/downloads/) — marque **"Add python.exe to PATH"** ao instalar
- [ffmpeg](https://www.gyan.dev/ffmpeg/builds/) — baixe a versão "release essentials", extraia e adicione a pasta `bin` ao PATH do Windows
- [Ollama](https://ollama.com/download) — IA local que escolhe os melhores momentos

## 📥 Instalação

1. Baixe este repositório (botão verde **Code → Download ZIP**) e extraia numa pasta
2. Dê duplo clique em **`install.bat`** e espere terminar
3. Dê duplo clique em **`run.bat`**
4. Seu navegador abre automaticamente em `http://localhost:5000`

## 🍪 Vídeos que pedem login

Alguns vídeos (lives fechadas, conteúdo de membros) exigem estar logado no
YouTube pra baixar. Se aparecer esse erro:

1. Instale a extensão **"Get cookies.txt LOCALLY"** no seu navegador
2. Faça login no YouTube normalmente
3. Clique na extensão e exporte os cookies de `youtube.com`
4. Salve o arquivo baixado como **`cookies.txt`** na pasta principal deste projeto (mesma pasta do `install.bat`)

> ⚠️ **Nunca compartilhe seu `cookies.txt` com ninguém.** Ele equivale à senha
> da sua conta Google. O `.gitignore` deste projeto já impede que ele seja
> enviado pro GitHub por engano.

## 🛠️ Como funciona por dentro

1. **`yt-dlp`** baixa o vídeo
2. **`faster-whisper`** transcreve o áudio localmente
3. **Ollama** (IA local) lê a transcrição e escolhe os melhores trechos
4. **`ffmpeg`** corta, deixa vertical (9:16) e queima a legenda dinâmica

## 📁 Estrutura do projeto

```
cortes-automaticos/
├── install.bat          # instalador (rodar 1x)
├── run.bat               # abre a ferramenta
├── requirements.txt
├── cookies.txt           # você cria esse (não incluso)
└── app/
    ├── server.py         # servidor local
    ├── downloader.py     # baixa o vídeo
    ├── transcriber.py    # transcreve o áudio
    ├── highlighter.py    # escolhe os melhores momentos (IA)
    ├── cutter.py          # corta e legenda os clipes
    └── static/index.html # interface
```

## ⚠️ Uso responsável

Baixe apenas vídeos que você tem permissão para usar (seus próprios ou com
autorização). Respeite os termos de uso do YouTube/Twitch e os direitos
autorais de terceiros.
