var app = angular.module('users', []);

app.config(['$httpProvider', '$interpolateProvider', function($httpProvider, $interpolateProvider) {
    $interpolateProvider.startSymbol('{$');
    $interpolateProvider.endSymbol('$}');
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
}]);

app.factory('UsersService', ['$http', '$timeout', function($http, $timeout) {

    var data = {
        profiles: [],
        profile: {},
        errors: {}
    };

    function fetchProfiles() {
        $http.get('/auth/api/profiles/')
            .success(function(response) {
                data.profiles = response.results;
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
        data.profile.user.is_active = !data.profile.user.is_active;
        $http.put('/auth/api/profiles/' + data.profile.id + '/', data.profile)
            .success(function(response) {
                fetchProfiles();
                $timeout(function() {
                    $('#toggle-user-modal').modal('hide');
                });
            })
            .error(function(response) {
                console.log('error');
                console.log(response);
            });
    }

    fetchProfiles();

    return {
        data: data,
        showUserModal: showUserModal,
        updateUserModal: updateUserModal,
        updateUser: updateUser,
        toggleUserModal: toggleUserModal,
        toggleUser: toggleUser
    };
}]);

app.controller('UsersController', ['$scope', 'UsersService', function($scope, UsersService) {

    $scope.service = UsersService;

}]);
