angular.module('serve_table', ['core'])

.controller('ServeTableController', ['$scope', 'TableService', function($scope, TableService) {

    $scope.table = TableService;

}]);
