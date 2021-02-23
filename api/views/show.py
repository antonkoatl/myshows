from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from api.common import StandardPageNumberPagination
from myshows.models.show import Show
from myshows.serializers import ShowSerializer


class ShowViewSet(viewsets.ModelViewSet):
    """
    API методы для работы с Show
    """
    queryset = Show.objects.all()
    serializer_class = ShowSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StandardPageNumberPagination
