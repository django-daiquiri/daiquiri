var app = angular.module('users', ['list', 'infinite-scroll']);

app.factory('UsersService', ['$resource', '$timeout', 'ListService', function($resource, $timeout, ListService) {

    /* get the base url */

    var baseurl = angular.element('meta[name="baseurl"]').attr('content');

    /* configure resources */

    var resources = {
        profiles: $resource(baseurl + 'auth/api/profiles/:id/:detail_route/'),
        groups: $resource(baseurl + 'auth/api/groups/:id/')
    }

    /* init the list service */

    ListService.init(resources.profiles);

    /* create the messages service */

    var service = {
        list: ListService
    };

    service.init = function() {
        service.groups = resources.groups.query();
    };

    service.modal = function(modal_id, index) {
        service.current_index = index;
        service.current_row = angular.copy(service.list.rows[index]);
        service.errors = {};

        $timeout(function() {
            $('#' + modal_id).modal('show');
        });
    };

    service.store_profile = function(action) {
        service.errors = {};

        resources.profiles.update({
            id: service.current_row.id,
            detail_route: action
        }, service.current_row, function(response) {
            // copy the data back to the rows array and close the modal
            service.list.rows[service.current_index] = response;

            $('.modal').modal('hide');
        }, function(result) {
            service.errors = result.data;
        });
    };

    return service;
}]);

app.controller('UsersController', ['$scope', 'UsersService', function($scope, UsersService) {

    $scope.service = UsersService;
    $scope.service.init();

}]);
