from django.db import models


class DataFile(models.Model):
    FILE_TYPES = (
        ('csv', 'CSV'),
        ('parquet', 'Parquet'),
    )
    file_name = models.CharField(max_length=255)
    file = models.FileField(upload_to='data_files/')
    file_type = models.CharField(max_length=10, choices=FILE_TYPES)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.file_name} ({self.get_file_type_display()}) uploaded on {self.uploaded_at}"
