var app = angular.module('archive', ['core']);

app.factory('ArchiveService', ['$http', 'TableService', 'PollingService', function($http, TableService, PollingService) {

    /* get the base url */

    var baseurl = angular.element('meta[name="baseurl"]').attr('content');

    /* configure resources */

    var zip_url = baseurl + 'archive/api/files/zip/'

    /* create the messages service */

    var service = {
        table: TableService
    };

    service.init = function() {

    };

    service.get_id = function(row, column_index) {
        return row[0];
    }

    service.get_file_url = function(row, column_index) {
        return service.table.files_url + row[0];
    }

    service.download_checked = function() {
        var files = [];
        angular.forEach(service.table.checked, function(value, key) {
            if (value) {
                files.push(key);
            }
        })

        if (files.length) {
            console.log(files);
        }
    }

    service.download_all = function() {
        var url = zip_url + '?all=';

        var search = service.table.params.search;
        if (search) {
            url += '&search=' + search;
        }

        console.log(url);
    }

    return service;
}]);

app.controller('ArchiveController', ['$scope', 'ArchiveService', function($scope, ArchiveService) {

    $scope.service = ArchiveService;
    $scope.service.init();

}]);
