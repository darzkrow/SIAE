from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .utils_import import CSVImportProcessor

class CSVImportViewSet(viewsets.ViewSet):
    """ViewSet para manejar la importación de datos externos."""
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'], url_path='upload-articles')
    def upload_articles(self, request):
        """Sube un CSV para importar artículos."""
        # Solo permitir a ADMINS
        if request.user.role != 'ADMIN':
            return Response({'error': 'Solo administradores pueden importar datos'}, status=status.HTTP_403_FORBIDDEN)

        file_obj = request.FILES.get('file')
        product_type = request.data.get('product_type') # 'chemical', 'pipe', etc.

        if not file_obj:
            return Response({'error': 'No se proporcionó ningún archivo'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not product_type:
            return Response({'error': 'Debe especificar el tipo de producto (product_type)'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            results = CSVImportProcessor.process_csv(file_obj, product_type)
            return Response(results, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
