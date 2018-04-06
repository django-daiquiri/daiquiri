app.factory('JobsService', ['$resource', '$timeout', 'ListService', function($resource, $timeout, ListService) {

    /* get the base url */

    var baseurl = angular.element('meta[name="baseurl"]').attr('content');

    /* configure resources */

    var resources = {
        jobs: $resource(baseurl + 'query/api/jobs/:id/:detail_route/'),
        queues: $resource(baseurl + 'query/api/queues/:id/'),
        phases: $resource(baseurl + 'query/api/phases/:id/')
    }

    /* create the service */

    var service = {
        list: ListService,
        selected: {},
        phase_map: {}
    };

    service.init = function(phases) {
        service.queues = resources.queues.query();

        resources.phases.query(function(response) {
            service.phases = response;

            angular.forEach(service.phases, function(phase) {
                service.phase_map[phase.id] = phase.text;

                if (phase.id == 'ARCHIVED') {
                    service.selected[phase.id] = false;
                } else {
                    service.selected[phase.id] = true;
                }
            });

            service.update_phases();
            service.list.init(resources.jobs);
            service.ready = true;
        });
    };

    service.reload = function(fetch) {
        service.update_phases();
        service.list.reload();
    };

    service.update_phases = function() {
        service.list.params.phase = [];
        angular.forEach(service.selected, function(value, key) {
            if (value) {
                service.list.params.phase.push(key);
            }
        });
    }

    service.modal = function(modal_id, index) {
        service.current_index = index;
        service.current_row = service.list.rows[index];

        service.job = service.list.rows[index];

        if (modal_id == 'show-job-modal') {
            resources.jobs.get({id: service.current_row.id}, function(response) {
                service.job = response;
                $('#show-job-modal').modal('show');

                CodeMirror.runMode(service.job.query, "text/x-sql", angular.element('#query')[0]);

                if (service.job.native_query) {
                    CodeMirror.runMode(service.job.native_query, "text/x-sql", angular.element('#native-query')[0]);
                }
                if (service.job.actual_query) {
                    CodeMirror.runMode(service.job.actual_query, "text/x-sql", angular.element('#actual-query')[0]);
                }
            })
        } else {
            service.values = angular.copy(service.current_row);
            $('#' + modal_id).modal('show');
        }
    };

    service.copy_query = function(row_id) {
        resources.jobs.get({id: row_id}, function(response) {
            localStorage.setItem('stored_query_language', response.query_language);
            localStorage.setItem('stored_query', response.query);
        });
    };

    service.update_job = function() {
        resources.jobs.update({id: service.values.id}, service.values, function(response) {
            service.list.rows[service.current_index].table_name = response.table_name;
            service.list.rows[service.current_index].run_id = response.run_id;
            $('.modal').modal('hide');
        }, function(response) {
            service.errors = response.data;
        });
    };

    service.archive_job = function() {
        resources.jobs.delete({id: service.values.id}, function() {
            if (service.selected['ARCHIVED']) {
                service.list.rows[service.current_index].phase = 'ARCHIVED';
            } else {
                service.list.rows.splice(service.current_index, 1);
            }

            $('.modal').modal('hide');
        });
    };

    return service;
}]);
