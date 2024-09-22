```python
# models.py
from django_neomodel import DjangoNode
from neomodel import UniqueIdProperty, StringProperty, IntegerProperty


class Person(DjangoNode):
    uid = UniqueIdProperty()
    name = StringProperty(max_length=10, required=True, unique_index=True, blank=True)
    age = IntegerProperty(required=True)

    class Meta:
        app_label = "neo_demo"


class Movie(DjangoNode):
    uid = UniqueIdProperty()
    title = StringProperty(required=True, unique_index=True)
    released = IntegerProperty(default=2000)

    class Meta:
        app_label = "neo_demo"

```


```python
# serializers_01.py
from rest_framework import serializers
from neo_demo.utils.serializers import GenericNeomodelSerializer
from .models import Person, Movie


class PersonModelSerializer(GenericNeomodelSerializer):
    class Meta:
        model = Person
        fields = "__all__"


class MovieModelSerializer(GenericNeomodelSerializer):

    class Meta:
        model = Movie
        fields = "__all__"
        read_only_fields = ["uid"]

```

```python
# serializer.py
from rest_framework import serializers
import neomodel


class GenericNeomodelSerializer(serializers.Serializer):
    serializer_field_mapping = {
        neomodel.UniqueIdProperty: serializers.UUIDField,
        neomodel.StringProperty: serializers.CharField,
        neomodel.IntegerProperty: serializers.IntegerField,
    }

    # 定义可能的属性列表
    field_option_attrs = [
        "max_length",
        "required",
        "min_value",
        "max_value",
        "min_length",
        "blank",
        "default",
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 判空
        assert hasattr(
            self, "Meta"
        ), 'Class {serializer_class} missing "Meta" attribute'.format(
            serializer_class=self.__class__.__name__
        )
        assert hasattr(
            self.Meta, "model"
        ), 'Class {serializer_class} missing "Meta.model" attribute'.format(
            serializer_class=self.__class__.__name__
        )

        # 获取字段
        field_set = getattr(self.Meta.model, "__all_properties__")
        if self.Meta.fields != serializers.ALL_FIELDS:
            field_set = tuple(item for item in field_set if item[0] in self.Meta.fields)

        for field_name, field in field_set:
            # 获取字段的类型
            field_type = type(field)

            # 检查字段类型是否在 serializer_field_mapping 中
            if field_type in self.serializer_field_mapping:
                # 根据字段类型获取对应的序列化器字段类
                serializer_field_class = self.serializer_field_mapping[field_type]

                # 取属性
                field_kwargs = {}

                for attr in self.field_option_attrs:
                    value = getattr(field, attr, None)
                    if value is not None:
                        # 这个if为了保护uuid不被加上default属性
                        if (
                            type(field).__name__ == "UniqueIdProperty"
                            and attr == "default"
                        ):
                            continue
                        field_kwargs[attr] = value

                # 创建序列化器字段实例并赋值给字段
                if not field_name in self.fields:
                    self.fields[field_name] = serializer_field_class(**field_kwargs)

    def create(self, validated_data):
        for key, value in validated_data.items():
            if type(value).__name__ == "UUID":
                raise ValueError("UUID is auto generate")
        return self.Meta.model(**validated_data).save()

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            if type(value).__name__ == "UUID":
                raise ValueError("UUID is readonly")
            setattr(instance, key, value)
        instance.save()
        return instance


```


```python
views_01.py
from neo_demo.utils.views import GenericNeomodelView
from .seriealizers import PersonModelSerializer, MovieModelSerializer


from .models import Person, Movie


class PersonViewSet(GenericNeomodelView):
    model = Person
    serializer_class = PersonModelSerializer  # Replace with your actual serializer


class MovieViewSet(GenericNeomodelView):
    model = Movie
    serializer_class = MovieModelSerializer

```

```python
# views.py
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from neomodel import Q


class GenericNeomodelView(APIView):
    model = None
    serializer_class = None

    def post(self, request: Request):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(
            {"msg": "Person Created", "data": serializer.data},
            status=status.HTTP_201_CREATED,
        )

    def delete(self, request: Request, uid: str):
        try:
            instance = self.model.nodes.get(uid=uid)
            instance.delete()
            return Response({"msg": "Delete successfully"}, status=status.HTTP_200_OK)
        except self.model.DoesNotExist:
            return Response({"error": "not found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request: Request, uid: str):
        try:
            instance = self.model.nodes.get(uid=uid)
            serializer = self.serializer_class(
                instance, data=request.data, partial=True
            )
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response(
                {"msg": f"{self.serializer_class.Meta.model.__name__} Updated"},
                status=status.HTTP_200_OK,
            )
        except self.model.DoesNotExist:
            return Response({"error": "Not Found"}, status=status.HTTP_404_NOT_FOUND)

    def get(self, request: Request, uid: str | None = None):
        if not uid:
            #   查询多个
            queryset = self.model.nodes.all()
            serializer = self.serializer_class(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            # 查询单个
            try:
                instance = self.model.nodes.get(uid=uid)
                serializer = self.serializer_class(instance, many=False)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except self.model.DoesNotExist:
                return Response(
                    {"error": "Not Found"}, status=status.HTTP_404_NOT_FOUND
                )
```