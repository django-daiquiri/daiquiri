app.factory('QueryService', ['$resource', '$injector', 'PollingService', 'DownloadService', 'TableService', 'BrowserService', function($resource, $injector, PollingService, DownloadService, TableService, BrowserService) {

    /* get the base url */

    var baseurl = angular.element('meta[name="baseurl"]').attr('content');

    /* configure resources */

    var resources = {
        forms: $resource(baseurl + 'query/api/forms/'),
        jobs: $resource(baseurl + 'query/api/jobs/:id/:detail_route'),
        examples: $resource(baseurl + 'query/api/examples/'),
        databases: $resource(baseurl + 'query/api/databases/'),
        functions: $resource(baseurl + 'query/api/functions/'),
    };

    /* initialise the browser service */

    BrowserService.init('databases', ['databases', 'tables', 'columns'])
    BrowserService.init('columns', ['columns'], true)
    BrowserService.init('functions', ['functions'])
    BrowserService.init('examples', ['examples'])

    /* create the query service */

    var service = {
        forms: {},
        values: {},
        errors: {}
    };

    service.init = function() {
        // load forms
        resources.forms.query(function(response) {
            angular.forEach(response, function(form) {
                service.forms[form.key] = $injector.get(form.form_service);
            });

            // activate first form
            service.forms[response[0].key].activate();
        });

        // fetch functions
        resources.functions.query(function(response) {
            BrowserService.render('functions', response);
        });

        // fetch examples
        resources.examples.query(function(response) {
            BrowserService.render('examples', response);
        });

        // fetch databases
        resources.databases.query(function(response) {
            service.databases = response;

            service.columns = []
            angular.forEach(service.databases, function(database) {
                angular.forEach(database.tables, function(table) {
                    angular.forEach(table.columns, function(column) {
                        var column_copy = angular.copy(column);
                        column_copy.name = database.name + '.' + table.name + '.' + column.name;
                        service.columns.push(column_copy);
                    });
                });
            });

            // load joblist when database have been fetched
            service.fetchJobs();
        });

        // activate overview tab
        service.tab = 'overview';

        // start the polling service
        PollingService.init();
        PollingService.register('jobs', service.fetchJobs);

        // load the download service
        service.downloads = DownloadService;
    };

    service.fetchJobs = function() {
        return resources.jobs.query(function(response) {
            service.jobs = response;

            var user_database = {
                name: 'hey',
                tables: response.map(function(job) {
                    return {
                        name: job.table_name,
                        columns: job.columns
                    };
                })
            };

            var user_columns = [];
            angular.forEach(user_database.tables, function(table) {
                angular.forEach(table.columns, function(column) {
                    var column_copy = angular.copy(column);
                    column_copy.name = user_database.name + '.' + table.name + '.' + column.name;
                    user_columns.push(column_copy);
                });
            });

            BrowserService.render('databases', service.databases.concat(user_database));
            BrowserService.render('columns', service.columns.concat(user_columns));

        }).$promise;
    };

    service.fetchJob = function(job) {
        return resources.jobs.get({id: job.id}, function(response) {
            service.job = response;
        }).$promise;
    };

    service.activateForm = function(key) {
        service.form = key;
        service.job = null;
    };

    service.activateJob = function(job) {
        service.form = null;
        service.fetchJob(job).then(function() {

            TableService.init(service.job.database_name, service.job.table_name);

            CodeMirror.runMode(service.job.query, "text/x-mariadb", angular.element('#query')[0]);
            CodeMirror.runMode(service.job.actual_query, "text/x-mariadb", angular.element('#actual-query')[0]);
        });
    };

    service.submitJob = function(values) {
        values = angular.extend({}, values, {
            'queue': 'default',
            'query_language': 'mysql'
        });

        return resources.jobs.save(values).$promise.then(function() {
            resources.jobs.query(function(response) {
                service.jobs = response;
            });
        });
    };

    service.showModal = function(modal, job) {
        service.errors = {};

        if (angular.isDefined(job)) {
            service.values = job;
        }

        $('#' + modal + '-modal').modal('show');
    };

    service.renameJob = function() {
        resources.jobs.update({id: service.values.id}, service.values).$promise.then(function() {
            service.fetchJobs();
            $('.modal').modal('hide');
        }, function(response) {
            service.errors = response.data;
        });
    };

    service.killJob = function() {
        resources.jobs.update({id: service.values.id, detail_route: 'kill'}, {}, function() {
            service.fetchJobs();
            $('.modal').modal('hide');
        });
    };

    service.removeJob = function() {
        resources.jobs.delete({id: service.values.id}, function() {
            service.fetchJobs();
            $('.modal').modal('hide');
        });
    };

    return service;

}]);
