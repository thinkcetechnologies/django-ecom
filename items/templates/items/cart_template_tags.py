from django import template
from itmems.models import Order

@register.filter
def cart_item_count(user):
	if user.is_authenticated:
		qs = order.objects.filter(user=user,ordered=False)
		if qs.exists():
			return qs[0].items.count()
	return 0		