var app = angular.module('jobs', ['core', 'infinite-scroll']);

app.factory('JobsService', ['$resource', '$timeout', 'ListService', function($resource, $timeout, ListService) {

    /* get the base url */

    var baseurl = angular.element('meta[name="baseurl"]').attr('content');

    /* configure resources */

    var resources = {
        jobs: $resource(baseurl + 'query/api/jobs/:id/:detail_route/'),
        phases: $resource(baseurl + 'query/api/phases/:id/')
    }

    /* create the service */

    var service = {
        list: ListService,
        selected: {},
        phase_map: {}
    };

    service.init = function(phases) {
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

        service.values = angular.copy(service.list.rows[index]);
        service.errors = {};

        $('#' + modal_id).modal('show');

        $timeout(function() {
            if (angular.element('#' + modal_id + ' .CodeMirror').length) {
                angular.element('#' + modal_id + ' .CodeMirror')[0].CodeMirror.refresh();
            }
        });
    };

    return service;
}]);

app.controller('JobsController', ['$scope', 'JobsService', function($scope, JobsService) {

    $scope.service = JobsService;
    $scope.service.init();

}]);
