app.factory('SimbadService', ['$http', function($http) {

    /* get the base url */

    var service = {
        values: {},
        errors: []
    };

    service.query = function() {
        var url = 'http://simbad.u-strasbg.fr/simbad/sim-id';

        $http.get(url, {
            params: {
                'Ident': service.values.query,
                'output.format': 'votable',
                'output.params': 'main_id,coo(d),otype(V)'
            }
        }).success(function(response) {
            service.results = [];
            service.errors = [];

            // parse votable output
            xmlDoc = $.parseXML(response);
            $xml = $(xmlDoc);
            rows = $xml.find('TABLEDATA TR');

            if (rows.length) {
                rows.each(function() {
                    elements = $(this).find('TD');
                    service.results.push({
                        object: elements.eq(0).text(),
                        type: elements.eq(6).text(),
                        ra: elements.eq(1).text(),
                        de: elements.eq(2).text(),
                    });
                });
            } else {
                service.errors.push('Object not found.')
            }
        });
    };

    return service;
}]);
