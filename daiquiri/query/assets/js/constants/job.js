export const jobPhases = {
  'PENDING': gettext('Pending'),
  'QUEUED': gettext('Queued'),
  'EXECUTING': gettext('Executing'),
  'COMPLETED': gettext('Completed'),
  'ERROR': gettext('Error'),
  'ABORTED': gettext('Aborted'),
  'UNKNOWN': gettext('Unknown'),
  'HELD': gettext('Held'),
  'SUSPENDED': gettext('Suspended'),
  'ARCHIVED': gettext('Archived')
}

export const jobPhaseClass = {
  'PENDING': 'text-primary',
  'QUEUED': 'text-info-emphasis',
  'EXECUTING': 'text-secondary',
  'COMPLETED': 'text-success',
  'ERROR': 'text-danger',
  'ABORTED': 'text-secondary',
  'UNKNOWN': 'text-secondary',
  'HELD': 'text-secondary',
  'SUSPENDED': 'text-secondary',
  'ARCHIVED': 'text-secondary'
}

export const jobPhaseBadge = {
  'PENDING': 'badge text-bg-primary',
  'QUEUED': 'badge text-bg-info',
  'EXECUTING': 'badge text-bg-secondary',
  'COMPLETED': 'badge text-bg-success',
  'ERROR': 'badge text-bg-danger',
  'ABORTED': 'badge text-bg-secondary',
  'UNKNOWN': 'badge text-bg-secondary',
  'HELD': 'badge text-bg-secondary',
  'SUSPENDED': 'badge text-bg-secondary',
  'ARCHIVED': 'badge text-bg-secondary'
}

export const jobPhaseIcons = {
  'PENDING': 'bi bi-pause-circle',
  'EXECUTING': 'bi bi-play-circle',
  'COMPLETED': 'bi bi-check-circle',
  'ERROR': 'bi bi-exclamation-triangle',
  'ABORTED': 'bi bi-x-circle',
  'UNKNOWN': 'bi bi-question-circle',
  'HELD': 'bi bi-exclamation-octogon',
  'SUSPENDED': 'bi bi-exclamation-diamond',
  'ARCHIVED': 'bi bi-exclamation-archive'
}

export const jobPhaseSpinner = ['QUEUED']

export const jobPhaseMessage = {
  'PENDING': gettext('The query job is still pending.'),
  'QUEUED': gettext('The query job is still queued.'),
  'EXECUTING': gettext('The query job is still executing.'),
  'COMPLETED': gettext('The query job has been completed.'),
  'ERROR': gettext('The query job did not complete successfully.'),
  'ABORTED': gettext('The query job was aborted.'),
  'UNKNOWN': gettext('The query job has an unknown status.'),
  'HELD': gettext('The query job was held.'),
  'SUSPENDED': gettext('The query job was suspended.'),
  'ARCHIVED': gettext('The query job was archived.')
}
