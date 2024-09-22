from rest_framework import serializers
from neo_demo.utils.serializers import GenericNeomodelSerializer
from .models import Person, Movie


class PersonModelSerializer(GenericNeomodelSerializer):
    class Meta:
        model = Person
        fields = "__all__"
        read_only_fields = ["uid"]


class MovieModelSerializer(GenericNeomodelSerializer):

    class Meta:
        model = Movie
        fields = "__all__"
        read_only_fields = ["uid"]
