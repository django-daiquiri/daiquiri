angular.module('table', ['core'])

.controller('TableController', ['$scope', 'TableService', function($scope, TableService) {

    $scope.service = {
        table: TableService
    };

}]);
