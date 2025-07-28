# generate_ifc.py
import ifcopenshell

def create_basic_ifc():
    # Crear un nuevo archivo IFC vacío
    modelo = ifcopenshell.file()

    # Guardar el archivo IFC en disco (o donde prefieras)
    ifc_path = "/tmp/modelo.ifc"  # en Railway puede ser /tmp para escritura
    modelo.write(ifc_path)

    return ifc_path
