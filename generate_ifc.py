import ifcopenshell.api
import os

def create_basic_ifc(output_path="outputs/model.ifc"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    model = ifcopenshell.api.run("model.create_empty")
    ifcopenshell.api.run("unit.assign_unit", model, units=["METERS"])

    # Crea un muro dummy (más adelante usaremos coordenadas reales)
    wall = ifcopenshell.api.run("root.create_entity", model, {"type": "IfcWall"})
    ifcopenshell.api.run("aggregate.assign_object", model, {
        "products": [wall],
        "aggregates": [model.by_type("IfcProject")[0]]
    })

    model.write(output_path)
    return output_path
