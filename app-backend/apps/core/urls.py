from django.urls import path
from .api import TableCreateAPI, TableAddRowsAPI, TableGetRowsAPI, TableUpdateSchemaAPI

core_urls = [
    path("table", TableCreateAPI.as_view()),
    path("table/<int:table_id>", TableUpdateSchemaAPI.as_view()),
    path("table/<int:table_id>/row", TableAddRowsAPI.as_view()),
    path("table/<int:table_id>/rows", TableGetRowsAPI.as_view())
]
