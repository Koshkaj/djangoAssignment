from apps.core.schemas import TableCreateInput
from backend.utils import create_dynamic_django_model, inline_serializer, create_dynamic_serializer_class
from django.db import models, connection, transaction, utils
from django.conf import settings
from rest_framework.exceptions import ValidationError
from rest_framework import serializers, status
from .models import TableMetaData


def generate_serializer_fields(fields: dict):
    serializer_fields = {}
    for k, v in fields.items():
        match v:
            case "integer":
                ser_field = serializers.IntegerField()
            case "boolean":
                ser_field = serializers.BooleanField()
            case _:
                ser_field = serializers.CharField()
        serializer_fields[k] = ser_field
    return serializer_fields


def generate_model_fields(fields: dict | list):
    model_fields = {"__module__": __name__}

    if isinstance(fields, dict):
        for k, v in fields.items():
            match v:
                case "integer":
                    model_field = models.IntegerField()
                case "boolean":
                    model_field = models.BooleanField()
                case _:
                    model_field = models.CharField(settings.DEFAULT_CHAR_LENGTH)
            model_fields[k] = model_field
    elif isinstance(fields, list):
        for field in fields:
            title = field.get("title").lower()
            field_type = field.get("type").lower()
            match field_type:
                case "boolean":
                    model_fields[title] = models.BooleanField()
                case "integer":
                    model_fields[title] = models.IntegerField()
                case _:
                    model_fields[title] = models.CharField(max_length=settings.DEFAULT_CHAR_LENGTH)
    else:
        raise ValidationError({"detail": "unable to generate model fields"})
    return model_fields


def handle_table_create(serializer: TableCreateInput) -> models.Model:
    # check if table exists
    table_name = serializer.data['name'].lower()
    meta = get_table_meta(table_name=table_name)
    if meta:
        raise ValidationError({"detail": f"table `{table_name}` already exists"})

    fields = generate_model_fields(fields=serializer.data['fields'])

    with transaction.atomic():
        meta_data = TableMetaData.objects.create(table_name=table_name,
                                                 fields=fields_to_json_dict(fields))
        fields["meta_data_id"] = meta_data.id
        model = create_dynamic_django_model(model_name=table_name, fields=fields)
        with connection.schema_editor() as se:
            se.create_model(model)
    return model


def handle_table_update_schema(table_id: int, data: dict):
    # check if exists
    meta = get_table_meta(id=table_id)
    if not meta:
        raise ValidationError({"detail": f"table with id `{table_id}` does not exist"})

    model_fields = generate_model_fields(fields=data['fields'])
    to_add_keys = model_fields.keys() - meta.fields.keys()
    to_remove_keys = meta.fields.keys() - model_fields.keys()
    to_alter_keys = model_fields.keys() & meta.fields.keys()

    if to_remove_keys:
        temp = {}
        for k in to_remove_keys:
            v = meta.fields[k]
            temp[k] = v
        model_fields = {**generate_model_fields(temp), **model_fields}

    with transaction.atomic():
        try:
            model = create_dynamic_django_model(model_name=meta.table_name, fields=model_fields)
            with connection.schema_editor() as se:
                for k, v in model_fields.items():
                    if k in to_add_keys:
                        se.add_field(model, v)
                        meta.fields[k] = v.db_type(connection)
                        meta.save()
                    elif k in to_alter_keys:
                        old_field = getattr(model, k)
                        se.alter_field(model, old_field.field, v)
                        meta.fields[k] = v.db_type(connection)
                        meta.save()
                    elif k in to_remove_keys:
                        old_field = getattr(model, k)
                        se.remove_field(model, old_field.field)
                        del meta.fields[k]
                        meta.save()
        except utils.IntegrityError as e:
            raise ValidationError(code=status.HTTP_400_BAD_REQUEST, detail={"detail": e,
                                                                            "info": "probably the functionality that you are looking for is not implemented"})

    return data


def handle_table_add_rows(data: dict, table_id: int) -> dict:
    # Check if exists
    meta = get_table_meta(id=table_id)
    if not meta:
        raise ValidationError({"detail": f"table with id `{table_id}` does not exist"})

    # Query the table fields and generate dynamic serializer/model
    serializer_fields = generate_serializer_fields(fields=meta.fields)
    model_fields = generate_model_fields(fields=meta.fields)

    # check validity of the payload
    serializer = inline_serializer(fields=serializer_fields, many=True,
                                   data=data['rows'])
    serializer.is_valid(raise_exception=True)

    model = create_dynamic_django_model(model_name=meta.table_name, fields=model_fields)

    # add rows to the table
    with transaction.atomic():
        objects = model.objects.bulk_create(
            [
                model(**data) for data in serializer.data
            ]
        )
    output_serializer = create_dynamic_serializer_class(model)
    data = output_serializer(objects, many=True).data
    return {
        "table": meta.table_name,
        "data": data
    }


def handle_table_get_rows(table_id: int):
    # check if table exists
    meta = get_table_meta(id=table_id)
    if not meta:
        raise ValidationError({"detail": f"table with id `{table_id}` does not exist"})

    # generate dynamic model out of it
    model_fields = generate_model_fields(fields=meta.fields)
    model = create_dynamic_django_model(model_name=meta.table_name, fields=model_fields)

    # generate dynamic serializer and return the data
    output_serializer = create_dynamic_serializer_class(model)
    objects = model.objects.all()
    data = output_serializer(objects, many=True).data
    return {
        "table": meta.table_name,
        "data": data
    }


def get_table_meta(**kwargs) -> TableMetaData | None:
    return TableMetaData.objects.filter(**kwargs).first()


def jsonify_dynamic_model_data(model: object) -> dict:
    data = {"id": model.meta_data_id,
            "table_name": model.__name__,
            "fields": []}
    for field in model._meta.fields:
        field_data = {"title": field.name,
                      "type": field.db_type(connection)}
        data['fields'].append(field_data)
    return data


def fields_to_json_dict(data: dict) -> dict:
    return {k: v.db_type(connection) for k, v in data.items() if k != "__module__"}
