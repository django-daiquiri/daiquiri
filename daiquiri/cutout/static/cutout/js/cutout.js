angular.module('cutout', ['core'])

.factory('CutoutService', ['$http', '$httpParamSerializer', function($http, $httpParamSerializer) {

    /* get the base url */

    var baseurl = angular.element('meta[name="baseurl"]').attr('content');

    /* get the cutout url */

    var cutout_url = baseurl + 'cutout/api/datacubes';

    /* create the metadata service */

    var service = {
        values: {},
        errors: {}
    };

    /* define service functions */

    service.init = function(defaults) {
        service.defaults = defaults;
        service.reset();
    };

    service.reset = function() {
        angular.forEach(service.defaults, function(value, key) {
            service.values[key] = value;
        });
    };

    service.download = function() {
        // construct the url for the cutout
        var url = cutout_url + '?' + $httpParamSerializer(service.values);

        $http.get(url + '&download=').then(function() {
            // download the file, headers will prevent the browser reloading the page
            window.location.href = url;
        }, function(result) {
            service.errors = result.data;
        });
    }

    service.build_query_params = function() {
        service.query_params = $httpParamSerializer(service.values);
    }

    return service;
}])

.controller('CutoutController', ['$scope', 'CutoutService', function($scope, CutoutService) {

    $scope.service = CutoutService;
    $scope.$watch('service.values', $scope.service.build_query_params, true);

}]);
