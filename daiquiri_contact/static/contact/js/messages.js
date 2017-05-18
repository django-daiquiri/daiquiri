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

    var service = {
     config: {
            ordering: null,
          }
    };

    var show_spam = true;

    var ordering = null;

    function fetchMessages() {
        return $http.get(service.current_url)
            .success(function(response) {
                service.count = response.count;
                service.next = response.next;
                service.rows = service.rows.concat(response.results);
            });
    }

    service.fetch = function() {
        resources.rows.paginate(service.config, function(response) {
            service.count = response.count;
            service.rows = response.results;
        });
    };

    service.init = function() {
        // reset the url
        service.current_url = resource_url;

        // reset data
        service.search_string = null;
        service.rows = [];
        service.show_spam = show_spam;
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

        service.errors = {};
        row.status = status;

        $http.get('/contact/api/status/?format=json').success(function(status_json) {
            for(i = 0; i < status_json.length; i++){
                if (status_json[i].id == status){
                    row.status_label = status_json[i].text
                }
            }
        });
        return $http.put(resource_url + row.id + '/', row)
    }

    service.showSpam = function(show_spam) {
        service.show_spam = show_spam;
        if (show_spam) {
            console.log(show_spam)
            console.log('I want to see spam')
            service.current_url = resource_url + '?search=' + 'spam';
            service.rows = [];
            fetchMessages();
        }
        else {
            console.log(show_spam)


            // reset data
            service.rows = [];

            // fetch the profiles with the search parameter
           fetchMessages();
        }
      };

    service.order = function(column_name) {
        if (service.config.ordering == column_name) {
            service.config.ordering = '-' + column_name;
        } else {
            service.config.ordering = column_name;
        }
        service.fetchMessages();
    };

    return service;
}]);

app.controller('MessagesController', ['$scope', 'MessagesService', function($scope, MessagesService) {

    $scope.service = MessagesService;
    $scope.service.init();

}]);
