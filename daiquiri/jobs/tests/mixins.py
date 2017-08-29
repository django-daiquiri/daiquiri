import iso8601

from lxml import objectify

from django.core.urlresolvers import reverse
from django.db.models import Q
from django.utils.http import urlencode

from test_generator.core import TestMixin


class SyncTestMixin(TestMixin):

    def _test_get_job_list(self, username):
        '''
        GET /{jobs} returns 404.
        '''
        url = reverse(self.url_names['list'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)

    def _test_post_job_list_create(self, username):
        '''
        POST /{jobs} with an application/x-www-form-urlencoded set of KEY=VALUE
        creates a job with these parameters and redirects to /{jobs}/{job-id}
        as 303.
        '''
        for new_job in self.get_parameter_for_new_jobs(username):
            url = reverse(self.url_names['list'])
            response = self.client.post(url, urlencode(new_job), content_type='application/x-www-form-urlencoded')
            self.assertEqual(response.status_code, 303, msg=(
                ('username', username),
                ('url', url),
                ('data', new_job),
                ('status_code', response.status_code),
                ('content', response.content)
            ))

    def _test_post_job_list_create_internal(self, username):
        '''
        POST /{jobs} with an application/x-www-form-urlencoded set of KEY=VALUE
        creates a job with these parameters and redirects to /{jobs}/{job-id}
        as 303.
        '''
        for new_job in self.get_parameter_for_new_jobs_internal(username):
            url = reverse(self.url_names['list'])
            response = self.client.post(url, urlencode(new_job), content_type='application/x-www-form-urlencoded')
            self.assertEqual(response.status_code, 400 if username == 'anonymous' else 303, msg=(
                ('username', username),
                ('url', url),
                ('data', new_job),
                ('status_code', response.status_code),
                ('content', response.content)
            ))


class AsyncTestMixin(TestMixin):

    uws_ns = '{http://www.ivoa.net/xml/UWS/v1.0}'

    def _test_get_job_list_xml(self, username):
        '''
        GET /{jobs} returns the job list as <uws:jobs> xml element. The archived
        jobs are not returned.
        '''
        url = reverse(self.url_names['list'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        if username == 'user':
            root = objectify.fromstring(response.content)
            self.assertEqual(root.tag, self.uws_ns + 'jobs')
            self.assertEqual(root.jobref.tag, self.uws_ns + 'jobref')
            self.assertEqual(len(root.jobref), len(self.jobs))

    def _test_get_job_list_xml_phase(self, username):
        '''
        GET /{jobs}?PHASE=<phase> returns the filtered joblist as <jobs>
        element.
        '''
        url = reverse(self.url_names['list']) + '?PHASE=PENDING&PHASE=ARCHIVED'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        if username == 'user':
            root = objectify.fromstring(response.content)
            self.assertEqual(len(root.jobref), len(self.jobs.filter(Q(phase='PENDING')|Q(phase='ARCHIVED'))))

    def _test_get_job_list_xml_after(self, username):
        '''
        GET /{jobs}?AFTER=2014-09-10T10:01:02.000 returns jobs with startTimes
        after the given [std:iso8601] time in UTC. The archived jobs are not
        returned.
        '''
        url = reverse(self.url_names['list']) + '?AFTER=2017-01-01T01:00:00Z'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        if username == 'user':
            root = objectify.fromstring(response.content)
            self.assertEqual(len(root.jobref), len(self.jobs.filter(creation_time__gte='2017-01-01T01:00:00Z')))

    def _test_get_job_list_xml_last(self, username):
        '''
        GET /{jobs}?LAST=100 returns the given number of most recent jobs
        ordered by ascending startTimes. The archived jobs are not returned.
        '''
        url = reverse(self.url_names['list']) + '?LAST=3'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        if username == 'user':
            root = objectify.fromstring(response.content)
            self.assertEqual(len(root.jobref), 3)

    def _test_post_job_list_create(self, username):
        '''
        POST /{jobs} with an application/x-www-form-urlencoded set of KEY=VALUE
        creates a job with these parameters and redirects to /{jobs}/{job-id}
        as 303.
        '''
        for new_job in self.get_parameter_for_new_jobs(username):
            url = reverse(self.url_names['list'])
            response = self.client.post(url, urlencode(new_job), content_type='application/x-www-form-urlencoded')
            self.assertEqual(response.status_code, 303, msg=(
                ('username', username),
                ('url', url),
                ('data', new_job),
                ('status_code', response.status_code),
                ('content', response.content)
            ))

            response = self.client.get(response['Location'] + '/phase')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.content.decode(), 'PENDING')

    def _test_post_job_list_create_internal(self, username):
        '''
        POST /{jobs} with an application/x-www-form-urlencoded set of KEY=VALUE
        creates a job with these parameters and redirects to /{jobs}/{job-id}
        as 303.
        '''
        for new_job in self.get_parameter_for_new_jobs_internal(username):
            url = reverse(self.url_names['list'])
            response = self.client.post(url, urlencode(new_job), content_type='application/x-www-form-urlencoded')
            self.assertEqual(response.status_code, 400 if username == 'anonymous' else 303, msg=(
                ('username', username),
                ('url', url),
                ('data', new_job),
                ('status_code', response.status_code),
                ('content', response.content)
            ))

    def _test_post_job_list_create_run(self, username):
        '''
        POST /{jobs} with an application/x-www-form-urlencoded set of
        KEY=VALUE and additionally PHASE=RUN to an non-existing {job-id} creates
        a job with these parameters and runs it.
        '''
        for new_job in self.get_parameter_for_new_jobs(username):
            new_job.update({'PHASE': 'RUN'})

            url = reverse(self.url_names['list'])
            response = self.client.post(url, urlencode(new_job), content_type='application/x-www-form-urlencoded')
            self.assertEqual(response.status_code, 303)

            response = self.client.get(response['Location'] + '/phase')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.content.decode(), 'COMPLETED')

    def _test_get_job_detail(self, username):
        '''
        GET /{jobs}/{job-id} returns a job as <uws:job> xml element.
        '''
        for job in self.jobs:
            url = reverse(self.url_names['detail'], kwargs={'pk': job.pk})
            response = self.client.get(url)

            if username == 'user':
                self.assertEqual(response.status_code, 200)

                root = objectify.fromstring(response.content)
                self.assertEqual(root.tag, self.uws_ns + 'job')
            else:
                self.assertEqual(response.status_code, 404)

    def _test_get_job_results(self, username):
        '''
        GET /{jobs}/{job-id}/results returns any results of the job {job-id} as
        <uws:results> xml element.
        '''
        for job in self.jobs:
            url = reverse(self.url_names['results'], kwargs={'pk': job.pk})
            response = self.client.get(url)

            if username == 'user':
                self.assertEqual(response.status_code, 200)

                root = objectify.fromstring(response.content)
                self.assertEqual(root.tag, self.uws_ns + 'results')
            else:
                self.assertEqual(response.status_code, 404)


    def _test_get_job_result(self, username):
        '''
        GET /{jobs}/{job-id}/results/result returns a 303 to the stream url for this job.
        '''
        for job in self.jobs:
            url = reverse(self.url_names['result'], kwargs={'pk': job.pk})
            response = self.client.get(url)

            if username == 'user':
                if job.phase == 'COMPLETED':
                    self.assertRedirects(response, job.result, status_code=303, target_status_code=200)
                else:
                    self.assertRedirects(response, job.result, status_code=303, target_status_code=400)
            else:
                self.assertEqual(response.status_code, 404)


    def _test_get_job_parameters(self, username):
        '''
        GET /{jobs}/{job-id}/parameters returns any parameters for the job
        {job-id} as <uws:parameters> xml element.
        '''
        for job in self.jobs:
            url = reverse(self.url_names['parameters'], kwargs={'pk': job.pk})
            response = self.client.get(url)

            if username == 'user':
                self.assertEqual(response.status_code, 200)

                root = objectify.fromstring(response.content)
                self.assertEqual(root.tag, self.uws_ns + 'parameters')
            else:
                self.assertEqual(response.status_code, 404)

    def _test_get_job_error(self, username):
        '''
        GET /{jobs}/{job-id}/error returns any error message associated with
        {job-id} as text.
        '''
        for job in self.jobs:
            url = reverse(self.url_names['error'], kwargs={'pk': job.pk})
            response = self.client.get(url)

            if username == 'user':
                self.assertEqual(response.status_code, 200)
            else:
                self.assertEqual(response.status_code, 404)

    def _test_get_job_delete(self, username):
        '''
        DELETE /{jobs}/{job-id} sets the job phase to ARCHIVED and deletes the
        results and redirects to /{jobs}/{job-id} as 303.
        '''
        for job in self.jobs:
            url = reverse(self.url_names['detail'], kwargs={'pk': job.pk})
            response = self.client.delete(url)

            if username == 'user':
                redirect_url = 'http://testserver' + reverse(self.url_names['detail'], kwargs={'pk': job.pk})
                self.assertRedirects(response, redirect_url, status_code=303)
                self.assertEqual(self.jobs.get(pk=job.pk).phase, 'ARCHIVED')
            else:
                self.assertEqual(response.status_code, 404)


    def _test_post_job_delete(self, username):
        '''
        POST /{jobs}/{job-id} with ACTION=DELETE sets the job phase to ARCHIVED
        and deletes the results and redirects to /{jobs}/{job-id} as 303.
        '''
        for job in self.jobs:
            url = reverse(self.url_names['detail'], kwargs={'pk': job.pk})
            response = self.client.post(url, urlencode({'ACTION': 'DELETE'}), content_type='application/x-www-form-urlencoded')

            if username == 'user':
                redirect_url = 'http://testserver' + reverse(self.url_names['detail'], kwargs={'pk': job.pk})
                self.assertRedirects(response, redirect_url, status_code=303)
                self.assertEqual(self.jobs.get(pk=job.pk).phase, 'ARCHIVED')
            else:
                self.assertEqual(response.status_code, 404)


    def _test_post_job_invalid(self, username):
        '''
        POST /{jobs}/{job-id} with invalid ACTION returns 400.
        '''
        for job in self.jobs:
            url = reverse(self.url_names['detail'], kwargs={'pk': job.pk})
            response = self.client.post(url, urlencode({'ACTION': 'not_valid'}), content_type='application/x-www-form-urlencoded')

            if username == 'user':
                self.assertEqual(response.status_code, 400)
            else:
                self.assertEqual(response.status_code, 404)


    def _test_post_job_missing(self, username):
        '''
        POST /{jobs}/{job-id} without ACTION returns 400.
        '''
        for job in self.jobs:
            url = reverse(self.url_names['detail'], kwargs={'pk': job.pk})
            response = self.client.post(url, content_type='application/x-www-form-urlencoded')

            if username == 'user':
                self.assertEqual(response.status_code, 400)
            else:
                self.assertEqual(response.status_code, 404)


    def _test_get_job_destruction(self, username):
        '''
        GET /{jobs}/{job-id}/destruction returns the destruction instant for
        {job-id} as [std:iso8601].
        '''
        for job in self.jobs:
            url = reverse(self.url_names['destruction'], kwargs={'pk': job.pk})
            response = self.client.get(url)

            if username == 'user':
                self.assertEqual(response.status_code, 200)

                if job.destruction_time:
                    destruction_time = iso8601.parse_date(response.content.decode())
                    self.assertEqual(destruction_time, job.destruction_time)
                else:
                    self.assertEqual(response.content.decode(), '')
            else:
                self.assertEqual(response.status_code, 404)

    def _test_post_job_destruction(self, username):
        '''
        POST /{jobs}/{job-id}/destruction with DESTRUCTION={std:iso8601}
        (application/x-www-form-urlencoded) sets the destruction instant for
        {job-id} and redirects to /{jobs}/{job-id} as 303.
        '''
        destruction_time = '2016-01-01T00:00:00'

        for job in self.jobs:
            url = reverse(self.url_names['destruction'], kwargs={'pk': job.pk})
            response = self.client.post(url, urlencode({'DESTRUCTION': destruction_time}), content_type='application/x-www-form-urlencoded')

            if username == 'user':
                redirect_url = 'http://testserver' + reverse(self.url_names['detail'], kwargs={'pk': job.pk})
                self.assertRedirects(response, redirect_url, status_code=303)
                self.assertEqual(
                    self.jobs.get(pk=job.pk).destruction_time,
                    iso8601.parse_date('2016-01-01T00:00:00')
                )
            else:
                self.assertEqual(response.status_code, 404)


    def _test_post_job_destruction_invalid(self, username):
        '''
        POST /{jobs}/{job-id}/destruction with invalid DESTRUCTION returns 400.
        '''
        for job in self.jobs:
            url = reverse(self.url_names['destruction'], kwargs={'pk': job.pk})
            response = self.client.post(url, urlencode({'DESTRUCTION': 'not_a_date'}), content_type='application/x-www-form-urlencoded')

            if username == 'user':
                self.assertEqual(response.status_code, 400)
            else:
                self.assertEqual(response.status_code, 404)


    def _test_post_job_destruction_missing(self, username):
        '''
        POST /{jobs}/{job-id}/destruction without DESTRUCTION returns 400.
        '''
        for job in self.jobs:
            url = reverse(self.url_names['destruction'], kwargs={'pk': job.pk})
            response = self.client.post(url, content_type='application/x-www-form-urlencoded')

            if username == 'user':
                self.assertEqual(response.status_code, 400)
            else:
                self.assertEqual(response.status_code, 404)


    def _test_get_job_executionduration(self, username):
        '''
        GET /{jobs}/{job-id}/executionduration returns the maximum execution
        duration of {job-id} as integer.
        '''
        for job in self.jobs:
            url = reverse(self.url_names['executionduration'], kwargs={'pk': job.pk})
            response = self.client.get(url)

            if username == 'user':
                self.assertEqual(response.status_code, 200)
                self.assertEqual(int(response.content), job.execution_duration)
            else:
                self.assertEqual(response.status_code, 404)


    def _test_post_job_executionduration(self, username):
        '''
        POST /{jobs}/{job-id}/executionduration with EXECUTIONDURATION={int}
        sets the maximum execution duration of {job-id} and redirects as to
        /{jobs}/{job-id} 303.
        '''
        execution_duration = 60

        for job in self.jobs:
            url = reverse(self.url_names['executionduration'], kwargs={'pk': job.pk})
            response = self.client.post(url, urlencode({'EXECUTIONDURATION': 60}), content_type='application/x-www-form-urlencoded')

            if username == 'user':
                redirect_url = 'http://testserver' + reverse(self.url_names['detail'], kwargs={'pk': job.pk})
                self.assertRedirects(response, redirect_url, status_code=303)
                self.assertEqual(self.jobs.get(pk=job.pk).execution_duration, execution_duration)
            else:
                self.assertEqual(response.status_code, 404)


    def _test_post_job_executionduration_invalid(self, username):
        '''
        POST /{jobs}/{job-id}/executionduration with invalid EXECUTIONDURATION returns 400.
        '''
        for job in self.jobs:
            url = reverse(self.url_names['executionduration'], kwargs={'pk': job.pk})
            response = self.client.post(url, urlencode({'EXECUTIONDURATION': 'not_an_integer'}), content_type='application/x-www-form-urlencoded')

            if username == 'user':
                self.assertEqual(response.status_code, 400)
            else:
                self.assertEqual(response.status_code, 404)


    def _test_post_job_executionduration_missing(self, username):
        '''
        POST /{jobs}/{job-id}/executionduration without EXECUTIONDURATION returns 400.
        '''
        for job in self.jobs:
            url = reverse(self.url_names['executionduration'], kwargs={'pk': job.pk})
            response = self.client.post(url, content_type='application/x-www-form-urlencoded')

            if username == 'user':
                self.assertEqual(response.status_code, 400)
            else:
                self.assertEqual(response.status_code, 404)


    def _test_get_job_phase(self, username):
        '''
        GET /{jobs}/{job-id}/phase returns the phase of job {job-id} as one of
        the fixed strings.
        '''
        for job in self.jobs:
            url = reverse(self.url_names['phase'], kwargs={'pk': job.pk})
            response = self.client.get(url)

            if username == 'user':
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.content, job.phase.encode())
            else:
                self.assertEqual(response.status_code, 404)

    def _test_post_job_phase_run(self, username):
        '''
        POST /{jobs}/{job-id}/phase with PHASE=RUN runs the job {job-id} and
        redirects as to /{jobs}/{job-id} 303.
        '''
        for job in self.jobs:
            url = reverse(self.url_names['phase'], kwargs={'pk': job.pk})
            response = self.client.post(url, urlencode({'PHASE': 'RUN'}), content_type='application/x-www-form-urlencoded')

            if username == 'user':
                if job.phase in ['PENDING']:
                    redirect_url = 'http://testserver' + reverse(self.url_names['detail'], kwargs={'pk': job.pk})
                    self.assertRedirects(response, redirect_url, status_code=303)
                    self.assertEqual(self.jobs.get(pk=job.pk).phase, 'COMPLETED')
                else:
                    self.assertEqual(response.status_code, 400)

            else:
                self.assertEqual(response.status_code, 404)

    def _test_post_job_phase_abort(self, username):
        '''
        POST /{jobs}/{job-id}/phase with PHASE=ABORT aborts the job {job-id} and
        redirects as to /{jobs}/{job-id} 303.
        '''
        for job in self.jobs:
            url = reverse(self.url_names['phase'], kwargs={'pk': job.pk})
            response = self.client.post(url, urlencode({'PHASE': 'ABORT'}), content_type='application/x-www-form-urlencoded')

            if username == 'user':
                redirect_url = 'http://testserver' + reverse(self.url_names['detail'], kwargs={'pk': job.pk})
                self.assertRedirects(response, redirect_url, status_code=303)

                if job.phase in ['PENDING', 'QUEUED', 'EXECUTING']:
                    self.assertEqual(self.jobs.get(pk=job.pk).phase, 'ABORTED')
                else:
                    self.assertEqual(self.jobs.get(pk=job.pk).phase, job.phase)
            else:
                self.assertEqual(response.status_code, 404)


    def _test_post_job_phase_invalid(self, username):
        '''
        POST /{jobs}/{job-id}/phase with invalid PHASE returns 400.
        '''
        for job in self.jobs:
            url = reverse(self.url_names['phase'], kwargs={'pk': job.pk})
            response = self.client.post(url, urlencode({'PHASE': 'invalid'}), content_type='application/x-www-form-urlencoded')

            if username == 'user':
                self.assertEqual(response.status_code, 400)
            else:
                self.assertEqual(response.status_code, 404)


    def _test_post_job_phase_missing(self, username):
        '''
        POST /{jobs}/{job-id}/phase without PHASE returns 400.
        '''
        for job in self.jobs:
            url = reverse(self.url_names['phase'], kwargs={'pk': job.pk})
            response = self.client.post(url, content_type='application/x-www-form-urlencoded')

            if username == 'user':
                self.assertEqual(response.status_code, 400)
            else:
                self.assertEqual(response.status_code, 404)


    def _test_post_job_phase_unsupported(self, username):
        '''
        POST /{jobs}/{job-id}/phase with PHASE=unsupported returns 400.
        '''
        for job in self.jobs:
            url = reverse(self.url_names['phase'], kwargs={'pk': job.pk})
            response = self.client.post(url, urlencode({'PHASE': 'unsupported'}), content_type='application/x-www-form-urlencoded')

            if username == 'user':
                self.assertEqual(response.status_code, 400)
            else:
                self.assertEqual(response.status_code, 404)


    def _test_get_job_quote(self, username):
        '''
        GET /{jobs}/{job-id}/quote returns the quote for {job-id} as [std:iso8601].
        '''
        for job in self.jobs:
            url = reverse(self.url_names['quote'], kwargs={'pk': job.pk})
            response = self.client.get(url)

            if username == 'user':
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.content.decode(), '')
            else:
                self.assertEqual(response.status_code, 404)

    def _test_get_job_owner(self, username):
        '''
        GET /{jobs}/{job-id}/owner returns the owner of the job {job-id} as an
        appropriate identifier.
        '''
        for job in self.jobs:
            url = reverse(self.url_names['owner'], kwargs={'pk': job.pk})
            response = self.client.get(url)

            if username == 'user':
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.content.decode(), job.owner.username)
            else:
                self.assertEqual(response.status_code, 404)
