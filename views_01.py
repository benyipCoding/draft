from .seriealizers import PersonModelSerializer, MovieModelSerializer
from .utils.viewsets import NeoModelViewSet
from .models import Person, Movie
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from neomodel import db


class PersonViewSet(NeoModelViewSet):
    model = Person
    serializer_class = PersonModelSerializer
    search_fields = ["name"]

    @action(methods=["GET"], permission_classes=[IsAuthenticated], detail=False)
    def query_earning(self, request: Request):
        search_value = self.get_search_value(request)
        if not search_value:
            raise ValueError("Query params `search` is None")
        query = """
        MATCH (actor:Person)-[rel:ACTED_IN]->(movie:Movie)
        WHERE toLower(actor.name) CONTAINS $name
        RETURN actor.name,rel.earnings,movie.title      
        """
        results, meta = db.cypher_query(
            query, {"name": search_value}, resolve_objects=True
        )
        queryset = [
            {"name": res[0], "earnings": res[1], "movie": res[2]} for res in results
        ]
        return self.get_cypher_paginated_response(request, data=queryset)


class MovieViewSet(NeoModelViewSet):
    model = Movie
    serializer_class = MovieModelSerializer
    search_fields = ["title", "tagline"]
