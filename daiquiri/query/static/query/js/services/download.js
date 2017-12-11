app.factory('DownloadService', ['$http', 'PollingService', function($http, PollingService) {

    /* get the base url */

    var baseurl = angular.element('meta[name="baseurl"]').attr('content');

    /* configure urls */

    var base_download_url = baseurl + 'query/api/jobs/';
    var base_archive_url = baseurl + 'serve/archives/';

    var service = {
        pending_downloads: 0
    };

    service.start_download = function(job, format_key) {
        job.download_failed = false;

        var url = base_download_url + job.id + '/download/';
        $http.post(url, {
            format_key: format_key
        }).then(function(result) {
            var download_id = result.data.id;

            service.pending_downloads++;
            PollingService.register(download_id, service.poll_download, {
                job: job,
                download_id: download_id
            });
        }, function() {
            // display error message
            job.download_failed = true;
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
            }
        }, function() {
            service.pending_downloads--;
            PollingService.unregister(options.download_id);

            // display error message
            options.job.download_failed = true;
        });
    };

    service.start_zip = function(job, column_name) {

    };

    service.poll_zip = function(options) {

    };

    return service;
}]);
