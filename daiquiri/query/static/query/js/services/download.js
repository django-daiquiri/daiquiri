app.factory('DownloadService', ['$http', 'PollingService', function($http, PollingService) {

    /* get the base url */

    var baseurl = angular.element('meta[name="baseurl"]').attr('content');

    var base_download_url = baseurl + 'query/api/jobs/';
    var base_archive_url = baseurl + 'serve/archives/';

    var service = {
        pending_downloads: 0
    };

    service.download = function(job, format) {
        job.download_failed = false;

        var url = encodeURI(base_download_url + job.id + '/download/' + format + '/');
        $http.put(url)
            .then(function(result) {
                if (result.data == 'SUCCESS') {
                    service.unregister(url);

                    // append iframe
                    angular.element('body').append('<iframe style="display: none;" src="' + url + '"></iframe>');

                } else {
                    service.register(url, service.poll_download, {
                        'job': job,
                        'format': format
                    });
                }

            }, function() {
                // display error message
                job.download_failed = true;

                service.unregister(url);
            });
    };

    service.archive = function(job, column_name) {
        job.download_failed = false;

        var url = encodeURI(base_archive_url + job.database_name + '/' +  job.table_name +  '/' + column_name + '/');
        $http.put(url)
            .then(function(result) {
                if (result.data == 'SUCCESS') {
                    service.unregister(url);

                    // append iframe
                    angular.element('body').append('<iframe style="display: none;" src="' + url + '"></iframe>');

                } else {
                    service.register(url, service.poll_archive, {'job': job, 'column_name': column_name });
                }

            }, function() {
                // display error message
                job.download_failed = true;

                service.unregister(url);
            });
    };

    service.register = function(polling_id, method, options) {
        if (!PollingService.isRegistered(polling_id)) {
            // add download to pending downloads
            service.pending_downloads++;

            // add download to PollingService
            PollingService.register(polling_id, method, options);
        }
    };

    service.unregister  = function(polling_id) {
        if (PollingService.isRegistered(polling_id)) {
            // remove download from pending downloads
            service.pending_downloads--;

            // remove download from PollingService
            PollingService.unregister(polling_id);
        }
    };

    service.poll_download = function(options) {
        service.download(options.job, options.format);
    };

    service.poll_archive = function(options) {
        service.archive(options.job, options.column_name);
    };

    return service;
}]);
