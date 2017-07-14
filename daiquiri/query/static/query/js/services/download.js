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

        $http.put(baseurl + 'query/api/jobs/' + job.id + '/download/' + format + '/')
            .then(function(result) {
                var content_type = result.headers()['content-type'];

                if (content_type != 'application/json') {
                    service.unregister(job, format);

                    // get the filename from the Content-Disposition header
                    var content_disposition = result.headers()['content-disposition'];
                    var m = content_disposition.match(/filename[^;=\n]*=['"'](.*?[^'";\n]*)['"']/);
                    var filename = (m === null) ? 'download.dat' : m[1];

                    // store payload using angular-file-saver
                    var blob = new Blob([result.data], { type: content_type });
                    FileSaver.saveAs(blob, filename);

                    service.unregister(job, format);
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
