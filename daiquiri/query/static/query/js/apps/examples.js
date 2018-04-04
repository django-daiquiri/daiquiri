var app = angular.module('examples', ['core', 'infinite-scroll']);

app.controller('ExamplesController', ['$scope', 'ExamplesService', function($scope, ExamplesService) {

    $scope.service = ExamplesService;
    $scope.service.init();

}]);
