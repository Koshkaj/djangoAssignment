from django.db.models import Model
from rest_framework import serializers


def create_dynamic_django_model(model_name, fields):
    return type(model_name, (Model,), fields)


def create_dynamic_serializer_class(model):
    return type(f"{model.__name__}Serializer",
                (serializers.ModelSerializer,),
                {"Meta": type("Meta", (), {"model": model, "fields": "__all__"})})


def inline_serializer(*, fields, data=None, **kwargs):
    serializer_class = type("", (serializers.Serializer,), fields)

    if data is not None:
        return serializer_class(data=data, **kwargs)

    return serializer_class(**kwargs)
