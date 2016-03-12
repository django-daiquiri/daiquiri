var app = angular.module('users', ['infinite-scroll']);

app.config(['$httpProvider', '$interpolateProvider', function($httpProvider, $interpolateProvider) {
    $interpolateProvider.startSymbol('{$');
    $interpolateProvider.endSymbol('$}');
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
}]);

// throttle/debounce the frequency of infinite-scroll events
angular.module('infinite-scroll').value('THROTTLE_MILLISECONDS', 100)

app.factory('UsersService', ['$http', '$timeout', function($http, $timeout) {

    // the url under which the profiles api is located
    var resourceUrl = '/auth/api/profiles/';

    var data = {
        url: null,
        next: null,
        count: null,
        search: null,
        profiles: [],
        profile: {},
        errors: {},
    };

    function fetchProfiles() {
        $http.get(data.url)
            .success(function(response) {
                data.count = response.count;
                data.next = response.next;
                data.profiles = data.profiles.concat(response.results);
            })
            .error(function() {
                console.log('error');
            });
    }

    function fetchProfile(user_id) {
        $http.get('/auth/api/profiles/' + user_id)
            .success(function(response) {
                data.profile = response;
            })
            .error(function() {
                console.log('error');
            });
    }

    function init() {
        // reset the url
        data.url = resourceUrl;

        // reset data
        data.search = null;
        data.profiles = [];

        // fetch the first set of profiles
        fetchProfiles();
    }

    function search() {
        // reset the url and add the search string
        data.url = resourceUrl + '?search=' + data.search;

        // reset data
        data.profiles = [];

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

    function showUserModal(user_id) {
        fetchProfile(user_id);
        $timeout(function() {
            $('#show-user-modal').modal('show');
        });
    }

    function updateUserModal(user_id) {
        fetchProfile(user_id);
        $timeout(function() {
            $('#update-user-modal').modal('show');
        });
    }

    function updateUser() {
        $http.put('/auth/api/profiles/' + data.profile.id + '/', data.profile)
            .success(function(response) {
                fetchProfiles();
                $timeout(function() {
                    $('#update-user-modal').modal('hide');
                });
            })
            .error(function(response) {
                console.log('error');
                console.log(response);
            });
    }

    function toggleUserModal(user_id) {
        fetchProfile(user_id);
        $timeout(function() {
            $('#toggle-user-modal').modal('show');
        });
    }

    function toggleUser() {
        $('#toggle-user-modal').modal('hide');
        data.profile.user.is_active = !data.profile.user.is_active;
        $http.put('/auth/api/profiles/' + data.profile.id + '/', data.profile)
            .success(function(response) {
                fetchProfiles();
            })
            .error(function(response) {
                console.log('error');
                console.log(response);
            });
    }

    return {
        data: data,
        init: init,
        search: search,
        scroll: scroll,
        showUserModal: showUserModal,
        updateUserModal: updateUserModal,
        updateUser: updateUser,
        toggleUserModal: toggleUserModal,
        toggleUser: toggleUser
    };
}]);

app.controller('UsersController', ['$scope', 'UsersService', function($scope, UsersService) {

    $scope.service = UsersService;
    $scope.service.init();

}]);
