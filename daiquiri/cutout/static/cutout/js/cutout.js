angular.module('cutout', ['core'])

.factory('CutoutService', ['$httpParamSerializer', function($httpParamSerializer) {

    /* get the base url */

    var baseurl = angular.element('meta[name="baseurl"]').attr('content');

    /* get the cutout url */

    var cutout_url = baseurl + 'cutout/api/cutout';

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

    service.reset = function() {
        angular.forEach(service.defaults, function(value, key) {
            service.values[key] = value;
        });
    };

    service.download = function() {
        // construct the url for the cutout
        var url = cutout_url + '?' + $httpParamSerializer(service.values);

        // append iframe
        angular.element('body').append('<iframe style="display: none;" src="' + url + '"></iframe>');
    }

    return service;
}])

.controller('CutoutController', ['$scope', 'CutoutService', function($scope, CutoutService) {

    $scope.service = CutoutService;

}]);
