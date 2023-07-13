from rest_framework import serializers, fields
import re


class FieldSchema(serializers.Serializer):
    title = serializers.CharField()
    type = serializers.CharField()

    def validate(self, data):
        """
        Check if type is correct, else throw validation error
        """
        if not (data['type'].lower()) in ("string", "boolean", "integer"):
            raise serializers.ValidationError({"type": f"invalid type `{data['type']}`"})
        title = data['title'].strip().replace(" ", "")
        stop_chars = "#$%&\'()*+,./:;<=>?@[\\]\"^`{|}~ \t\n\r\x0b\x0c'"
        if any(char in stop_chars for char in title):
            raise serializers.ValidationError({"title": f"invalid field name `{title}`"})
        reserved_keywords = [
            'SELECT', 'INSERT', 'UPDATE', 'DELETE', 'FROM',
            'WHERE', 'AND', 'OR', 'JOIN', 'GROUP BY',
            'ORDER BY', 'DESC', 'ASC'
        ]
        if title.upper() in reserved_keywords:
            raise serializers.ValidationError({"title": f"invalid field name `{title}` sql reserved keyword"})
        data['title'] = title
        return data


class TableCreateInput(serializers.Serializer):
    name = fields.CharField(max_length=255)
    fields = FieldSchema(many=True, required=True)

    def validate(self, data):
        """
        Check if type is correct, else throw validation error
        """
        not_allowed_pattern = r"[^\w\d_$]"
        if re.search(not_allowed_pattern, data['name']):
            raise serializers.ValidationError({"type": f"invalid table name `{data['name']}`"})
        return data


class TableUpdateInput(serializers.Serializer):
    fields = FieldSchema(many=True, required=True)
