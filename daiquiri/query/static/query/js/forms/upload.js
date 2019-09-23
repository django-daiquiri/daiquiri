app.factory('UploadFormService', ['$http', '$timeout', '$filter', 'QueryService', function($http, $timeout, $filter, QueryService) {

    /* create the form service */

    var service = {
        values: {},
        errors: {}
    };

    /* create and configure the browser service */

    service.activate = function() {
        QueryService.activate_form('upload');
    };

    service.submit = function() {
        QueryService.upload_job(service.values)
            .then(function() {
                // service.errors
            }, function (response) {
                if (response.status == 400) {
                    service.errors = response.data;
                } else {
                    service.errors = {
                        server_error: true
                    };
                }
            });
    };

    return service;
}]);
