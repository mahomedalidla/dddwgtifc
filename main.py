from fastapi import FastAPI, UploadFile, Form
import os

app = FastAPI()

@app.post("/convert")
async def convert(
    file: UploadFile,
    units: str = Form(...),
    wall_height: float = Form(...),
    layers: str = Form(...)
):
    # Guardar archivo
    os.makedirs("uploads", exist_ok=True)
    file_path = f"uploads/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Aquí iría la lógica de conversión (DWG → DXF → IFC)
    return {"message": "Archivo recibido", "path": file_path}
