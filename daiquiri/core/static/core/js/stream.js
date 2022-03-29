angular.module('stream', ['core'])

.factory('StreamService', ['$http', '$httpParamSerializer', function($http, $httpParamSerializer) {

    /* get the base url */

    var baseurl = angular.element('meta[name="baseurl"]').attr('content');

    /* create the metadata service */

    var service = {
        values: {},
        errors: {}
    };

    /* define service functions */

    service.init = function(opt) {
        service.stream_url = baseurl + opt.stream_url;
        service.defaults = opt.defaults;

        if (angular.isDefined(opt.resource)) {
            service.resource = opt.resource;
        }

        service.reset();
    };

    service.reset = function() {
        angular.forEach(service.defaults, function(value, key) {
            service.values[key] = value;
        });
    };

    service.download = function() {
        // construct the url for the stream
        var url = service.stream_url + '/' + service.resource + '/?' + $httpParamSerializer(service.values);

        $http.get(url + '&download=').then(function() {
            // download the file using an iframe
            var iframe = document.createElement('iframe');
            iframe.style.display = 'none';
            iframe.src = url;
            iframe.onload = function() {
              this.parentNode.removeChild(this)
            }
            document.body.appendChild(iframe)
        }, function(result) {
            service.errors = result.data;
        });
    }

    service.build_query_params = function() {
        service.query_params = $httpParamSerializer(service.values);
    }

    return service;
}])

.controller('StreamController', ['$scope', 'StreamService', function($scope, StreamService) {

    $scope.service = StreamService;
    $scope.$watch('service.values', $scope.service.build_query_params, true);

}]);
