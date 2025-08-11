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

    # Asignar unidades al proyecto
    unit_assignment = model.create_entity("IfcUnitAssignment")
    project.UnitsInContext = unit_assignment

    # Crear y asignar las unidades basicas
    length_unit = model.create_entity("IfcSIUnit", UnitType="LENGTHUNIT", Name="METRE")
    area_unit = model.create_entity("IfcSIUnit", UnitType="AREAUNIT", Name="SQUARE_METRE")
    volume_unit = model.create_entity("IfcSIUnit", UnitType="VOLUMEUNIT", Name="CUBIC_METRE")
    plane_angle_unit = model.create_entity("IfcSIUnit", UnitType="PLANEANGLEUNIT", Name="RADIAN")
    
    unit_assignment.Units = [length_unit, area_unit, volume_unit, plane_angle_unit]

    # Configurar la unidad de longitud segun el parametro 'units'
    if units == "mm":
        length_unit.Prefix = "MILLI"
    # 'm' es el default de IfcSIUnit, no se necesita hacer nada

    

    # Crear elementos IfcWallStandardCase con geometría extruida
    for idx, entity in enumerate(entities):
        # Omitir geometrías que no son polígonos cerrados (necesitan al menos 3 vértices)
        if len(entity) < 3:
            continue
        # Se espera que entity sea una lista de puntos [(x1,y1), (x2,y2), ...] que definen una polilínea cerrada
        # Crear IfcPolyline a partir de puntos 2D (z=0)
        points = [model.create_entity("IfcCartesianPoint", (float(x), float(y), 0.0)) for x, y in entity]
        polyline = model.create_entity("IfcPolyline", Points=points)

        # Para IfcPolyLoop, la lista de puntos debe estar explícitamente cerrada.
        loop_points = list(points)
        if loop_points[0].Coordinates != loop_points[-1].Coordinates:
            loop_points.append(loop_points[0])

        # Crear IfcPolyLoop para definir la base del perfil
        poly_loop = model.create_entity("IfcPolyLoop", Polygon=loop_points)

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

        # Crear la ubicación del muro en el espacio del proyecto
        placement = model.create_entity("IfcLocalPlacement")

        # Crear muro con geometría
        wall = model.create_entity(
            "IfcWallStandardCase",
            GlobalId=ifcopenshell.guid.new(),
            Name=f"Wall_{idx}",
            ObjectPlacement=placement,
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