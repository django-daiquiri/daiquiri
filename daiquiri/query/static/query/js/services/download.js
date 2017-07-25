app.factory('DownloadService', ['$http', 'FileSaver', 'Blob', 'PollingService', function($http, FileSaver, Blob, PollingService) {

    /* get the base url */

    var baseurl = angular.element('meta[name="baseurl"]').attr('content');

    function getPollingId(job, format) {
        return 'download-' + job.id + '-' + format;
    }

    var service = {
        pending_downloads: 0
    };

    service.download = function(job, format) {
        job.download_failed = false;

        var url = baseurl + 'query/api/jobs/' + job.id + '/download/' + format + '/';
        $http.put(url)
            .then(function(result) {
                if (result.data == 'SUCCESS') {
                    service.unregister(job, format);

                    // append iframe
                    angular.element('body').append('<iframe style="display: none;" src="' + url + '"></iframe>');

                } else {
                    service.register(job, format);
                }

            }, function() {
                // display error message
                job.download_failed = true;

                service.unregister(job, format);
            });
    };

    service.register = function(job, format) {
        var polling_id = getPollingId(job, format);

        if (!PollingService.isRegistered(polling_id)) {
            service.pending_downloads++;

            PollingService.register(polling_id, service.check, {
                'format': format,
                'job': job
            });
        }
    };

    service.unregister  = function(job, format) {
        var polling_id = getPollingId(job, format);
        if (PollingService.isRegistered(polling_id)) {
            // remove download from pending downloads
            service.pending_downloads--;

            // remove download from PollingService
            PollingService.unregister(polling_id);
        }
    };

    service.check = function(options) {
        service.download(options.job, options.format);
    };

    return service;
}]);
