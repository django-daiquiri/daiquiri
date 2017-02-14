app.factory('VizierService', ['$http', function($http) {

    /* get the base url */

    var service = {
        values: {},
        errors: [],
        catalogs: ['I/322A', 'I/259']
    };

    service.query = function() {
        var url = 'http://vizier.u-strasbg.fr/viz-bin/votable';

        $http.get(url, {
            params: {
                '-source': service.catalogs.join(' '),
                '-c': service.values.query,
                '-c.r': 2,
                '-out': '_RA _DEC _r *meta.id.part;meta.main *meta.id;meta.main',
                '-sort': '_r',
                '-out.max': 5
            }
        }).success(function(response) {
            service.results = [];
            service.errors = [];

            // parse votable output
            xmlDoc = $.parseXML(response);
            xml = $(xmlDoc);

            angular.forEach(service.catalogs, function(catalog) {
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
        });
    };

    return service;
}]);
