import shutil
from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from typing import List
from PyPDF2 import PdfMerger
import uuid
import os

app = FastAPI()

TEMP_DIR = "/tmp/pdf_merge"
os.makedirs(TEMP_DIR, exist_ok=True)
tasks_status = {}

def process_merge(task_id: str, files_paths: List[str]):
    """Junta os PDFs no background"""
    try:
        merger = PdfMerger()
        for path in files_paths:
            merger.append(path)

        output_path = os.path.join(TEMP_DIR, f"{task_id}.pdf")
        merger.write(output_path)
        merger.close()

        # Remove arquivos temporários
        for path in files_paths:
            os.remove(path)

        tasks_status[task_id] = "done"
    except Exception as e:
        tasks_status[task_id] = "error"
        print(f"[ERRO] Merge falhou: {e}")

@app.post("/merge-pdfs")
async def merge_pdfs(background_tasks: BackgroundTasks, files: List[UploadFile] = File(...)):
    task_id = str(uuid.uuid4())
    tasks_status[task_id] = "pending"
    file_paths = []

    # Salvar uploads em disco enquanto chegam
    for file in files:
        temp_path = os.path.join(TEMP_DIR, f"{uuid.uuid4()}.pdf")
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)  # grava direto, sem ler tudo na memória
        file_paths.append(temp_path)

    background_tasks.add_task(process_merge, task_id, file_paths)

    # Retorna imediatamente
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
