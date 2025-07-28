import ezdxf

def extract_entities(dxf_path, target_layers):
    doc = ezdxf.readfile(dxf_path)
    msp = doc.modelspace()
    walls = []

    for entity in msp:
        if entity.dxf.layer in target_layers:
            if entity.dxftype() in ["LINE", "LWPOLYLINE"]:
                start = entity.dxf.start if entity.dxftype() == "LINE" else None
                end = entity.dxf.end if entity.dxftype() == "LINE" else None
                walls.append({
                    "type": entity.dxftype(),
                    "layer": entity.dxf.layer,
                    "start": (start.x, start.y) if start else None,
                    "end": (end.x, end.y) if end else None
                })

    return walls
