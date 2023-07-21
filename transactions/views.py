from rest_framework import generics, permissions, pagination, status
from .models import Transaction
from .serializers import TransactionSerializer
from rest_framework.response import Response
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from .permissions import IsOwner
from django.db.models import Sum
from django.db.models.functions import Lower
from rest_framework.decorators import api_view, permission_classes


class CustomPagination(pagination.PageNumberPagination):
    """
    Custom pagination class to return custom response
    """
    page_size = 10
    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):
        return Response({
            'page_size': self.page_size,
            'current_page_number': self.page.number,
            'total_pages': self.page.paginator.num_pages,
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })


class TransactionListCreateView(generics.ListCreateAPIView):
    """
    get: List all transactions for requesting user and order by date or custom user filter by date, category, type
    post: Create a new transaction for requesting user
    """
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomPagination
    category_param_config = openapi.Parameter('category', in_=openapi.IN_QUERY, description='Filter by category', type=openapi.TYPE_STRING)
    type_param_config = openapi.Parameter('type', in_=openapi.IN_QUERY, description='Filter by type', type=openapi.TYPE_STRING)
    date_from_param_config = openapi.Parameter('date_from', in_=openapi.IN_QUERY, description='Filter by date from', type=openapi.FORMAT_DATE)
    date_to_param_config = openapi.Parameter('date_to', in_=openapi.IN_QUERY, description='Filter by date to', type=openapi.FORMAT_DATE)

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(manual_parameters=[category_param_config, type_param_config, date_from_param_config, date_to_param_config])
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def get_queryset(self):
        translations = super().get_queryset().filter(user=self.request.user)
        category = self.request.query_params.get('category', None)
        type = self.request.query_params.get('type', None)
        date_from = self.request.query_params.get('date_from', None)
        date_to = self.request.query_params.get('date_to', None)

        if category:
            translations = translations.filter(category=category)

        if type:
            translations = translations.filter(type=type)

        if date_from and date_to:
            translations = translations.filter(date__range=[date_from, date_to])
            
        return translations.order_by('-date')


class TransactionRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    lookup_field = 'pk'


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def monthly_summary_report(request):
    monthly_summary = Transaction.objects.values('date__year', 'date__month', 'type')\
                                         .annotate(total_amount=Sum('amount'))\
                                         .order_by('date__year', 'date__month')
    return Response(monthly_summary)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def category_wise_expense_report(request):
    category_wise_expenses = Transaction.objects.filter(type='expense') \
                                                .values('category') \
                                                .annotate(total_expense=Sum('amount')) \
                                                .order_by(Lower('category'))
    return Response(category_wise_expenses)
