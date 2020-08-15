from django import template

from benford.graph import get_graph_img_src
from benford.models import Dataset

register = template.Library()


@register.inclusion_tag('benford/templatetags/graph.html')
def graph(dataset: Dataset):
    img_src = get_graph_img_src(dataset=dataset)
    return {
        'img_src': img_src,
    }
