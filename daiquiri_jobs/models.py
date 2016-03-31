from __future__ import unicode_literals

import uuid

from django.db import models
from django.contrib.auth.models import User
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from .utils import UWSException


@python_2_unicode_compatible
class Job(models.Model):

    PHASE_PENDING = 'PENDING'
    PHASE_QUEUED = 'QUEUED'
    PHASE_EXECUTING = 'EXECUTING'
    PHASE_COMPLETED = 'COMPLETED'
    PHASE_ERROR = 'ERROR'
    PHASE_ABORTED = 'ABORTED'
    PHASE_UNKNOWN = 'UNKNOWN'
    PHASE_HELD = 'HELD'
    PHASE_SUSPENDED = 'SUSPENDED'
    PHASE_ARCHIVED = 'ARCHIVED'
    PHASE_ACTIVE = (
        PHASE_PENDING,
        PHASE_QUEUED,
        PHASE_EXECUTING
    )
    PHASE_CHOICES = (
        (PHASE_PENDING, 'Pending'),
        (PHASE_QUEUED, 'Queued'),
        (PHASE_EXECUTING, 'Executing'),
        (PHASE_COMPLETED, 'Completed'),
        (PHASE_ERROR, 'Error'),
        (PHASE_ABORTED, 'Aborted'),
        (PHASE_UNKNOWN, 'Unknown'),
        (PHASE_HELD, 'Held'),
        (PHASE_SUSPENDED, 'Suspended'),
        (PHASE_ARCHIVED, 'Archived')
    )

    JOB_TYPE_QUERY = 'QUERY'
    JOB_TYPE_CHOICES = (
        (JOB_TYPE_QUERY, 'Query'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    owner = models.ForeignKey(User)

    run_id = models.CharField(max_length=256, blank=True)

    phase = models.CharField(max_length=10, choices=PHASE_CHOICES)

    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    execution_duration = models.PositiveIntegerField(blank=True, default=0)
    destruction_time = models.DateTimeField(blank=True, null=True)

    job_type = models.CharField(max_length=10, choices=JOB_TYPE_CHOICES)

    class Meta:
        ordering = ('start_time', )

        verbose_name = _('Job')
        verbose_name_plural = _('Jobs')

        permissions = (('view_job', 'Can view Job'),)

    def __str__(self):
        return "id=%s; phase=%s" % (str(self.id), self.phase)

    @property
    def error(self):
        return None

    @property
    def quote(self):
        return None

    def run(self):
        if self.phase == self.PHASE_PENDING:
            self.phase = self.PHASE_QUEUED
            self.save()
        else:
            raise UWSException('Job is not in PENDING phase')

    def abort(self):
        if self.phase in self.PHASE_ACTIVE:
            self.phase = self.PHASE_ABORTED
            self.save()
        else:
            raise UWSException('Job is not in PENDING, QUEUED or EXECUTING phase')

    def archive(self):
        if self.phase != self.PHASE_ARCHIVED:
            self.phase = self.PHASE_ARCHIVED
            self.save()
        else:
            raise UWSException('Job is already in ARCHIVED phase')
