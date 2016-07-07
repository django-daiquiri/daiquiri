angular.module('core', ['ngResource'])

.config(['$httpProvider', '$interpolateProvider', function($httpProvider, $interpolateProvider) {
    $interpolateProvider.startSymbol('{$');
    $interpolateProvider.endSymbol('$}');
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
}])

.config(['$resourceProvider', function($resourceProvider) {
    $resourceProvider.defaults.stripTrailingSlashes = false;
    $resourceProvider.defaults.actions.update = {
        method: 'PUT',
        params: {}
    };
}]);
