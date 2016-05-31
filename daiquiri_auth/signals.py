from django.dispatch import Signal

user_confirmed = Signal(providing_args=['request', 'user'])
user_activated = Signal(providing_args=['request', 'user'])
user_disabled = Signal(providing_args=['request', 'user'])
user_enabled = Signal(providing_args=['request', 'user'])
