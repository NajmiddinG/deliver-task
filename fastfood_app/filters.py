import django_filters
from .models import Delivered


class DeliveredFilter(django_filters.FilterSet):
    """
    Filters Delivered objects by year and month of their delivery date.
    """
    year = django_filters.NumberFilter(field_name='date__year')
    month = django_filters.NumberFilter(field_name='date__month')

    class Meta:
        model = Delivered
        fields = ['year', 'month']
