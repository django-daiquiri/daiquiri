var app = angular.module('examples', ['list', 'infinite-scroll']);

app.factory('ExamplesService', ['$resource', '$timeout', 'ListService', function($resource, $timeout, ListService) {

    /* get the base url */

    var baseurl = angular.element('meta[name="baseurl"]').attr('content');

    /* configure resources */

    var resources = {
        examples: $resource(baseurl + 'query/api/examples/:id/'),
        accesslevels: $resource(baseurl + 'metadata/api/accesslevels/:id/'),
        querylanguages: $resource(baseurl + 'query/api/querylanguages/'),
        groups: $resource(baseurl + 'auth/api/groups/:id/'),
    }

    /* configure factories */

    var factories = {
        examples: function(){
            return {
                groups: []
            };
        }
    };

    /* init the list service */

    ListService.init(resources.examples);

    /* create the messages service */

    var service = {
        list: ListService
    };

    service.init = function() {
        service.accesslevels = resources.accesslevels.query();
        service.query_languages = resources.querylanguages.query();

        resources.groups.query(function(response) {
            service.groups = response;
            service.groups_map = {};
            angular.forEach(response, function(group){
                service.groups_map[group.id] = group.name;
            });
        });
    };

    service.modal = function(modal_id, index) {
        service.errors = {};

        if (angular.isUndefined(index)) {
            service.current_row = factories.examples();
        } else {
            service.current_index = index;
            service.current_row = angular.copy(service.list.rows[index]);
            service.errors = {};
        }

        $('#' + modal_id).modal('show');

        $timeout(function() {
            if (angular.element('#' + modal_id + ' .CodeMirror').length) {
                angular.element('#' + modal_id + ' .CodeMirror')[0].CodeMirror.refresh();
            }
        });
    };

    service.storeExample = function() {
        service.errors = {};

        var promise;
        if (angular.isDefined(service.current_row.id) && service.current_row.id) {
            promise = resources.examples.update({id: service.current_row.id}, service.current_row, function(response) {
                // copy the data back to the rows array and close the modal
                service.list.rows[service.current_index] = response;
            }).$promise;
        } else {
            promise = resources.examples.save(service.current_row, function() {
                // reload the list
                service.list.params.page = 1;
                service.list.fetch();
            }).$promise;
        }

        promise.then(function() {
            $('.modal').modal('hide');
        }, function(result) {
            service.errors = result.data;
        })
    };

    service.deleteExample = function() {
        resources.examples.delete({id: service.current_row.id}, function() {
            service.list.rows.splice(service.current_index, 1);

            $('.modal').modal('hide');
        });
    };

    return service;
}]);

app.controller('ExamplesController', ['$scope', 'ExamplesService', function($scope, ExamplesService) {

    $scope.service = ExamplesService;
    $scope.service.init();

}]);
