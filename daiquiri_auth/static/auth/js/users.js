var app = angular.module('users', ['infinite-scroll']);

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
    var resourceUrl = '/auth/api/profiles/';

    var data = {
        url: null,
        next: null,
        count: null,
        search: null,
        rows: [],
        row: null,
        errors: {},
    };

    function fetchProfiles() {
        $http.get(data.url)
            .success(function(response) {
                data.count = response.count;
                data.next = response.next;
                data.rows = data.rows.concat(response.results);
            });
    }

    function init() {
        // reset the url
        data.url = resourceUrl;

        // reset data
        data.search = null;
        data.rows = [];

        // fetch the first set of profiles
        fetchProfiles();
    }

    function search() {
        // reset the url and add the search string
        data.url = resourceUrl + '?search=' + data.search;

        // reset data
        data.rows = [];

        // fetch the profiles with the search parameter
        fetchProfiles();
    }

    function scroll() {
        if (data.next) {
            // set the url to next and invalidate next so this code will not be triggered again
            data.url = data.next;
            data.next = null;

            // fetch the profiles with the next url
            fetchProfiles();
        }
    }

    function modal(modal_id, index) {
        data.index = index;
        data.row = angular.copy(data.rows[index]);

        $timeout(function() {
            $('#' + modal_id).modal('show');
        });
    }

    function updateUser() {
        $http.put(resourceUrl + data.row.id + '/', data.row)
            .success(function(response) {
                // copy the data back to the rows array and close the modal
                data.rows[data.index] = angular.copy(data.row);
                $('#update-user-modal').modal('hide');
            });
    }

    function toggleUser() {
        $('#toggle-user-modal').modal('hide');

        // toggle the is_active flag of the user
        data.row.user.is_active = !data.row.user.is_active;

        $http.put(resourceUrl + data.row.id + '/', data.row)
            .success(function(response) {
                // copy the data back to the rows array and close the modal
                data.rows[data.index] = angular.copy(data.row);
            });
    }

    return {
        data: data,
        init: init,
        search: search,
        scroll: scroll,
        modal: modal,
        updateUser: updateUser,
        toggleUser: toggleUser
    };
}]);

app.controller('UsersController', ['$scope', 'UsersService', function($scope, UsersService) {

    $scope.service = UsersService;
    $scope.service.init();

}]);
