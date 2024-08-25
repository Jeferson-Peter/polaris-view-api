from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .models import DataFile
from .serializers import DataFileSerializer
import polars as pl
import json


class DataFileUploadView(generics.CreateAPIView):
    queryset = DataFile.objects.all()
    serializer_class = DataFileSerializer
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        # Salva o nome original do arquivo
        file_name = self.request.FILES['file'].name
        file_type = 'csv' if file_name.endswith('.csv') else 'parquet'
        serializer.save(file_name=file_name, file_type=file_type)


class DataFileListView(generics.ListAPIView):
    queryset = DataFile.objects.all()
    serializer_class = DataFileSerializer


class DataFileDetailView(APIView):
    def get(self, request, pk, format=None):
        try:
            data_file = DataFile.objects.get(pk=pk)
        except DataFile.DoesNotExist:
            return Response({"error": "File not found"}, status=status.HTTP_404_NOT_FOUND)

        file_path = data_file.file.path

        try:
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 10))
            start = (page - 1) * page_size

            lazy_df = pl.scan_csv(file_path) if data_file.file_type == 'csv' else pl.scan_parquet(file_path)

            filters = json.loads(request.query_params.get('filters', '[]'))
            for filter in filters:
                col = filter['col']
                val = filter['val']
                lazy_df = lazy_df.filter(pl.col(col) == val)

            paginated_data = lazy_df.slice(start, page_size).collect()
            total_records = lazy_df.collect().height

            return Response({
                "file_name": data_file.file_name,
                "headers": paginated_data.columns,
                "data": paginated_data.to_dicts(),
                "page": page,
                "page_size": page_size,
                "total_records": total_records,
                "total_pages": (total_records + page_size - 1) // page_size
            })

        except Exception as e:
            return Response({"error": f"Failed to read the file: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

