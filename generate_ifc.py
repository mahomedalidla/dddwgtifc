import ifcopenshell
import ifcopenshell.api
import ifcopenshell.guid

def create_ifc_from_entities(entities, output_path, wall_height=3000.0, units="mm"):
    model = ifcopenshell.file(schema="IFC4")

    # Crear proyecto
    project = model.create_entity(
        "IfcProject",
        GlobalId=ifcopenshell.guid.new(),
        Name="Proyecto DXF a IFC"
    )

    # Crear contexto geométrico
    context = model.create_entity(
        "IfcGeometricRepresentationContext",
        ContextIdentifier="Body",
        ContextType="Model",
        CoordinateSpaceDimension=3,
        Precision=0.0001,
        WorldCoordinateSystem=model.create_entity("IfcAxis2Placement3D")
    )

    project.RepresentationContexts = [context]

    # Asignar unidades al proyecto (mm o metros)
    if units == "mm":
        length_unit = ifcopenshell.api.run("unit.create_si_unit", model, unit_type="LENGTHUNIT", name="MILLIMETRE")
    elif units == "m" or units == "meter" or units == "meters":
        length_unit = ifcopenshell.api.run("unit.create_si_unit", model, unit_type="LENGTHUNIT", name="METRE")
    else:
        # Por defecto milímetros
        length_unit = ifcopenshell.api.run("unit.create_si_unit", model, unit_type="LENGTHUNIT", name="MILLIMETRE")

    ifcopenshell.api.run("unit.assign_unit", model, units=[length_unit])

    # Crear unidad de medida para el proyecto
    ifcopenshell.api.run("project.assign_representation_context", model, product=project, context=context)

    # Crear elementos IfcWallStandardCase con geometría extruida
    for idx, entity in enumerate(entities):
        # Se espera que entity sea una lista de puntos [(x1,y1), (x2,y2), ...] que definen una polilínea cerrada
        # Crear IfcPolyline a partir de puntos 2D (z=0)
        points = [model.create_entity("IfcCartesianPoint", (float(x), float(y), 0.0)) for x, y in entity]
        polyline = model.create_entity("IfcPolyline", Points=points)

        # Crear IfcPolyLoop para definir la base del perfil
        poly_loop = model.create_entity("IfcPolyLoop", Polygon=points)

        # Crear IfcArbitraryClosedProfileDef con la polilínea
        profile = model.create_entity(
            "IfcArbitraryClosedProfileDef",
            ProfileType="AREA",
            OuterCurve=poly_loop
        )

        # Crear IfcExtrudedAreaSolid para extruir el perfil en Z (altura del muro)
        extruded_solid = model.create_entity(
            "IfcExtrudedAreaSolid",
            SweptArea=profile,
            Position=model.create_entity("IfcAxis2Placement3D"),
            ExtrudedDirection=model.create_entity("IfcDirection", (0.0, 0.0, 1.0)),
            Depth=wall_height
        )

        # Crear IfcShapeRepresentation para la geometría
        shape_representation = model.create_entity(
            "IfcShapeRepresentation",
            ContextOfItems=context,
            RepresentationIdentifier="Body",
            RepresentationType="SweptSolid",
            Items=[extruded_solid]
        )

        # Crear IfcProductDefinitionShape para asignar la representación
        product_def_shape = model.create_entity(
            "IfcProductDefinitionShape",
            Representations=[shape_representation]
        )

        # Crear muro con geometría
        wall = model.create_entity(
            "IfcWallStandardCase",
            GlobalId=ifcopenshell.guid.new(),
            Name=f"Wall_{idx}",
            Representation=product_def_shape
        )
        model.add(wall)

    # Escribir archivo IFC de salida
    model.write(output_path)

# Comentarios:
# - 'entities' debe ser una lista de polilíneas, cada una definida como lista de tuplas (x,y).
# - El muro se extruye en dirección Z con altura 'wall_height' (en las unidades definidas).
# - Se asignan unidades al proyecto (mm o metros).
# - El archivo IFC se escribe en 'output_path'.
# - Este código puede usarse en entornos como Railway y con archivos almacenados en Supabase.