from django import template

from benford.analyzer import BenfordAnalyzer
from benford.graph import get_graph_img_src

register = template.Library()


@register.inclusion_tag('benford/templatetags/graph.html')
def graph(analyzer: BenfordAnalyzer):
    img_src = get_graph_img_src(analyzer=analyzer)
    return {
        'img_src': img_src,
    }
