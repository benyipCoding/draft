from django_neomodel import DjangoNode
from neomodel import (
    UniqueIdProperty,
    StringProperty,
    IntegerProperty,
    StructuredRel,
    RelationshipTo,
    RelationshipFrom,
)


class ActedIn(StructuredRel):
    earnings = IntegerProperty()
    roles = StringProperty()


class Reviewed(StructuredRel):
    rating = IntegerProperty()
    summary = StringProperty()


class Movie(DjangoNode):
    title = StringProperty(unique_index=True)
    released = IntegerProperty()
    tagline = StringProperty()

    class Meta:
        app_label = "neo_demo"


class Person(DjangoNode):
    name = StringProperty(unique_index=True)
    born = IntegerProperty()
    acted_in = RelationshipTo(Movie, "ACTED_IN", model=ActedIn)
    directed = RelationshipTo(Movie, "DIRECTED")
    follows = RelationshipTo("Person", "FOLLOWS")
    follows_by = RelationshipFrom("Person", "FOLLOWS")
    has_contact = RelationshipTo("Person", "HAS_CONTACT")
    has_contact_by = RelationshipFrom("Person", "HAS_CONTACT")
    produced = RelationshipTo(Movie, "PRODUCED")
    reviewed = RelationshipTo(Movie, "REVIEWED", model=Reviewed)
    wrote = RelationshipTo(Movie, "WROTE")

    class Meta:
        app_label = "neo_demo"
