angular.module('core', ['ngResource'])

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
