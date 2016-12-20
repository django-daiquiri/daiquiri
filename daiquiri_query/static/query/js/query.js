angular.module('query', ['core'])

.filter('bytes', function() {
    return function(bytes) {
        if (angular.isUndefined(bytes) || isNaN(parseFloat(bytes)) || !isFinite(bytes)) return '';
        if (bytes === 0 || bytes === '0' ) return '0 bytes';

        var units = ['bytes', 'kB', 'MB', 'GB', 'TB', 'PB'];
        var number = Math.floor(Math.log(bytes) / Math.log(1024));

        return (bytes / Math.pow(1024, Math.floor(number))).toFixed(1) +  ' ' + units[number];
    };
})

.factory('QueryService', ['$resource', function($resource) {

    /* get the base url */

    var baseurl = angular.element('meta[name="baseurl"]').attr('content');

    /* configure resources */

    var resources = {
        jobs: $resource(baseurl + 'query/api/jobs/:id/'),
        databases: $resource(baseurl + 'query/api/databases/'),
        functions: $resource(baseurl + 'query/api/functions/'),
    };

    /* configure factories */

    var factories = {
        'jobs': {
            'queue': 'default',
            'query_language': 'mysql'
        }
    };

    /* create the query service */

    var service = {
        values: {},
        errors: {}
    };

    service.init = function() {
        service.jobs = resources.jobs.query();
        service.activateForm('sql');
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

    service.submitJob = function(key) {

        service.errors[key] = {};

        var values = angular.extend({}, service.values[key], factories.jobs);

        resources.jobs.save(values).$promise
            .then(function (response) {
            }, function (response) {
                service.errors[key] = response.data;

                var editor = $('.CodeMirror')[0].CodeMirror;
                var positions = angular.fromJson(service.errors.sql.query.positions);
                angular.forEach(positions, function(position) {
                    editor.markText(
                        {line: position[0] - 1, ch: position[1]},
                        {line: position[0] - 1, ch: position[1] + position[2].length},
                        {className: 'codemirror-error'},
                        {clearOnEnter: true}
                    );
                });
            });
    };

    service.renameJob = function() {

    };

    service.killJob = function() {

    };

    service.removeJob = function() {

    };

    return service;

}])

.controller('QueryController', ['$scope', 'QueryService', function($scope, QueryService) {

    $scope.service = QueryService;
    $scope.service.init();

}]);
