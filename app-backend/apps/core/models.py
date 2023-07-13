from django.db import models


class TableMetaData(models.Model):
    id = models.AutoField(primary_key=True)
    # You would have a user foreign key here in prod scenario
    table_name = models.CharField(max_length=255)
    fields = models.JSONField()

    def __str__(self):
        return f"{self.id} -> {self.table_name}"
