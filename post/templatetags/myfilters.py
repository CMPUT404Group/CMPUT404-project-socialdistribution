from django import template
import json

register = template.Library()

@register.filter(name='addClass')
def addClass(value, arg):
	return value.as_widget(attrs={'class': arg})

@register.filter(name='addPlaceholder')
def addPlaceholder(value, arg):
	return value.as_widget(attrs={'placeholder': arg})

@register.filter(name='addAttributes')
def addAttributes(value, arg):
	newArg = json.loads(arg)
	# attributes = arg.split('+')
	# newArg = {}
	# for attr in attributes:
	# 	values = attr.split(":")
	# 	newArg[values[0]] = values[1]

	return value.as_widget(attrs=newArg)