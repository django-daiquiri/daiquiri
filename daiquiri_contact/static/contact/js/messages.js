var app = angular.module('messages', ['core', 'infinite-scroll']);

app.config(['$httpProvider', '$interpolateProvider', function($httpProvider, $interpolateProvider) {
    $interpolateProvider.startSymbol('{$');
    $interpolateProvider.endSymbol('$}');
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
}]);

// throttle/debounce the frequency of infinite-scroll events
angular.module('infinite-scroll').value('THROTTLE_MILLISECONDS', 100);

app.factory('MessagesService', ['$http', '$timeout', function($http, $timeout) {

    // the url under which the profiles api is located
    var resource_url = '/contact/api/messages/';

    var service = {};

    function fetchMessages() {
        return $http.get(service.current_url)
            .success(function(response) {
                console.log(response)
                service.count = response.count;
                service.next = response.next;
                service.rows = service.rows.concat(response.results);
            });
    }

    function storeMessage(action) {
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
        fetchMessages();
    };

    service.search = function() {
        // reset the url and add the search string
        service.current_url = resource_url + '?search=' + service.search_string;

        // reset data
        service.rows = [];

        // fetch the profiles with the search parameter
        fetchMessages();
    };

    service.scroll = function() {
        if (service.next_url) {
            // set the url to next and invalidate next so this code will not be triggered again
            service.url = service.next_url;
            service.next_url = null;

            // fetch the profiles with the next url
            fetchMessages();
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

    service.updateStatus = function() {
        storeMessages().then(function() {
            $('#setStatusClosed-messages-modal').modal('hide');
        });
    };

    service.updateMessage = function() {
        updateMessage().then(function() {
            $('#update-messages-modal').modal('hide');
        });
    };




    return service;
}]);

app.controller('MessagesController', ['$scope', 'MessagesService', function($scope, MessagesService) {

    $scope.service = MessagesService;
    $scope.service.init();

}]);
