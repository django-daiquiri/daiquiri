from django.dispatch import Signal

user_created = Signal()
user_updated = Signal()
user_deleted = Signal()
user_groups_updated = Signal()

user_confirmed = Signal()
user_rejected = Signal()
user_activated = Signal()
user_disabled = Signal()
user_enabled = Signal()
