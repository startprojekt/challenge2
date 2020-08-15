from django.db import models
from django.db.models import Sum
from django.urls import reverse

from benford.core import get_expected_distribution
from benford.utils import calc_percentage, generate_random_identifier


class Dataset(models.Model):
    slug = models.CharField(
        max_length=10, unique=True, default=generate_random_identifier)
    title = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    base = models.PositiveSmallIntegerField(default=10)

    def display_title(self):
        return self.title or 'Untitled dataset'

    def get_absolute_url(self):
        return reverse('benford:dataset_detail', kwargs={'slug': self.slug})

    def get_occurences_summary(self):
        return dict((x.digit, x.occurences) for x in self.significant_digits.all())

    class Meta:
        ordering = ['-created_at', ]


class SignificantDigit(models.Model):
    dataset = models.ForeignKey(
        'Dataset', on_delete=models.CASCADE, related_name='significant_digits')
    digit = models.PositiveSmallIntegerField()
    occurences = models.PositiveIntegerField()

    def calculate_occurence_percentage(self):
        return calc_percentage(self.occurences, self.dataset.count_records())

    def benford_percentage(self):
        return get_expected_distribution(self.digit, self.dataset.base)

    class Meta:
        unique_together = [
            ('dataset', 'digit'),
        ]
