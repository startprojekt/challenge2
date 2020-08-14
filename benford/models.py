import uuid
from decimal import Decimal

from django.db import models
from django.db.models import Count, Sum

from benford.utils import calc_percentage, generate_random_identifier


class Dataset(models.Model):
    slug = models.CharField(
        max_length=10, unique=True, default=generate_random_identifier)
    title = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def count_records(self) -> int:
        data = self.significant_digits.aggregate(Sum('occurences'))
        return data['occurences__sum']

    class Meta:
        ordering = ['-created_at', ]


class SignificantDigit(models.Model):
    dataset = models.ForeignKey(
        'Dataset', on_delete=models.CASCADE, related_name='significant_digits')
    digit = models.PositiveSmallIntegerField()
    occurences = models.PositiveSmallIntegerField()

    def calculate_occurence_percentage(self):
        return calc_percentage(self.occurences, self.dataset.count_records())

    class Meta:
        unique_together = [
            ('dataset', 'digit'),
        ]
