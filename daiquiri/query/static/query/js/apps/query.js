var app = angular.module('query', ['core']);

app.controller('QueryController', ['$scope', 'QueryService', function($scope, QueryService) {

    $scope.service = QueryService;
    $scope.service.init();


    $('.daiquiri-query-dropdowns .dropdown-menu').on('click', function(event) {
        event.stopPropagation();
    })
    $scope.$on('browserDblItemClicked', function(event, resource, item) {
        $scope.service.forms.sql.paste_iStem(resource, item);
    });
}]);
