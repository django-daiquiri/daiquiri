app.factory('QueryService', ['$resource', '$injector', function($resource, $injector) {

    /* get the base url */

    var baseurl = angular.element('meta[name="baseurl"]').attr('content');

    /* configure resources */

    var resources = {
        forms: $resource(baseurl + 'query/api/forms/'),
        jobs: $resource(baseurl + 'query/api/jobs/:id/'),
        databases: $resource(baseurl + 'query/api/databases/'),
        functions: $resource(baseurl + 'query/api/functions/'),
    };

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

        // load joblist
        service.jobs = resources.jobs.query();

        // activate overview tab
        service.tab = 'overview';
    };

    service.activateForm = function(key) {
        service.form = key;
        service.job = null;
    };

    service.activateJob = function(job) {
        service.form = null;
        service.job = resources.jobs.get({id: job.id}, function() {
            CodeMirror.runMode(service.job.query, "text/x-mariadb", angular.element('#query')[0]);
            CodeMirror.runMode(service.job.actual_query, "text/x-mariadb", angular.element('#actual-query')[0]);
        });
    };

    service.submitJob = function(values) {
        values = angular.extend({}, values, {
            'queue': 'default',
            'query_language': 'mysql'
        });
        return resources.jobs.save(values).$promise;
    };

    service.renameJob = function() {

    };

    service.killJob = function() {

    };

    service.removeJob = function() {

    };

    return service;

}]);
