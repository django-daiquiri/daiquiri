app.factory('QueryService', ['$resource', '$injector', '$q', '$filter', 'PollingService', 'PlotService', 'DownloadService', 'TableService', 'BrowserService', function($resource, $injector, $q, $filter, PollingService, PlotService, DownloadService, TableService, BrowserService) {

    /* get the base url */

    var baseurl = angular.element('meta[name="baseurl"]').attr('content');

    /* configure resources */

    var resources = {
        status: $resource(baseurl + 'query/api/status/'),
        forms: $resource(baseurl + 'query/api/forms/'),
        dropdowns: $resource(baseurl + 'query/api/dropdowns/'),
        jobs: $resource(baseurl + 'query/api/jobs/:id/:detail_route/'),
        examples: $resource(baseurl + 'query/api/examples/user/'),
        queues: $resource(baseurl + 'query/api/queues/'),
        querylanguages: $resource(baseurl + 'query/api/querylanguages/'),
        phases: $resource(baseurl + 'query/api/phases/'),
        schemas: $resource(baseurl + 'metadata/api/schemas/user/'),
        functions: $resource(baseurl + 'metadata/api/functions/user/'),
    };

    /* initialise the browser service */

    BrowserService.init('schemas', ['schemas', 'tables', 'columns'])
    BrowserService.init('columns', ['columns'], true)
    BrowserService.init('functions', ['functions'])
    BrowserService.init('examples', ['examples'])

    /* create the query service */

    var service = {
        first_form: null,
        submitting: false,
        show: {'': true},
        forms: {},
        dropdowns: {},
        values: {},
        errors: {}
    };

    service.init = function() {
        // fetch queues,  query languages and then load forms
        service.queues = resources.queues.query();
        service.query_languages = resources.querylanguages.query();

        $q.all([service.queues.$promise, service.query_languages.$promise]).then(function(){
            service.active_queue = service.queues[0].id;

            resources.forms.query(function(response) {
                angular.forEach(response, function(form) {
                    service.forms[form.key] = $injector.get(form.form_service);

                    // remember the first form
                    if (!service.first_form) {
                        service.first_form = service.forms[form.key];
                    }
                });

                // activate the first form
                service.first_form.activate();
            });
        });

        // fetch job phases
        service.phases = resources.phases.query();

        // load dropdowns
        resources.dropdowns.query(function(response) {
            angular.forEach(response, function(dropdown) {
                service.dropdowns[dropdown.key] = $injector.get(dropdown.dropdown_service);
                service.dropdowns[dropdown.key].options = dropdown.options;
            });
        });

        // fetch status
        service.fetch_status();

        // fetch functions
        resources.functions.query(function(response) {
            BrowserService.render('functions', response);
        });

        // fetch examples
        resources.examples.query(function(response) {
            BrowserService.render('examples', response);
        });

        // fetch schemas
        resources.schemas.query(function(response) {
            service.schemas = response;

            service.columns = []
            angular.forEach(service.schemas, function(schema) {
                angular.forEach(schema.tables, function(table) {
                    angular.forEach(table.columns, function(column) {
                        var column_copy = angular.copy(column);
                        column_copy.name = schema.name + '.' + table.name + '.' + column.name;
                        service.columns.push(column_copy);
                    });
                });
            });

            // load user schema when schemas have been fetched
            service.fetch_user_schema();
        });

        // fetch joblist
        service.fetch_jobs();

        // activate overview tab
        service.tab = 'overview';

        // start the polling service
        service.polling = PollingService
        service.polling.init();
        service.polling.register('status', service.fetch_status, {}, true, false);
        service.polling.register('jobs', service.fetch_jobs, {}, true, false);
        service.polling.register('schema', service.fetch_user_schema, {}, true, false);

        // load the other services
        service.table = TableService;
        service.plot = PlotService;
        service.downloads = DownloadService;
    };

    service.fetch_status = function() {
        return resources.status.query(function(response) {
            service.status = response[0];
        }).$promise;
    };

    service.fetch_user_schema = function() {
        return resources.jobs.query({
            'detail_route': 'tables'
        }, function(response) {
            var user_schema = response[0];

            var user_columns = [];
            angular.forEach(user_schema.tables, function(table) {
                angular.forEach(table.columns, function(column) {
                    var column_copy = angular.copy(column);
                    column_copy.name = user_schema.name + '.' + table.name + '.' + column.name;
                    user_columns.push(column_copy);
                });
            });

            BrowserService.render('schemas', service.schemas.concat(user_schema));
            BrowserService.render('columns', service.columns.concat(user_columns));
        }).$promise;
    }

    service.fetch_jobs = function() {
        return resources.jobs.paginate({
            page_size: 1000,
            archived: ''
        }, function(response) {
            service.jobs = response.results;

            service.run_ids = service.jobs.map(function(job) {
                return job.run_id;
            }).filter(function(run_id, index, run_ids) {
                return run_id && run_ids.indexOf(run_id) == index;
            }).sort();
            service.run_ids.push('');

            if (service.job) {
                // show the run id of the current job
                service.show[service.job.run_id] = true;

                // get the current job from the jobs list
                var current_job = $filter('filter')(service.jobs, {'id': service.job.id})[0];

                // if the phase has changed, fetch it again
                if (current_job && current_job.phase != service.job.phase) {
                    service.activate_job(service.job);
                }
            }

        }).$promise;
    };

    service.fetch_job = function(job) {
        return resources.jobs.get({id: job.id}, function(response) {
            service.job = response;

            // get the current job in the jobs list
            var jobs_job = $filter('filter')(service.jobs, {'id': service.job.id})[0]

            if (angular.isUndefined(jobs_job) || jobs_job.phase != service.job.phase) {
                // if the phase has changed, fetch the job list again
                service.fetch_jobs();
            }
        }).$promise;
    };

    service.activate_form = function(key) {
        // this function should be called from the form service
        service.form = key;
        service.job = null;
    };

    service.submit_job = function(values) {
        // this function should be called from the form service
        values = angular.extend({}, values, {
            'queue': service.active_queue
        });

        service.submitting = true;
        return resources.jobs.save(values).$promise
            .then(function(job) {
                service.fetch_status();
                service.activate_job(job);
            }).finally(function() {
                service.submitting = false;
            });
    };

    service.activate_job = function(job) {
        service.form = null;
        service.fetch_job(job).then(function() {
            service.table.ready = false;
            service.plot.ready = false;

            if (service.job.phase == 'COMPLETED') {
                // re-init current tab
                service.init_tab(service.tab);
            } else {
                // activate overview tab
                service.activate_tab('overview');
            }

            CodeMirror.runMode(service.job.query, "text/x-sql", angular.element('#query')[0]);

            if (service.job.native_query) {
                CodeMirror.runMode(service.job.native_query, "text/x-sql", angular.element('#native-query')[0]);
            }
            if (service.job.actual_query) {
                CodeMirror.runMode(service.job.actual_query, "text/x-sql", angular.element('#actual-query')[0]);
            }
        });
    };

    service.modal = function(modal_id) {
        service.errors = {};
        service.values = service.job;

        $('#' + modal_id).modal('show');
    };

    service.update_job = function() {
        resources.jobs.update({id: service.values.id}, service.values).$promise.then(function() {
            service.fetch_jobs();
            $('.modal').modal('hide');
        }, function(response) {
            service.errors = response.data;
        });
    };

    service.abort_job = function() {
        resources.jobs.update({id: service.values.id, detail_route: 'abort'}, {}, function() {
            service.fetch_status();
            service.fetch_jobs();
            $('.modal').modal('hide');
        });
    };

    service.archive_job = function() {
        var index = service.jobs.indexOf($filter('filter')(service.jobs, {
            'id': service.job.id
        })[0]);

        var next_job = null;
        if (index == 0 && angular.isDefined(service.jobs[1])) {
            next_job = service.jobs[1];
        } else if (angular.isDefined(service.jobs[index - 1])){
            next_job = service.jobs[index - 1];
        }

        resources.jobs.delete({id: service.values.id}, function() {
            service.fetch_status();
            service.fetch_jobs();

            if (next_job) {
                service.activate_job(next_job);
            } else {
                service.first_form.activate();
            }

            $('.modal').modal('hide');
        });
    };

    service.activate_tab = function(tab) {
        service.init_tab(tab);
        service.tab = tab;
    };

    service.init_tab = function(tab) {
        if (tab == 'results') {
            if (!service.table.ready) {
                if (service.job && service.job.phase == 'COMPLETED') {
                    service.table.init({
                        rows_url: 'query/api/jobs/' + service.job.id +'/rows/',
                        columns_url: 'query/api/jobs/' + service.job.id +'/columns/',
                        files_url: 'files/api/files/',
                        references_url: 'serve/api/references/',
                        params: {
                            job: service.job.id
                        }
                    });
                } else {
                    service.table.clear();
                }
            }
        } else if (tab == 'plot') {
            if (!service.plot.ready) {
                if (service.job && service.job.phase == 'COMPLETED') {
                    service.plot.init({
                        rows_url: 'query/api/jobs/' + service.job.id +'/rows/',
                        columns: service.job.columns
                    });
                } else {
                    service.plot.clear();
                }
            }
        } else if (tab == 'download') {
            service.downloads.init({
                job: service.job
            });
        }
    }

    return service;

}]);
