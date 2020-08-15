import base64
import io
import urllib

import matplotlib.pyplot as plt

from benford.core import get_expected_distribution_flat
from benford.models import Dataset


def create_graph_buffer(dataset: Dataset):
    expected_distribution = get_expected_distribution_flat()
    x_range = range(1, dataset.base)
    plt.plot(
        x_range, expected_distribution,
        color='black', marker='o', linestyle='None')
    plt.errorbar(
        x_range, expected_distribution,
        yerr=2, linestyle='None', color='black')
    digits = dataset.significant_digits.values_list('digit', flat=True).order_by('digit')

    # Observed values.
    percentages = dataset.significant_digits.values_list('percentage', flat=True).order_by('digit')
    plt.bar(digits, percentages, color='#7C90DB')

    fig = plt.gcf()
    buffer = io.BytesIO()
    fig.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close(fig)
    return buffer


def get_graph_as_base64(buffer):
    string = base64.b64encode(buffer.read())
    base64_string = urllib.parse.quote(string)
    return f'data:image/png;base64,{base64_string}'


def get_graph_img_src(dataset: Dataset):
    return get_graph_as_base64(create_graph_buffer(dataset=dataset))
