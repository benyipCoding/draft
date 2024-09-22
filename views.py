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
