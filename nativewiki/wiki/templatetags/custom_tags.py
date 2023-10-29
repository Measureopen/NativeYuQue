from django import template
from wiki.models import Repository

register = template.Library()

@register.simple_tag
def change_id_name(id):

    name_value = Repository.objects.filter(repo_id=id).values("name").first()
    name = name_value.get("name")

    return name
