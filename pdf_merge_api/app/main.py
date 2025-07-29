from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from typing import List
import os
from PyPDF2 import PdfMerger
import uuid

app = FastAPI()

@app.post("/merge-pdfs")
async def merge_pdfs(files: List[UploadFile] = File(...)):
    merger = PdfMerger()
    temp_files = []

    for file in files:
        temp_path = f"/tmp/{uuid.uuid4()}.pdf"
        with open(temp_path, "wb") as f:
            f.write(await file.read())
        merger.append(temp_path)
        temp_files.append(temp_path)

    output_path = "/tmp/merged_output.pdf"
    merger.write(output_path)
    merger.close()

    for temp_file in temp_files:
        os.remove(temp_file)

    return FileResponse(output_path, filename="merged.pdf", media_type="application/pdf")