import base64
import io
import urllib

import matplotlib.pyplot as plt
from matplotlib.pyplot import xticks

from benford.analyzer import BenfordAnalyzer
from benford.core import get_expected_distribution_flat


def create_graph_buffer(analyzer: BenfordAnalyzer):
    assert isinstance(analyzer, BenfordAnalyzer)
    dataset = analyzer.dataset
    expected_distribution = get_expected_distribution_flat()
    x_range = range(1, dataset.base)
    xticks(x_range)
    plt.plot(
        x_range, expected_distribution,
        color='black', marker='o', linestyle='None')
    plt.errorbar(
        x_range, expected_distribution,
        yerr=2, linestyle='None', color='black')
    digits = x_range

    # Observed values.
    percentages = analyzer.get_observed_distribution_flat()
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


def get_graph_img_src(analyzer: BenfordAnalyzer):
    return get_graph_as_base64(create_graph_buffer(analyzer=analyzer))
