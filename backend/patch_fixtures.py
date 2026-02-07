import json
import os
from datetime import datetime

timestamp = datetime.now().isoformat()

files_to_patch = [
    'catalogo/fixtures/marcas_populares.json',
    'catalogo/fixtures/initial_data.json',
    'productos/fixtures/unidades_medida.json',
    'flota/fixtures/tipos_vehiculos.json',
    'tareas/fixtures/initial_setup.json'
]

def patch_file(filepath):
    full_path = os.path.join(os.getcwd(), filepath)
    if not os.path.exists(full_path):
        print(f"File not found: {full_path}")
        return

    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        updated = False
        for item in data:
            fields = item.setdefault('fields', {})
            if 'created_at' not in fields:
                fields['created_at'] = timestamp
                updated = True
            if 'updated_at' not in fields:
                fields['updated_at'] = timestamp
                updated = True
            # Also handle deleted_at for SoftDeleteModel if needed (usually null is fine if we don't include it?)
            # But let's check if we need to include deleted_at=null explicitly
            # Django deserializer usually handles missing nullable fields as None.
            # But TimeStampedModel fields are NOT NULL.

        if updated:
            with open(full_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"Patched {filepath}")
        else:
            print(f"No changes needed for {filepath}")

    except Exception as e:
        print(f"Error patching {filepath}: {e}")

if __name__ == '__main__':
    for f in files_to_patch:
        patch_file(f)
