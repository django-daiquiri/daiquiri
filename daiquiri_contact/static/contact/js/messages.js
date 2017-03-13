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
                service.count = response.count;
                service.next = response.next;
                service.rows = service.rows.concat(response.results);
            });
    }

    service.init = function() {
        // reset the url
        service.current_url = resource_url;

        console.log(resource_url)
        $http.get(service.current_url).success(function(response) {
                console.log(response);
                //service.rows = service.rows.concat(response.results);
            });
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

    service.updateMessage = function(row, status) {
        console.log('status:', status)
        console.log(row)

        //console.log(action)
        service.errors = {};
        row.status = status;

        $http.get('/contact/api/status/?format=json').success(function(status_json) {
            console.log(status_json)
            text = ""
            for(i = 0; i < status_json.length; i++){
                console.log(i)
                console.log(status_json[i])
                if (status_json[i].id == status){
                    row.status_label = status_json[i].text

                }
            }
        });
        return $http.put(resource_url + row.id + '/', row)
    }


    return service;
}]);

app.controller('MessagesController', ['$scope', 'MessagesService', function($scope, MessagesService) {

    $scope.service = MessagesService;
    $scope.service.init();

}]);
