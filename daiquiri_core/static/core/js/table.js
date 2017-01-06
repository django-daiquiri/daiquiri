angular.module('core')

.directive('daiquiriTable', ['TableService', function(TableService) {
    return {
        templateUrl: function(element, attrs) {
            var staticurl = angular.element('meta[name="staticurl"]').attr('content');
            return staticurl + 'core/html/table.html';
        },
        link: function (scope, element, attrs) {
            scope.table = TableService;

            if (angular.isDefined(attrs.database) && angular.isDefined(attrs.table)) {
                TableService.init(attrs.database, attrs.table);
            }
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
            page_size: 10,
            filter: null
        },
        i18n: {
            first: gettext('First'),
            previous: gettext('Previous'),
            next: gettext('Next'),
            last: gettext('Last'),
            reset: gettext('Reset'),
            filter: gettext('Filter'),
            count: function() {
                var page_count = Math.ceil(service.count / service.config.page_size);
                if (service.config.filter) {
                    return interpolate(gettext('Page %s of %s (%s rows total, filtering for "%s")'), [service.config.page,page_count, service.count, service.config.filter]);
                } else {
                    return interpolate(gettext('Page %s of %s (%s rows total)'), [service.config.page,page_count, service.count]);
                }
            },
            page_size: function(value) {
                return interpolate(gettext('Show %s of %s rows'), [value, service.count]);
            }
        },
        search_string: null
    };

    service.init = function(database, table) {
        service.config.database = database;
        service.config.table = table;
        service.config.filter = null;
        service.filter_string = null;

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
        service.config.page = Math.ceil(service.count / service.config.page_size);
        service.fetch();
    };

    service.reset = function() {
        service.config.page = 1;
        service.config.filter = null;
        service.filter_string = null;
        service.fetch();
    };

    service.filter = function() {
        service.config.filter = service.filter_string;
        service.fetch();
    };

    return service;
}]);
