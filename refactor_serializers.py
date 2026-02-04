"""
Script de Refactorización Automática de Serializers
Migra todos los serializers a heredar de las clases base de core
"""
import re
import sys
from pathlib import Path


def refactor_serializer_file(file_path):
    """Refactoriza un archivo de serializers para usar clases base de core"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # 1. Agregar import de core.serializers si no existe
    if 'from core.serializers import' not in content:
        # Encontrar la línea de imports de rest_framework
        import_pattern = r'(from rest_framework import serializers)'
        replacement = r'\1\nfrom core.serializers import BaseModelSerializer, SoftDeleteSerializer'
        content = re.sub(import_pattern, replacement, content)
    
    # 2. Refactorizar serializers que heredan de serializers.ModelSerializer
    # Patrón: class XSerializer(serializers.ModelSerializer):
    
    # Primero, identificar si el modelo tiene soft delete mirando los fields
    # Por ahora, asumiremos que todos pueden heredar de BaseModelSerializer
    # y los que tienen deleted_at de SoftDeleteSerializer
    
    # Patrón para encontrar clases de serializers
    class_pattern = r'class\s+(\w+Serializer)\(serializers\.ModelSerializer\):'
    
    def replace_class(match):
        class_name = match.group(1)
        # Por defecto usar BaseModelSerializer
        return f'class {class_name}(BaseModelSerializer):'
    
    content = re.sub(class_pattern, replace_class, content)
    
    # 3. Actualizar Meta classes para heredar de BaseModelSerializer.Meta
    # Patrón: class Meta:\n        model = 
    meta_pattern = r'(class\s+\w+Serializer\([^)]+\):.*?)(class Meta:)'
    
    def replace_meta(match):
        serializer_def = match.group(1)
        meta_class = match.group(2)
        
        # Determinar qué clase base se está usando
        if 'BaseModelSerializer' in serializer_def:
            return f'{serializer_def}class Meta(BaseModelSerializer.Meta):'
        elif 'SoftDeleteSerializer' in serializer_def:
            return f'{serializer_def}class Meta(SoftDeleteSerializer.Meta):'
        else:
            return match.group(0)
    
    content = re.sub(meta_pattern, replace_meta, content, flags=re.DOTALL)
    
    # 4. Actualizar fields en Meta para incluir campos base
    # Buscar patterns como fields = ['id', 'name', ...]
    # y reemplazar con fields = BaseModelSerializer.Meta.fields + ['name', ...]
    
    def update_fields(match):
        indent = match.group(1)
        fields_content = match.group(2)
        
        # Si ya incluye BaseModelSerializer.Meta.fields, no hacer nada
        if 'BaseModelSerializer.Meta.fields' in fields_content or 'SoftDeleteSerializer.Meta.fields' in fields_content:
            return match.group(0)
        
        # Si es fields = '__all__', dejarlo como está
        if "'__all__'" in fields_content or '"__all__"' in fields_content:
            return match.group(0)
        
        # Si es una lista de campos
        if fields_content.strip().startswith('['):
            # Remover 'id' si está presente (ya está en base)
            fields_content_clean = re.sub(r"'id',?\s*", '', fields_content)
            fields_content_clean = re.sub(r'"id",?\s*', '', fields_content_clean)
            
            # Determinar qué clase base usar (por defecto BaseModelSerializer)
            base_class = 'BaseModelSerializer'
            
            return f'{indent}fields = {base_class}.Meta.fields + {fields_content_clean}'
        
        return match.group(0)
    
    # Patrón para fields
    fields_pattern = r'(\s+)fields\s*=\s*(\[[\s\S]*?\]|\'__all__\'|"__all__")'
    content = re.sub(fields_pattern, update_fields, content)
    
    # 5. Actualizar read_only_fields para incluir campos base
    def update_readonly_fields(match):
        indent = match.group(1)
        fields_content = match.group(2)
        
        # Si ya incluye BaseModelSerializer.Meta.read_only_fields, no hacer nada
        if 'BaseModelSerializer.Meta.read_only_fields' in fields_content or 'SoftDeleteSerializer.Meta.read_only_fields' in fields_content:
            return match.group(0)
        
        # Si es una lista de campos
        if fields_content.strip().startswith('['):
            # Remover 'id', 'created_at', 'updated_at' si están presentes
            fields_content_clean = re.sub(r"'id',?\s*", '', fields_content)
            fields_content_clean = re.sub(r'"id",?\s*', '', fields_content_clean)
            fields_content_clean = re.sub(r"'created_at',?\s*", '', fields_content_clean)
            fields_content_clean = re.sub(r"'updated_at',?\s*", '', fields_content_clean)
            
            # Si la lista quedó vacía, solo usar base
            if fields_content_clean.strip() in ['[]', '[ ]']:
                return f'{indent}read_only_fields = BaseModelSerializer.Meta.read_only_fields'
            
            return f'{indent}read_only_fields = BaseModelSerializer.Meta.read_only_fields + {fields_content_clean}'
        
        return match.group(0)
    
    readonly_pattern = r'(\s+)read_only_fields\s*=\s*(\[[\s\S]*?\])'
    content = re.sub(readonly_pattern, update_readonly_fields, content)
    
    # Solo escribir si hubo cambios
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False


def main():
    """Refactorizar archivos de serializers"""
    
    # Archivos a refactorizar
    files_to_refactor = [
        'backend/inventario/serializers.py',
        'backend/institucion/serializers.py',
    ]
    
    base_dir = Path('c:/Users/gfranco/Desktop/SIAE')
    
    refactored_count = 0
    
    for file_rel_path in files_to_refactor:
        file_path = base_dir / file_rel_path
        
        if not file_path.exists():
            print(f"❌ Archivo no encontrado: {file_path}")
            continue
        
        print(f"🔄 Refactorizando: {file_rel_path}")
        
        if refactor_serializer_file(file_path):
            print(f"✅ Refactorizado: {file_rel_path}")
            refactored_count += 1
        else:
            print(f"⏭️  Sin cambios: {file_rel_path}")
    
    print(f"\n✨ Refactorización completada: {refactored_count} archivos modificados")


if __name__ == '__main__':
    main()
