from django.dispatch import Signal

user_created = Signal(providing_args=['user'])
user_updated = Signal(providing_args=['user'])
user_groups_updated = Signal(providing_args=['user'])

user_confirmed = Signal(providing_args=['request', 'user'])
user_rejected = Signal(providing_args=['request', 'user'])
user_activated = Signal(providing_args=['request', 'user'])
user_disabled = Signal(providing_args=['request', 'user'])
user_enabled = Signal(providing_args=['request', 'user'])
