app.factory('VizierDropdownService', ['$http', function($http) {

    /* get the base url */

    var service = {
        values: {},
        errors: [],
    };

    service.query = function() {
        $http.get(service.options.url, {
            params: {
                '-source': service.options.catalogs.join(' '),
                '-c': service.values.query,
                '-c.r': 2,
                '-out': '_RA _DEC _r *meta.id.part;meta.main *meta.id;meta.main',
                '-sort': '_r',
                '-out.max': 5
            }
        }).then(function(result) {
            service.results = [];
            service.errors = [];

            // parse votable output
            xmlDoc = $.parseXML(result.data);
            xml = $(xmlDoc);

            angular.forEach(service.options.catalogs, function(catalog) {
                var catalog_xml = xml.find("RESOURCE[name='" + catalog + "']");

                catalog_xml.find("TABLEDATA TR").each(function() {
                    var fields = $(this).find('TD');

                    if (catalog == 'I/259') {
                        // hack for Tycho 2 catalog
                        var id = fields.eq(3).text() + '-' + fields.eq(4).text() + '-' + fields.eq(5).text();
                    } else {
                        var id = fields.eq(3).text();
                    }

                    service.results.push({
                        id: id,
                        ra: fields.eq(0).text(),
                        de: fields.eq(1).text(),
                        distance: fields.eq(2).text(),
                        catalog: catalog_xml.find("DESCRIPTION:first").text()
                    });
                });
            });

            if (service.results.length == 0) {
                service.errors.push('Query retrieved no object.')
            }
        });
    };

    return service;
}]);
