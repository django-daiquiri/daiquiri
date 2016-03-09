var app = angular.module('users', []);

app.factory('UsersService', ['$http', function($http) {

    console.log('UsersService');

    return {

    };
}]);

app.controller('UsersController', ['$scope', 'UsersService', function($scope, UsersService) {

}]);
