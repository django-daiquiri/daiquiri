from django.dispatch import Signal

user_confirmed = Signal(providing_args=['user', 'confirmed_by'])
user_activated = Signal(providing_args=['user', 'activated_by'])
