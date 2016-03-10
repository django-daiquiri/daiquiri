var app = angular.module('users', []);

app.config(['$httpProvider', function($httpProvider) {
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
}]);

app.factory('UsersService', ['$http', '$timeout', function($http, $timeout) {

    var data = {
        users: [],
        user: {},
        errors: {}
    };

    function fetchUsers() {
        $http.get('/auth/api/users/')
            .success(function(response) {
                data.users = response.results;
            })
            .error(function() {
                console.log('error');
            });
    }

    function fetchUser(user_id) {
        $http.get('/auth/api/users/' + user_id)
            .success(function(response) {
                data.user = response;
            })
            .error(function() {
                console.log('error');
            });
    }

    function showUpdateUser(user_id) {
        fetchUser(user_id);
        $timeout(function() {
            $('#update-user-modal').modal('show');
        });
    }

    function submitUpdateUser() {
        $http.put('/auth/api/users/' + data.user.id + '/', data.user)
            .success(function(response) {
                fetchUsers();
                $timeout(function() {
                    $('#update-user-modal').modal('hide');
                });
            })
            .error(function(response) {
                console.log('error');
                console.log(response);
            });
    }

    fetchUsers();

    return {
        data: data,
        showUpdateUser: showUpdateUser,
        submitUpdateUser: submitUpdateUser
    };
}]);

app.controller('UsersController', ['$scope', 'UsersService', function($scope, UsersService) {

    $scope.service = UsersService;

}]);
