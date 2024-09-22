from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.viewsets import ViewSetMixin
from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    UpdateModelMixin,
    RetrieveModelMixin,
)
from django.http import Http404
from neomodel import Q
import math
from functools import reduce
from collections import OrderedDict


class NeoGenericAPIView(GenericAPIView):
    model = None
    lookup_field = "uid"
    cypher_query_limit = 10

    def get_object_or_404(self, **kwargs):
        try:
            return self.model.nodes.get(**kwargs)
        except self.model.DoesNotExist:
            raise Http404(
                "No %s matches the given query." % self.model.__class__.__name__
            )

    def get_object(self):
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        assert lookup_url_kwarg in self.kwargs, (
            "Expected view %s to be called with a URL keyword argument "
            'named "%s". Fix your URL conf, or set the `.lookup_field` '
            "attribute on the view correctly."
            % (self.__class__.__name__, lookup_url_kwarg)
        )

        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        obj = self.get_object_or_404(**filter_kwargs)
        self.check_object_permissions(self.request, obj)
        return obj

    def get_search_value(self, request: Request) -> dict | None:
        return request.query_params.get("search", None)

    def get_cypher_paginated_response(self, request: Request, data):
        code = 2000
        msg = "success"
        page = int(request.query_params.get("page")) or 1
        total = len(data) if data else 0
        limit = int(self.cypher_query_limit) or 10
        total_pages = math.ceil(len(data) / limit) if data else 0
        is_next = True if page < total_pages else False
        is_previous = True if page > 1 else False

        start_index = (page - 1) * limit
        end_index = start_index + limit

        paginated_data = data[start_index:end_index]

        if not data:
            code = 2000
            msg = "暂无数据"
            data = []

        return Response(
            OrderedDict(
                [
                    ("code", code),
                    ("msg", msg),
                    ("page", page),
                    ("limit", limit),
                    ("total", total),
                    ("is_next", is_next),
                    ("is_previous", is_previous),
                    ("data", paginated_data),
                ]
            )
        )


class ListModelMixin:
    def list(self, request: Request, *args, **kwargs):
        search_value = self.get_search_value(request)
        if not search_value:
            queryset = self.model.nodes.all()
        else:
            # 判空
            if not self.search_fields:
                raise ValueError(
                    "%s search_fields option must not be None"
                    % (self.__class__.__name__)
                )
            # 判类型
            if not isinstance(self.search_fields, (list, tuple)):
                raise TypeError(
                    "%s search_fields option type must be list or tuple"
                    % (self.__class__.__name__)
                )

            q_objects = [
                Q(**{f"{field}__icontains": search_value})
                for field in self.search_fields
            ]

            # 使用 reduce 和 | 操作符将 Q 对象连接起来

            queryset = self.model.nodes.filter(reduce(lambda x, y: x | y, q_objects))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class GenericNeoViewSet(ViewSetMixin, NeoGenericAPIView):
    pass


class NeoModelViewSet(
    CreateModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    GenericNeoViewSet,
):
    pass
