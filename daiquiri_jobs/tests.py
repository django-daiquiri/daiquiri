from django.test import TestCase


        '''
        If a request is made to a resource that does not exist (e.g. an
        non-existent job-id) then a 404 error should be returned.
        '''
        # IMPLEMENTED

        '''
        If a request is made that is illegal for the current state of the UWS
        then a 403 status should e returned.
        '''
        # IMPLEMENTED

        '''
        If for some reason there is a complete failure in the underlying UWS
        machinery then a 500 "internal server error" status should be returned.
        '''
        # IMPLEMENTED

        '''
        GET /{jobs} returns the job list as <uws:jobs> xml element.
        '''
        # IMPLEMENTED

        '''
        GET /{jobs}?PHASE=<phase> returns the filtered joblist as <jobs>
        element.
        '''
        # IMPLEMENTED

        '''
        GET /{jobs}?AFTER=2014-09-10T10:01:02.000 returns jobs with startTimes
        after the given [std:iso8601] time in UTC.
        '''
        # IMPLEMENTED

        '''
        GET /{jobs}?LAST=100 returns the given number of most recent jobs
        ordered by ascending startTimes.
        '''
        # IMPLEMENTED

        '''
        GET /{jobs}/{job-id} returns a job as <uws:job> xml element.
        '''
        # IMPLEMENTED

        '''
        GET /{jobs}/{job-id}/results returns any results of the job {job-id} as
        <uws:results> xml element.
        '''

        '''
        GET /{jobs}/{job-id}/parameters returns any parameters for the job
        {job-id} as <uws:parameters> xml element.
        '''

        '''
        POST /{jobs}/{job-id} with an application/x-www-form-urlencoded set of
        KEY=VALUE to an non-existing {job-id} creates a job with these
        parameters.
        '''

        '''
        POST /{jobs}/{job-id} with an application/x-www-form-urlencoded set of
        KEY=VALUE and additionally PHASE=RUN to an non-existing {job-id} creates
        a job with these parameters and runs it.
        '''

        '''
        POST /{jobs}/{job-id} with an application/x-www-form-urlencoded set of
        KEY=VALUE to an existing {job-id} updates the parameters.
        '''

        '''
        POST /{jobs}/{job-id}/parameters with application/x-www-form-urlencoded
        set of KEY=VALUE updates the parameters.
        '''

        '''
        GET /{jobs}/{job-id}/error returns any error message associated with
        {job-id} as text.
        '''
        # IMPLEMENTED

        '''
        DELETE /{jobs}/{job-id} sets the job phase to ARCHIVED and deletes the
        results and redirects to /{jobs}/{job-id} as 303.
        '''
        # IMPLEMENTED

        '''
        POST /{jobs}/{job-id} with ACTION=DELETE sets the job phase to ARCHIVED
        and deletes the results and redirects to /{jobs}/{job-id} as 303.
        '''

        '''
        GET /{jobs}/{job-id}/destruction returns the destruction instant for
        {job-id} as [std:iso8601].
        '''
        # IMPLEMENTED

        '''
        POST /{jobs}/{job-id}/destruction with DESTRUCTION={std:iso8601} sets
        the destruction instant for {job-id} and redirects to /{jobs}/{job-id}
        as 303.
        '''
        # IMPLEMENTED

        '''
        GET /{jobs}/{job-id}/executionduration returns the maximum execution
        duration of {job-id} as integer.
        '''
        # IMPLEMENTED

        '''
        POST /{jobs}/{job-id}/executionduration with EXECUTIONDURATION={int}
        sets the maximum execution duration of {job-id} and redirects as to
        /{jobs}/{job-id} 303.
        '''
        # IMPLEMENTED

        '''
        GET /{jobs}/{job-id}/phase returns the phase of job {job-id} as one of
        the fixed strings.
        '''
        # IMPLEMENTED

        '''
        POST /{jobs}/{job-id}/phase with PHASE=RUN runs the job {job-id} and
        redirects as to /{jobs}/{job-id} 303.
        '''
        # IMPLEMENTED

        '''
        POST /{jobs}/{job-id}/phase with PHASE=ABORT aborts the job {job-id} and
        redirects as to /{jobs}/{job-id} 303.
        '''
        # IMPLEMENTED

        '''
        GET /{jobs}/{job-id}/quote returns the quote for {job-id} as
        [std:iso8601].
        '''
        # IMPLEMENTED

        '''
        GET /{jobs}/{job-id}/owner returns the owner of the job {job-id} as an
        appropriate identifier.
        '''
        # IMPLEMENTED

        # TODO: 2.2.1.2. Blocking Behaviour
