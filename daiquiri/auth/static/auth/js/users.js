var app = angular.module('users', ['core', 'infinite-scroll']);

app.config(['$httpProvider', '$interpolateProvider', function($httpProvider, $interpolateProvider) {
    $interpolateProvider.startSymbol('{$');
    $interpolateProvider.endSymbol('$}');
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
}]);

// throttle/debounce the frequency of infinite-scroll events
angular.module('infinite-scroll').value('THROTTLE_MILLISECONDS', 100);

app.factory('UsersService', ['$http', '$timeout', function($http, $timeout) {

    // the url under which the profiles api is located
    var resource_url = '/auth/api/profiles/';

    var service = {
        current_url: null,
        next_url: null
    };

    function fetchProfiles() {
        return $http.get(service.current_url)
            .success(function(response) {
                service.count = response.count;
                service.next = response.next;
                service.rows = service.rows.concat(response.results);
            });
    }

    function storeProfile(action) {
        service.errors = {};

        if (angular.isUndefined(action)) {
            action = '/';
        } else {
            action = '/' + action + '/';
        }

        return $http.put(resource_url + service.current_row.id + action, service.current_row)
            .success(function(response) {
                // copy the data back to the rows array and close the modal
                service.rows[service.current_index] = response;
            })
            .error(function(response, status) {
                service.errors = response;
            });
    }

    service.init = function() {
        // reset the url
        service.current_url = resource_url;

        // reset data
        service.search_string = null;
        service.rows = [];

        // fetch the first set of profiles
        fetchProfiles();
    };

    service.search = function() {
        // reset the url and add the search string
        service.current_url = resource_url + '?search=' + service.search_string;

        // reset data
        service.rows = [];

        // fetch the profiles with the search parameter
        fetchProfiles();
    };

    service.scroll = function() {
        if (service.next_url) {
            // set the url to next and invalidate next so this code will not be triggered again
            service.url = service.next_url;
            service.next_url = null;

            // fetch the profiles with the next url
            fetchProfiles();
        }
    };

    service.modal = function(modal_id, index) {
        service.current_index = index;
        service.current_row = angular.copy(service.rows[index]);
        service.errors = {};

        $timeout(function() {
            $('#' + modal_id).modal('show');
        });
    };

    service.updateUser = function() {
        storeProfile().then(function() {
            $('#update-user-modal').modal('hide');
        });
    };

    service.confirmUser = function() {
        storeProfile('confirm').then(function() {
            $('#confirm-user-modal').modal('hide');
        });
    };

    service.activateUser = function() {
        storeProfile('activate').then(function() {
            $('#activate-user-modal').modal('hide');
        });
    };

    service.disableUser = function() {
        storeProfile('disable').then(function() {
            $('#disable-user-modal').modal('hide');
        });
    };

    service.enableUser = function() {
        storeProfile('enable').then(function() {
            $('#enable-user-modal').modal('hide');
        });
    };

    return service;
}]);

app.controller('UsersController', ['$scope', 'UsersService', function($scope, UsersService) {

    $scope.service = UsersService;
    $scope.service.init();

}]);
