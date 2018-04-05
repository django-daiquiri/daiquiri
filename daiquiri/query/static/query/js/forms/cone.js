app.factory('ConeFormService', ['QueryService', function(QueryService) {

    var service = {
        values: {
            ra: 0.0,
            de: 0.0,
            radius: 10.0
        },
        errors: {}
    };

    service.activate = function() {
        QueryService.activate_form('cone');
    };

    service.submit = function() {
        service.values.query = 'SELECT ra, de FROM daiquiri_data_obs.stars WHERE SQRT(POWER(ra - ' + service.values.ra + ', 2) + POWER(de - ' + service.values.de + ', 2)) <= ' + service.values.radius / 60.0 / 60.0;
        service.values.query_language = 'adql-2.0';

        QueryService.submit_job(service.values)
            .then(function() {
                // success
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
