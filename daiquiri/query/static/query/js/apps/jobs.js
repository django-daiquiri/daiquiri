var app = angular.module('jobs', ['core', 'infinite-scroll']);

app.controller('JobsController', ['$scope', 'JobsService', function($scope, JobsService) {

    $scope.service = JobsService;
    $scope.service.init();

}]);
