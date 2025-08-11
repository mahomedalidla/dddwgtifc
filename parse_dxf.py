import ezdxf

def extract_entities(dxf_path, target_layers):
    """
    Lee un DXF y extrae polilíneas/líneas de las capas indicadas.
    Devuelve lista de polilíneas: cada polilínea es lista de tuplas (x, y).
    """
    doc = ezdxf.readfile(dxf_path)
    msp = doc.modelspace()

    target_layers_upper = [l.upper() for l in target_layers]
    polylines = []

    for entity in msp:
        layer_name = entity.dxf.layer.upper()

        if layer_name not in target_layers_upper:
            continue

        if entity.dxftype() == "LINE":
            start = entity.dxf.start
            end = entity.dxf.end
            polyline = [
                (float(start.x), float(start.y)),
                (float(end.x), float(end.y))
            ]
            polylines.append(polyline)

        elif entity.dxftype() == "LWPOLYLINE":
            pts = []
            for p in entity.get_points():
                pts.append((float(p[0]), float(p[1])))
            if pts:
                polylines.append(pts)

        elif entity.dxftype() == "POLYLINE":
            pts = []
            for v in entity.vertices:
                pts.append((float(v.dxf.location.x), float(v.dxf.location.y)))
            if pts:
                polylines.append(pts)

    return polylines