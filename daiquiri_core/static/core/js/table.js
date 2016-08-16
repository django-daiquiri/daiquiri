angular.module('core')

.directive('daiquiriTable', ['TableService', function(TableService) {
    return {
        templateUrl: function(element, attrs) {
            var staticurl = angular.element('meta[name="staticurl"]').attr('content');
            return staticurl + 'core/html/table.html';
        },
        link: function (scope, element, attrs) {
            scope.table = TableService;
            scope.table.init(attrs['database'], attrs['table']);
        }
    };
}])

.factory('TableService', ['$resource', '$timeout', '$filter', function($resource, $timeout, $filter) {

    /* get the base url */

    var baseurl = angular.element('meta[name="baseurl"]').attr('content');

    /* configure the resources */

    var resources = {
        rows: $resource(baseurl + 'serve/api/rows/'),
        columns: $resource(baseurl + 'serve/api/columns/'),
    };

    /* create the metadata service */

    var service = {
        config: {
            page: 1,
            page_size: 10
        }
    };

    service.init = function(database, table) {
        service.config.database = database;
        service.config.table = table;

        service.columns = resources.columns.query(service.config);

        service.fetch();
    };

    service.fetch = function() {
        resources.rows.paginate(service.config, function(response) {
            service.count = response.count;
            service.rows = response.results;
        });
    };

    service.first = function() {
        service.config.page = 1;
        service.fetch();
    };

    service.previous = function() {
        if (service.config.page > 1) {
            service.config.page -= 1;
            service.fetch();
        }
    };

    service.next = function() {
        if (service.config.page * service.config.page_size < service.count) {
            service.config.page += 1;
            service.fetch();
        }
    };

    service.last = function() {
        service.config.page = Math.floor(service.count / service.config.page_size);
        service.fetch();
    };

    return service;
}]);
