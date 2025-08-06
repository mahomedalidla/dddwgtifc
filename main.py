import ifcopenshell
import ifcopenshell.util.unit
import os

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