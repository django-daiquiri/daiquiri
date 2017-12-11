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
        var files = [];
        angular.forEach(service.table.checked, function(value, key) {
            if (value) {
                files.push(key);
            }
        })

        if (files.length) {
            service.start_download(files)
        }
    }

    service.download_all = function() {
        // var url = zip_url + '?all=';

        // var search = service.table.params.search;
        // if (search) {
        //     url += '&search=' + search;
        // }

        // console.log(url);
    }

    service.start_download = function(files) {
        service.download_failed = false;

        $http.post(archive_url, files).then(function(result) {
            var download_id = result.data.id;

            service.pending_downloads++;
            PollingService.register(download_id, service.poll_download, {
                download_id: download_id
            });
        }, function() {
            // display error message
            service.download_failed = true;
        });
    };

    service.poll_download = function(options) {
        console.log(options);
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
