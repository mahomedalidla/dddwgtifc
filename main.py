from fastapi import FastAPI, UploadFile, File
from generate_ifc import create_basic_ifc
import shutil

app = FastAPI()

@app.post("/convert")
async def convert(file: UploadFile = File(...)):
    # Guarda el archivo recibido (si quieres, para procesamiento futuro)
    temp_path = f"/tmp/{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Llama a la función para crear IFC
    ifc_path = create_basic_ifc()

    # Lee el IFC creado y devuélvelo como respuesta (opcional)
    with open(ifc_path, "rb") as f:
        data = f.read()

    return {
        "message": "Archivo IFC creado exitosamente",
        "ifc_file_size_bytes": len(data),
    }
