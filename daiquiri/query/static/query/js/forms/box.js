app.factory('BoxFormService', ['QueryService', function(QueryService) {

    var service = {
        values: {
            x_min: 0.0,
            x_max: 50.0,
            y_min: 0.0,
            y_max: 50.0,
            z_min: 0.0,
            z_max: 20.0
        },
        errors: {}
    };

    service.activate = function() {
        QueryService.activate_form('box');
    };

    service.submit = function() {
        service.values.query = 'SELECT x, y, z FROM daiquiri_data_sim.particles WHERE x BETWEEN ' + service.values.x_min + ' AND ' + service.values.x_max + ' AND y BETWEEN ' + service.values.x_min + ' AND ' + service.values.y_max + ' AND z BETWEEN ' + service.values.z_min + ' AND ' + service.values.z_max  ;
        service.values.query_language = 'adql-2.0';

        QueryService.submit_job(service.values)
            .then(function() {
                // success
                service.errors = {};

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
