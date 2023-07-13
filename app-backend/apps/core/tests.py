from django.test import TestCase

from apps.core.handlers import handle_table_create
from apps.core.models import TableMetaData
from apps.core.schemas import TableCreateInput


class CreateTableTests(TestCase):

    def test_table_creation_success(self):
        data = {
            "name": "tester",
            "fields": [
                {"title": "name", "type": "string"},
                {"title": "age", "type": "integer"},
                {"title": "is_active", "type": "boolean"}
            ]
        }
        serializer = TableCreateInput(data=data)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        model = handle_table_create(serializer)
        self.assertIsNotNone(model)
        self.assertTrue(TableMetaData.objects.filter(table_name=data['name']).exists())

    def test_table_creation_fail_invalid_data(self):
        data = {
            "name": "%#$%#!@#!",
            "fields": [
                {"title": "isActive", "type": "boolean"}
            ]
        }
        serializer = TableCreateInput(data=data)
        self.assertFalse(serializer.is_valid())

        data = {
            "name": "tablename",
            "fields": [
                {"title": "is&ctive", "type": "boolean"}
            ]
        }
        serializer = TableCreateInput(data=data)
        self.assertFalse(serializer.is_valid())

    def test_table_creation_fail_invalid_type(self):
        data = {
            "name": "tablename",
            "fields": [
                {"title": "fieldname", "type": "other"}
            ]
        }
        serializer = TableCreateInput(data=data)
        self.assertFalse(serializer.is_valid())
