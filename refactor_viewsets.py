"""
Script de Refactorización Automática de ViewSets
Migra todos los viewsets a heredar de las clases base de core
"""
import re
import sys
from pathlib import Path


def refactor_viewset_file(file_path):
    """Refactoriza un archivo de viewsets para usar clases base de core"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # 1. Agregar import de core.viewsets si no existe
    if 'from core.viewsets import' not in content:
        # Encontrar la línea de imports de rest_framework
        import_pattern = r'(from rest_framework import viewsets)'
        replacement = r'\1\nfrom core.viewsets import BaseModelViewSet, SoftDeleteViewSet'
        content = re.sub(import_pattern, replacement, content)
    
    # 2. Refactorizar viewsets que heredan de viewsets.ModelViewSet
    # Patrón: class XViewSet(..., viewsets.ModelViewSet):
    
    # Casos a manejar:
    # - class XViewSet(viewsets.ModelViewSet):
    # - class XViewSet(AuditMixin, TrashBinMixin, viewsets.ModelViewSet):
    # - class XViewSet(BaseAPIViewSet):  # No cambiar
    
    # Patrón para encontrar clases de viewsets
    # Buscar viewsets.ModelViewSet y reemplazar con BaseModelViewSet
    class_pattern = r'(class\s+\w+ViewSet\([^)]*?)viewsets\.ModelViewSet(\))'
    
    def replace_viewset_class(match):
        prefix = match.group(1)
        suffix = match.group(2)
        
        # Si ya tiene AuditMixin, TrashBinMixin, usar SoftDeleteViewSet
        if 'AuditMixin' in prefix or 'TrashBinMixin' in prefix:
            return f'{prefix}SoftDeleteViewSet{suffix}'
        else:
            return f'{prefix}BaseModelViewSet{suffix}'
    
    content = re.sub(class_pattern, replace_viewset_class, content)
    
    # 3. Reemplazar viewsets.ReadOnlyModelViewSet con BaseModelViewSet
    readonly_pattern = r'(class\s+\w+ViewSet\([^)]*?)viewsets\.ReadOnlyModelViewSet(\))'
    content = re.sub(readonly_pattern, r'\1BaseModelViewSet\2', content)
    
    # 4. Reemplazar viewsets.ViewSet con viewsets.ViewSet (no cambiar)
    # No hacer nada, ViewSet es para custom viewsets sin modelo
    
    # Solo escribir si hubo cambios
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False


def main():
    """Refactorizar archivos de viewsets"""
    
    # Archivos a refactorizar
    files_to_refactor = [
        'backend/inventario/views.py',
        'backend/institucion/views.py',
    ]
    
    base_dir = Path('c:/Users/gfranco/Desktop/SIAE')
    
    refactored_count = 0
    
    for file_rel_path in files_to_refactor:
        file_path = base_dir / file_rel_path
        
        if not file_path.exists():
            print(f"❌ Archivo no encontrado: {file_path}")
            continue
        
        print(f"🔄 Refactorizando: {file_rel_path}")
        
        if refactor_viewset_file(file_path):
            print(f"✅ Refactorizado: {file_rel_path}")
            refactored_count += 1
        else:
            print(f"⏭️  Sin cambios: {file_rel_path}")
    
    print(f"\n✨ Refactorización completada: {refactored_count} archivos modificados")


if __name__ == '__main__':
    main()
