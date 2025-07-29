from fastapi import FastAPI, UploadFile, File, HTTPException
import ezdxf
import tempfile
import os
import ifcopenshell
import ifcopenshell.util.element
import ifcopenshell.util.unit
import uuid

app = FastAPI()

@app.post("/upload-dxf")
async def upload_dxf(file: UploadFile = File(...)):
    # Validar que sea DXF
    if not file.filename.endswith(".dxf"):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos .dxf")
    
    # Guardar archivo temporal
    tmp_dir = tempfile.mkdtemp()
    tmp_path = os.path.join(tmp_dir, file.filename)

    with open(tmp_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # Leer DXF con ezdxf
    try:
        doc = ezdxf.readfile(tmp_path)
        msp = doc.modelspace()

        # Extraer líneas y polilíneas
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

        # Aquí podrías guardar estos datos para usarlos después en IFC

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
        # Limpiar archivo temporal
        os.remove(tmp_path)
        os.rmdir(tmp_dir)

@app.get("/create-ifc")
def create_basic_ifc():
    try:
        # Crear modelo vacío
        model = ifcopenshell.file(schema="IFC4")

        # Añadir entidades mínimas requeridas
        project = model.create_entity("IfcProject", GlobalId=ifcopenshell.guid.new(), Name="ProyectoDemo")
        context = model.create_entity("IfcGeometricRepresentationContext", ContextIdentifier="Body", ContextType="Model", CoordinateSpaceDimension=3, Precision=0.0001, WorldCoordinateSystem=model.create_entity("IfcAxis2Placement3D"))
        unit_assignment = ifcopenshell.util.unit.assign_unit(model, length_units="METERS")

        model.create_entity("IfcUnitAssignment", Units=unit_assignment)

        model.create_entity("IfcProjectLibrary", GlobalId=ifcopenshell.guid.new(), Name="LibreríaDemo")
        model.create_entity("IfcRelDefinesByProperties", GlobalId=ifcopenshell.guid.new(), Name="RelacionDemo")

        project.RepresentationContexts = [context]
        project.UnitsInContext = unit_assignment

        # Guardar en archivo temporal
        ifc_path = "/tmp/basic_model.ifc"
        model.write(ifc_path)

        # Leer archivo IFC para mostrar respuesta
        with open(ifc_path, "rb") as f:
            data = f.read()

        os.remove(ifc_path)

        return {
            "message": "Archivo IFC creado exitosamente (modo clásico)",
            "ifc_file_size_bytes": len(data)
        }

    except Exception as e:
        return {"error": str(e)}