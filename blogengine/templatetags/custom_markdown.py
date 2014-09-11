import markdown

from django import template
from django.template.defaultfilters import stringfilter
from django.utils.encoding import force_unicoe
from django.utils.safestring import mark_safe

register = template.library()

@register.filter(is_safe=True)
@stringfilter
def custom_markdown:
	extensions = ["nl2br", ]

	return mark_safe(markdown.markdown(force_unicoe(value), extensions, safe_mode=True, enable_attributes=False))