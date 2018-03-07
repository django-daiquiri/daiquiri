app.factory('DownloadService', ['$http', 'PollingService', function($http, PollingService) {

    /* get the base url */

    var baseurl = angular.element('meta[name="baseurl"]').attr('content');

    /* configure urls */

    var base_download_url = baseurl + 'query/api/jobs/';

    var service = {
        pending_downloads: 0
    };

    service.init = function(opt) {
        service.job = opt.job;

        service.archive_columns = [];

        angular.forEach(service.job.columns, function(column) {
            angular.forEach(['meta.note', 'meta.preview', 'meta.file'], function(key) {
                if (column.ucd && column.ucd.indexOf(key) > -1) {
                    service.archive_columns.push(column.name);
                }
            });
        });
    }

    service.start_download = function(format_key) {
        service.job.download_failed = false;

        var url = base_download_url + service.job.id + '/download/';
        $http.post(url, {
            format_key: format_key
        }).then(function(result) {
            var download_id = result.data.id;

            service.pending_downloads++;
            PollingService.register(download_id, service.poll_download, {
                job: service.job,
                download_id: download_id
            });
        }, function() {
            // display error message
            service.job.download_failed = true;
        });
    };

    service.poll_download = function(options) {
        var url = base_download_url + options.job.id + '/download/' + options.download_id + '/';
        $http.get(url + '?download=').then(function(result) {
            if (result.data == 'COMPLETED') {
                service.pending_downloads--;
                PollingService.unregister(options.download_id);

                // download the file, headers will prevent the browser reloading the page
                window.location.href = url;
            } else if (result.data == 'ERROR') {
                service.pending_downloads--;
                PollingService.unregister(options.download_id);

                // display error message
                options.job.download_failed = true;
            }
        }, function() {
            service.pending_downloads--;
            PollingService.unregister(options.download_id);

            // display error message
            options.job.download_failed = true;
        });
    };

    service.start_archive = function(column_name) {
        service.job.download_failed = false;

        var url = base_download_url + service.job.id + '/archive/';
        $http.post(url, {
            column_name: column_name
        }).then(function(result) {
            var archive_id = result.data.id;

            service.pending_downloads++;
            PollingService.register(archive_id, service.poll_archive, {
                job: service.job,
                archive_id: archive_id
            });
        }, function() {
            // display error message
            service.job.download_failed = true;
        });
    };

    service.poll_archive = function(options) {
        var url = base_download_url + options.job.id + '/archive/' + options.archive_id + '/';
        $http.get(url + '?download=').then(function(result) {
            if (result.data == 'COMPLETED') {
                service.pending_downloads--;
                PollingService.unregister(options.archive_id);

                // download the file, headers will prevent the browser reloading the page
                window.location.href = url;
            } else if (result.data == 'ERROR') {
                service.pending_downloads--;
                PollingService.unregister(options.download_id);

                // display error message
                options.job.download_failed = true;
            }
        }, function() {
            service.pending_downloads--;
            PollingService.unregister(options.archive_id);

            // display error message
            options.job.download_failed = true;
        });
    };

    return service;
}]);
