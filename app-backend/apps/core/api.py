from rest_framework.views import APIView, Response, status
from rest_framework.exceptions import APIException
from .schemas import TableCreateInput, TableUpdateInput
from .handlers import (handle_table_create, jsonify_dynamic_model_data,
                       handle_table_update_schema, handle_table_add_rows, handle_table_get_rows)


class TableCreateAPI(APIView):
    serializer_class = TableCreateInput

    def post(self, request, *args, **kwargs):
        # Validate the data
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        model = handle_table_create(serializer)
        data = jsonify_dynamic_model_data(model)
        return Response(data=data, status=status.HTTP_200_OK)


class TableUpdateSchemaAPI(APIView):

    serializer_class = TableUpdateInput

    def put(self, request, table_id, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = handle_table_update_schema(table_id, serializer.data)
        return Response(data=data, status=status.HTTP_200_OK)


class TableAddRowsAPI(APIView):

    def post(self, request, table_id, *args, **kwargs):
        if not request.data.get("rows"):
            raise APIException(code=status.HTTP_400_BAD_REQUEST, detail={"rows": "list should be provided"})
        data = handle_table_add_rows(data=request.data, table_id=table_id)

        return Response(data=data, status=status.HTTP_200_OK)


class TableGetRowsAPI(APIView):
    def get(self, request, table_id, *args, **kwargs):
        data = handle_table_get_rows(table_id)
        return Response(data=data, status=status.HTTP_200_OK)

