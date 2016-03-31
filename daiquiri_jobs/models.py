from __future__ import unicode_literals

import uuid

from django.db import models
from django.contrib.auth.models import User
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from .utils import UWSException


@python_2_unicode_compatible
class Job(models.Model):

    PHASE_PENDING = 1
    PHASE_QUEUED = 2
    PHASE_EXECUTING = 3
    PHASE_COMPLETED = 4
    PHASE_ERROR = 5
    PHASE_ABORTED = 6
    PHASE_UNKNOWN = 7
    PHASE_HELD = 8
    PHASE_SUSPENDED = 9
    PHASE_ARCHIVED = 10
    PHASE_CHOICES = (
        (PHASE_PENDING, 'PENDING'),
        (PHASE_QUEUED, 'QUEUED'),
        (PHASE_EXECUTING, 'EXECUTING'),
        (PHASE_COMPLETED, 'COMPLETED'),
        (PHASE_ERROR, 'ERROR'),
        (PHASE_ABORTED, 'ABORTED'),
        (PHASE_UNKNOWN, 'UNKNOWN'),
        (PHASE_HELD, 'HELD'),
        (PHASE_SUSPENDED, 'SUSPENDED'),
        (PHASE_ARCHIVED, 'ARCHIVED')
    )

    JOB_TYPE_QUERY = 1
    JOB_TYPE_CHOICES = (
        (JOB_TYPE_QUERY, 'Query'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    owner = models.OneToOneField(User)

    run_id = models.CharField(max_length=256, blank=True)

    phase = models.PositiveSmallIntegerField(choices=PHASE_CHOICES)

    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    execution_duration = models.PositiveIntegerField(blank=True, default=0)
    destruction_time = models.DateTimeField(blank=True, null=True)

    job_type = models.PositiveSmallIntegerField(choices=JOB_TYPE_CHOICES)

    class Meta:
        ordering = ('start_time', )

        verbose_name = _('Job')
        verbose_name_plural = _('Jobs')

        permissions = (('view_job', 'Can view Job'),)

    def __str__(self):
        return str(self.id)

    def get_phase_str(self):
        return dict(self.PHASE_CHOICES)[self.phase]

    def get_job_type_str(self):
        return dict(self.JOB_TYPE_CHOICES)[self.job_type]

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
            raise UWSException('Job is not in PENDING phase.')

    def abort(self):
        if self.phase in (self.PHASE_PENDING, self.PHASE_QUEUED, self.PHASE_EXECUTING):
            self.phase = self.PHASE_ABORTED
            self.save()
        else:
            raise UWSException('Job is not in PENDING, QUEUED or EXECUTING phase.')
