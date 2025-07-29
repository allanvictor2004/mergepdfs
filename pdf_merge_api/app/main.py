# from fastapi import FastAPI, UploadFile, File
# from fastapi.responses import FileResponse
# from typing import List
# import os
# from PyPDF2 import PdfMerger
# import uuid

# app = FastAPI()

# @app.post("/merge-pdfs")
# async def merge_pdfs(files: List[UploadFile] = File(...)):
#     merger = PdfMerger()
#     temp_files = []

#     for file in files:
#         temp_path = f"/tmp/{uuid.uuid4()}.pdf"
#         with open(temp_path, "wb") as f:
#             f.write(await file.read())
#         merger.append(temp_path)
#         temp_files.append(temp_path)

#     output_path = "/tmp/merged_output.pdf"
#     merger.write(output_path)
#     merger.close()

#     for temp_file in temp_files:
#         os.remove(temp_file)

#     return FileResponse(output_path, filename="merged.pdf", media_type="application/pdf")

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse
from typing import List
from PyPDF2 import PdfMerger
import io

app = FastAPI()

@app.post("/merge-pdfs")
async def merge_pdfs(files: List[UploadFile] = File(...)):
    merger = PdfMerger()

    # Adiciona os arquivos diretamente do upload ao merger
    for file in files:
        file_content = await file.read()
        merger.append(io.BytesIO(file_content))

    # Escreve o PDF consolidado em memória (BytesIO)
    output_pdf = io.BytesIO()
    merger.write(output_pdf)
    merger.close()
    output_pdf.seek(0)  # Move para o início do arquivo

    return StreamingResponse(
        output_pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=merged.pdf"}
    )