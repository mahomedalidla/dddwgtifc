from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
import os, tempfile, shutil

from parse_dxf import extract_entities
from generate_ifc import create_ifc_from_entities
from supabase import create_client
from dotenv import load_dotenv

# Cargar variables de entorno (en Railway deben estar configuradas)
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "ifc-files")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI()

@app.post("/convert")
async def convert_file(
    file: UploadFile = File(...),
    units: str = Form("mm"),
    wall_height: float = Form(3000.0),
    layers: str = Form("WALLS,DOORS,WINDOWS")
):
    """
    Convierte un archivo DXF a IFC, lo guarda en Supabase y devuelve un enlace firmado.
    """
    if not file.filename.lower().endswith(".dxf"):
        raise HTTPException(status_code=400, detail="Por ahora solo se aceptan archivos .dxf")

    tmp_dir = tempfile.mkdtemp()
    tmp_path = os.path.join(tmp_dir, file.filename)

    try:
        # Guardar archivo temporal
        with open(tmp_path, "wb") as f:
            f.write(await file.read())

        # Extraer entidades del DXF
        target_layers = [l.strip() for l in layers.split(",")]
        entities = extract_entities(tmp_path, target_layers)

        if not entities:
            raise HTTPException(status_code=400, detail="No se encontraron entidades en las capas especificadas")

        # Generar IFC
        out_ifc = os.path.join(tmp_dir, "modelo.ifc")
        create_ifc_from_entities(entities, out_ifc, wall_height, units)

        # Subir IFC a Supabase
        supabase_path = f"{os.path.splitext(file.filename)[0]}.ifc"
        with open(out_ifc, "rb") as f:
            supabase.storage.from_(SUPABASE_BUCKET).upload(supabase_path, f, {"upsert": True})

        # Crear URL firmada (1 hora)
        signed_url = supabase.storage.from_(SUPABASE_BUCKET).create_signed_url(supabase_path, 3600)

        return JSONResponse(content={
            "message": "Conversión exitosa",
            "ifc_url": signed_url["signedURL"]
        })

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando archivo: {str(e)}")
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

@app.get("/")
def root():
    return {"message": "API DXF → IFC lista con Supabase", "status": "ok"}