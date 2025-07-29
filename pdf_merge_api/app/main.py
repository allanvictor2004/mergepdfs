from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from typing import List
from PyPDF2 import PdfMerger
import uuid
import os
import io

app = FastAPI()

# Pasta temporária para salvar PDFs
TEMP_DIR = "/tmp/pdf_merge"
os.makedirs(TEMP_DIR, exist_ok=True)

tasks_status = {}  # {task_id: "pending" | "done" | "error"}

def process_merge(task_id: str, files_content: List[bytes]):
    """Função que faz o merge em segundo plano."""
    try:
        merger = PdfMerger()
        for content in files_content:
            merger.append(io.BytesIO(content))

        output_path = os.path.join(TEMP_DIR, f"{task_id}.pdf")
        with open(output_path, "wb") as f:
            merger.write(f)

        merger.close()
        tasks_status[task_id] = "done"
    except Exception as e:
        tasks_status[task_id] = "error"
        print(f"Erro no merge: {e}")

@app.post("/merge-pdfs")
async def merge_pdfs(background_tasks: BackgroundTasks, files: List[UploadFile] = File(...)):
    # Gera um ID único para a tarefa
    task_id = str(uuid.uuid4())
    tasks_status[task_id] = "pending"

    # Lê os arquivos (conteúdo em memória)
    files_content = [await file.read() for file in files]

    # Chama o processamento em background
    background_tasks.add_task(process_merge, task_id, files_content)

    return {"task_id": task_id, "status": "pending", "download_url": f"/download/{task_id}"}

@app.get("/status/{task_id}")
async def check_status(task_id: str):
    status = tasks_status.get(task_id)
    if not status:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    return {"task_id": task_id, "status": status}

@app.get("/download/{task_id}")
async def download_file(task_id: str):
    status = tasks_status.get(task_id)
    if not status:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    if status != "done":
        return JSONResponse({"message": "Arquivo ainda não está pronto. Verifique o status."})

    output_path = os.path.join(TEMP_DIR, f"{task_id}.pdf")
    if not os.path.exists(output_path):
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")

    return FileResponse(output_path, filename="merged.pdf", media_type="application/pdf")
