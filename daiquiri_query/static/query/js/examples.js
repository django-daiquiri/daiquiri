var app = angular.module('examples', ['core', 'infinite-scroll']);

app.config(['$httpProvider', '$interpolateProvider', function($httpProvider, $interpolateProvider) {
    $interpolateProvider.startSymbol('{$');
    $interpolateProvider.endSymbol('$}');
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
}]);

// throttle/debounce the frequency of infinite-scroll events
angular.module('infinite-scroll').value('THROTTLE_MILLISECONDS', 100);

app.factory('ExamplesService', ['$http', '$timeout', function($http, $timeout) {

    // the url under which the profiles api is located
    var resource_url = '/query/api/examples/';

    var service = {};

    function fetchExamples() {

        return $http.get(service.current_url)
            .success(function(response) {
                service.count = response.count;
                service.next = response.next;
                service.rows = service.rows.concat(response.results);
            });
    }


    function storeExample(action) {
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
        console.log('init')
        service.current_url = resource_url;
        console.log(resource_url)
        // reset data
        service.search_string = null;
        service.rows = [];

        // fetch the first set of profiles
        fetchExamples();
    };

    service.search = function() {
        // reset the url and add the search string
        service.current_url = resource_url + '?search=' + service.search_string;

        // reset data
        service.rows = [];

        // fetch the profiles with the search parameter
        fetchExamples();
    };

    service.scroll = function() {
        if (service.next_url) {
            // set the url to next and invalidate next so this code will not be triggered again
            service.url = service.next_url;
            service.next_url = null;

            // fetch the profiles with the next url
            fetchExamples()
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


     service.storeExample = function(row) {

        console.log('storeExample')
        console.log(row)
        service.errors = {};
        if (row.id != null) {
            return $http.put(resource_url + row.id + '/', row)
        } else {
            return $http.post(resource_url, row)
        }
    };

    service.deleteExample = function(row) {

        return $http.put(resource_url + row.id + '/' + 'delete', row)
    };

    return service;
}]);

app.controller('ExamplesController', ['$scope', 'ExamplesService', function($scope, ExamplesService) {

    $scope.service = ExamplesService;
    $scope.service.init();

}]);