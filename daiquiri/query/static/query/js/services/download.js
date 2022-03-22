app.factory('DownloadService', ['$http', '$resource', '$injector', 'PollingService', function($http, $resource, $injector, PollingService) {

    /* get the base url */

    var baseurl = angular.element('meta[name="baseurl"]').attr('content');

    /* configure resources */

    var resources = {
        downloads: $resource(baseurl + 'query/api/downloads/')
    };

    /* configure urls */

    var base_download_url = baseurl + 'query/api/jobs/';

    var service = {
        pending_downloads: 0
    };

    service.init = function(opt) {
        service.job = opt.job;

        // inject download services
        resources.downloads.query(function(response) {
            angular.forEach(response, function(download) {
                if (download.download_service) {
                    service[download.key] = $injector.get(download.download_service);
                }
            });
        });
    }

    service.start_download = function(download_key, params) {
        service.job.download_failed = false;

        var url = base_download_url + service.job.id + '/download/' + download_key + '/';
        $http.post(url, params).then(function(result) {
            var download_job_id = result.data.id;

            service.pending_downloads++;
            PollingService.register(download_job_id, service.poll_download, {
                download_key: download_key,
                job: service.job,
                download_job_id: download_job_id
            });
        }, function() {
            // display error message
            service.job.download_failed = true;
        });
    };

    service.poll_download = function(options) {
        var url = base_download_url + options.job.id + '/download/' + options.download_key + '/' + options.download_job_id + '/';
        $http.get(url + '?download=').then(function(result) {
            if (result.data == 'COMPLETED') {
                service.pending_downloads--;
                PollingService.unregister(options.download_job_id);

                // download the file, headers will prevent the browser reloading the page
                window.location.href = url;
            } else if (result.data == 'ERROR') {
                service.pending_downloads--;
                PollingService.unregister(options.download_job_id);

                // display error message
                options.job.download_failed = true;
            }
        }, function() {
            service.pending_downloads--;
            PollingService.unregister(options.download_job_id);

            // display error message
            options.job.download_failed = true;
        });
    };

    return service;
}]);
