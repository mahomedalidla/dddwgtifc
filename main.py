from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import os
import ifcopenshell
import tempfile
import ezdxf
from supabase import create_client, Client

# Inicializa FastAPI
app = FastAPI()

# Configurar Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

BUCKET_NAME = "ifc-files"  # Asegúrate que este bucket exista en Supabase

# ---- Endpoint para leer DXF ----
@app.post("/upload-dxf")
async def upload_dxf(file: UploadFile = File(...)):
    if not file.filename.endswith(".dxf"):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos .dxf")
    
    tmp_dir = tempfile.mkdtemp()
    tmp_path = os.path.join(tmp_dir, file.filename)

    with open(tmp_path, "wb") as f:
        content = await file.read()
        f.write(content)

    try:
        doc = ezdxf.readfile(tmp_path)
        msp = doc.modelspace()

        lines = []
        polylines = []

        for e in msp:
            if e.dxftype() == 'LINE':
                lines.append({
                    "start": (e.dxf.start.x, e.dxf.start.y, e.dxf.start.z),
                    "end": (e.dxf.end.x, e.dxf.end.y, e.dxf.end.z)
                })
            elif e.dxftype() == 'LWPOLYLINE':
                points = [(p[0], p[1], 0) for p in e]
                polylines.append(points)

        return {
            "message": "Archivo DXF leído correctamente",
            "line_count": len(lines),
            "polyline_count": len(polylines),
            "lines": lines,
            "polylines": polylines
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error leyendo DXF: {str(e)}")

    finally:
        os.remove(tmp_path)
        os.rmdir(tmp_dir)


# ---- Endpoint para crear IFC y subirlo a Supabase ----
@app.get("/create-ifc")
def create_basic_ifc():
    try:
        # Crear modelo IFC básico
        model = ifcopenshell.file(schema="IFC4")
        project = model.create_entity("IfcProject", GlobalId=ifcopenshell.guid.new(), Name="ProyectoDemo")
        context = model.create_entity(
            "IfcGeometricRepresentationContext",
            ContextIdentifier="Body",
            ContextType="Model",
            CoordinateSpaceDimension=3,
            Precision=0.0001,
            WorldCoordinateSystem=model.create_entity("IfcAxis2Placement3D")
        )
        project.RepresentationContexts = [context]

        # Guardar IFC en archivo temporal
        ifc_path = "/tmp/basic_model.ifc"
        model.write(ifc_path)

        # Leer archivo IFC
        with open(ifc_path, "rb") as f:
            ifc_data = f.read()

        # Subir a Supabase
        file_name = f"basic_model.ifc"
        response = supabase.storage.from_(BUCKET_NAME).upload(file_name, ifc_data, {"content-type": "application/octet-stream", "upsert": True})

        # Generar URL pública
        public_url = supabase.storage.from_(BUCKET_NAME).get_public_url(file_name)

        os.remove(ifc_path)

        return {
            "message": "Archivo IFC creado y subido exitosamente",
            "public_url": public_url
        }

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})