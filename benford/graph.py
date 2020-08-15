import base64
import io
import urllib

import matplotlib.pyplot as plt

from benford.core import get_expected_distribution_flat
from benford.models import Dataset


def create_graph_buffer(dataset: Dataset):
    plt.plot(range(1, 10), get_expected_distribution_flat(),
             color='#736B92', marker='.', linestyle='None')
    digits = dataset.significant_digits.values_list('digit', flat=True).order_by('digit')
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
