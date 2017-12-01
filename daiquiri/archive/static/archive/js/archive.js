var app = angular.module('archive', ['core']);

app.factory('ArchiveService', ['$resource', '$timeout', 'TableService', function($resource, $timeout, TableService) {

    /* get the base url */

    var baseurl = angular.element('meta[name="baseurl"]').attr('content');

    /* configure resources */

    var resources = {

    }

    /* create the messages service */

    var service = {
        table: TableService
    };

    service.init = function() {

    };

    return service;
}]);

app.controller('ArchiveController', ['$scope', 'ArchiveService', function($scope, ArchiveService) {

    $scope.service = ArchiveService;
    $scope.service.init();

}]);
