app.factory('SimbadDropdownService', ['$http', function($http) {

    /* get the base url */

    var service = {
        values: {},
        errors: []
    };

    service.query = function() {
        $http.get(service.options.url, {
            params: {
                'Ident': service.values.query,
                'output.format': 'votable',
                'output.params': 'main_id,coo(d),otype(V)'
            }
        }).then(function(result) {
            service.results = [];
            service.errors = [];

            // parse votable output
            xmlDoc = $.parseXML(result.data);
            $xml = $(xmlDoc);
            rows = $xml.find('TABLEDATA TR');

            rows.each(function() {
                elements = $(this).find('TD');
                service.results.push({
                    object: elements.eq(0).text(),
                    type: elements.eq(6).text(),
                    ra: elements.eq(1).text(),
                    de: elements.eq(2).text(),
                });
            });

            if (service.results.length == 0) {
                service.errors.push('Query retrieved no object.')
            }
        });
    };

    return service;
}]);
