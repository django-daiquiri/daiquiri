import uuid
from typing import override

from django.contrib.auth.models import User
from django.db import models


class Proposal(models.Model):
    PHASE_PENDING = 'PENDING'
    PHASE_SUBMITTED = 'SUBMITTED'
    PHASE_ACCEPTED = 'ACCEPTED'
    PHASE_DECLINED = 'DECLINED'

    PHASE_CHOICES = [
        (PHASE_PENDING, 'Pending'),
        (PHASE_SUBMITTED, 'Submitted'),
        (PHASE_ACCEPTED, 'Accepted'),
        (PHASE_DECLINED, 'Declined'),
    ]

    prop_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pi = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='pi_proposals')
    title = models.CharField(max_length=255, default='')
    abstract = models.TextField(default='')
    copi = models.ManyToManyField(User, blank=True, related_name='copi_proposals')
    proprietary_until = models.DateTimeField(null=True, blank=True)
    phase = models.CharField(max_length=16, choices=PHASE_CHOICES, default=PHASE_PENDING)

    @override
    def __str__(self):
        return f'{self.title}, PI: {self.pi.username if self.pi else "Not available"}'
