angular.module('core', ['ngResource', 'ngSanitize'])

.config(['$httpProvider', '$interpolateProvider', '$resourceProvider', function($httpProvider, $interpolateProvider, $resourceProvider) {

    $interpolateProvider.startSymbol('{$');
    $interpolateProvider.endSymbol('$}');

    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';

    $resourceProvider.defaults.stripTrailingSlashes = false;
    $resourceProvider.defaults.actions.update = {
        method: 'PUT',
        params: {}
    };
    $resourceProvider.defaults.actions.paginate = {
        method: 'GET',
        isArray: false
    };
}])

.directive('codemirror', function() {
    return {
        scope: {
            id: '@',
            model: '='
        },
        require: 'ngModel',
        link: function(scope, element, attrs, ngModel) {
            // instanciate CodeMirror on the element
            scope.editor = CodeMirror.fromTextArea(element[0], {
                lineNumbers: true,
                lineWrapping: true,
                mode: attrs.mode
            });

            // whenever the user types into code mirror update the model
            scope.editor.on('change', function(cm, change) {
                ngModel.$setViewValue(cm.getValue());
            });

            // // when the model is updated update codemirror
            ngModel.$formatters.push(function(model_values) {

                if (angular.isDefined(model_values) && model_values) {
                    scope.editor.setValue(model_values);
                } else {
                    scope.editor.setValue('');
                }
                return model_values;
            });
        }
    };
})

.directive('pending', ['$http', '$timeout', function ($http, $timeout) {
    return {
        restrict: 'E',
        template: '<i class="fa fa-circle-o-notch fa-spin fa-fw"></i>',
        link: function (scope, element, attrs) {
            scope.isPending = function () {
                return $http.pendingRequests.length > 0;
            };
            scope.$watch(scope.isPending, function (value) {
                if (value) {
                    if (angular.isUndefined(scope.promise) || scope.pending === null) {
                        scope.promise = $timeout(function(){
                            element.removeClass('ng-hide');
                        }, 500);
                    }
                } else {
                    $timeout.cancel(scope.promise);
                    scope.pending = null;
                    element.addClass('ng-hide');
                }
            });
        }
    };
}]);
