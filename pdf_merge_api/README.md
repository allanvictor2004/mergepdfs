# PDF Merge API

Esta API consolida múltiplos arquivos PDF em um único documento.

## Como usar localmente

```bash
pip install -r app/requirements.txt
uvicorn app.main:app --reload
```

Acesse em: http://127.0.0.1:8000/docs

## Implantação (Railway)

1. Crie um novo projeto em https://railway.app
2. Conecte este repositório.
3. Configure como serviço web:
   - Comando: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Porta: 8000