var app = angular.module('query', ['core']);

app.directive('submitting', ['$timeout', function ($timeout) {
    return {
        restrict: 'E',
        template: '<i class="daiquiri-query-submitting fa fa-circle-o-notch fa-spin fa-fw"></i>',
        link: function (scope, element, attrs) {
            scope.timeout = null;
            scope.isActive = function () {
                return scope.service.submitting;
            };
            scope.$watch(scope.isActive, function (value) {
                if (value) {
                    if (scope.timeout === null) {
                        scope.timeout = $timeout(function(){
                            $('.daiquiri-query-submitting').removeClass('ng-hide');
                        }, 500);
                    }
                } else {
                    $('.daiquiri-query-submitting').addClass('ng-hide');
                    $timeout.cancel(scope.timeout);

                    scope.timeout = null;
                }
            });
        }
    };
}]);

app.controller('QueryController', ['$scope', 'QueryService', function($scope, QueryService) {

    $scope.service = QueryService;
    $scope.service.init();


    $('.daiquiri-query-dropdowns .dropdown-menu').on('click', function(event) {
        event.stopPropagation();
    })
    $scope.$on('browserDblItemClicked', function(event, resource, item) {
        $scope.service.forms.sql.paste_item(resource, item);
    });
}]);
