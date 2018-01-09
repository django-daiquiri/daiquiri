var app = angular.module('archive', ['core']);

app.factory('ArchiveService', ['$http', 'TableService', 'PollingService', function($http, TableService, PollingService) {

    /* get the base url */

    var baseurl = angular.element('meta[name="baseurl"]').attr('content');

    /* configure resources */

    var archive_url = baseurl + 'archive/api/archives/'

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
        var file_ids = [];
        angular.forEach(service.table.checked, function(value, key) {
            if (value) {
                file_ids.push(key);
            }
        })

        if (file_ids.length) {
            service.start_download({
                file_ids: file_ids
            });
        }
    }

    service.download_all = function() {
        service.download_failed = false;

        service.start_download({
            search: service.table.params.search
        });
    }

    service.start_download = function(data) {
        service.download_failed = false;

        $http.post(archive_url, data).then(function(result) {
            var download_id = result.data.id;

            service.pending_downloads++;
            PollingService.register(download_id, service.poll_download, {
                download_id: download_id
            });
        }, function() {
            // display error message
            service.download_failed = true;
        });
    }

    service.poll_download = function(options) {
        var url = archive_url + options.download_id + '/';
        $http.get(url + '?download=').then(function(result) {
            if (result.data == 'COMPLETED') {
                service.pending_downloads--;
                PollingService.unregister(options.download_id);

                // download the file, headers will prevent the browser reloading the page
                window.location.href = url;
            }
        }, function() {
            service.pending_downloads--;
            PollingService.unregister(options.download_id);

            // display error message
            service.download_failed = true;
        });
    };

    return service;
}]);

app.controller('ArchiveController', ['$scope', 'ArchiveService', function($scope, ArchiveService) {

    $scope.service = ArchiveService;
    $scope.service.init();

}]);
