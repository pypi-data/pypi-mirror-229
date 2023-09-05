import django_filters
from django.forms.utils import pretty_name
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from django_filters import BaseInFilter, NumberFilter


class NumberInFilter(BaseInFilter, NumberFilter):
    pass


class OrderingFilter(django_filters.OrderingFilter):
    descending_fmt = _('%s Descending')
    ascending_fmt = _('%s Ascending')

    def build_choices(self, fields, labels):
        ascending = [
            (param, labels.get(field, _(pretty_name(param))))
            for field, param in fields.items()
        ]

        descending = [
            ('-%s' % param, labels.get('-%s' % param, self.descending_fmt % label))
            for param, label in ascending
        ]

        ascending = [
            (field, self.ascending_fmt % param)
            for field, param in ascending
        ]

        return [val for pair in zip(ascending, descending) for val in pair]


class RateFilter(django_filters.ChoiceFilter):
    """
    A custom choice filter for filtering by rating.

    This filter is designed to handle rating-based filtering, allowing users to select
    a rating level (1 to 4 stars) to filter results based on their rating criteria.

    :param field_name: The name of the field in the model to filter by.
    :type field_name: str
    :param label: The label for the filter. Defaults to 'Rating'.
    :type label: str
    :param choices: The choices for the filter. Defaults to the predefined star rating choices.
    :type choices: list of tuple
    """

    CHOICES = (
        (4, mark_safe('<i class="text-warning fs-4 bi bi-star-fill"></i>'
                      '<i class="text-warning fs-4 bi bi-star-fill"></i>'
                      '<i class="text-warning fs-4 bi bi-star-fill"></i>'
                      '<i class="text-warning fs-4 bi bi-star-fill"></i>'
                      '<i class="text-warning fs-4 bi bi-star"></i>'
                      '{}'.format(_(" & Up")))),
        (3, mark_safe('<i class="text-warning fs-4 bi bi-star-fill"></i>'
                      '<i class="text-warning fs-4 bi bi-star-fill"></i>'
                      '<i class="text-warning fs-4 bi bi-star-fill"></i>'
                      '<i class="text-warning fs-4 bi bi-star"></i>'
                      '<i class="text-warning fs-4 bi bi-star"></i>'
                      '{}'.format(_(" & Up")))),
        (2, mark_safe('<i class="text-warning fs-4 bi bi-star-fill"></i>'
                      '<i class="text-warning fs-4 bi bi-star-fill"></i>'
                      '<i class="text-warning fs-4 bi bi-star"></i>'
                      '<i class="text-warning fs-4 bi bi-star"></i>'
                      '<i class="text-warning fs-4 bi bi-star"></i>'
                      '{}'.format(_(" & Up")))),
        (1, mark_safe('<i class="text-warning fs-4 bi bi-star-fill"></i>'
                      '<i class="text-warning fs-4 bi bi-star"></i>'
                      '<i class="text-warning fs-4 bi bi-star"></i>'
                      '<i class="text-warning fs-4 bi bi-star"></i>'
                      '<i class="text-warning fs-4 bi bi-star"></i>'
                      '{}'.format(_(" & Up"))))
    )

    def __init__(self, field_name, label=_('Rating'), choices=CHOICES):
        """
        Initialize a new RateFilter.

        :param field_name: The name of the field in the model to filter by.
        :type field_name: str
        :param label: The label for the filter. Defaults to 'Rating'.
        :type label: str
        :param choices: The choices for the filter. Defaults to the predefined star rating choices.
        :type choices: list of tuple
        """
        super().__init__(field_name=field_name, label=label, choices=choices)

    def filter(self, queryset, value):
        """
        Apply the rating filter to the queryset.

        This method filters the queryset based on the selected rating value.
        It constructs a lookup dictionary to filter the queryset according to the
        chosen rating level (1 to 4 stars).

        :param queryset: The queryset to filter.
        :type queryset: django.db.models.QuerySet
        :param value: The selected rating level.
        :type value: int or str
        :return: The filtered queryset.
        :rtype: django.db.models.QuerySet
        """
        if not value:
            return queryset

        value = int(value)
        lookup = {}

        if value == 1:
            lookup = {f'{self.field_name}__lt': 2, f'{self.field_name}__gte': 1}
        elif value == 2:
            lookup = {f'{self.field_name}__lt': 3, f'{self.field_name}__gte': 2}
        elif value == 3:
            lookup = {f'{self.field_name}__lt': 4, f'{self.field_name}__gte': 3}
        elif value == 4:
            lookup = {f'{self.field_name}__lte': 5, f'{self.field_name}__gte': 4}

        return queryset.filter(**lookup)


class FilterSet(django_filters.FilterSet):
    filterset_types = {}
    fields_map = {
        "top_left": [],
        "top_right": [],
        "top_body": [],
        "side": []
    }
    force_visibility = []
