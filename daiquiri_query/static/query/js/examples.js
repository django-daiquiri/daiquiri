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

    service.init = function() {
        // reset the url
        service.current_url = resource_url;

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

    service.updateExample = function(row) {

        service.errors = {};

        return $http.put(resource_url + row.id + '/', row)
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