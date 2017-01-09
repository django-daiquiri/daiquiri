angular.module('core')

.directive('daiquiriTable', ['$timeout', '$compile', '$templateCache', 'TableService', function($timeout, $compile, $templateCache, TableService) {
    return {
        templateUrl: function(element, attrs) {
            var staticurl = angular.element('meta[name="staticurl"]').attr('content');
            return staticurl + 'core/html/table.html';
        },
        scope: {
            'values': '='
        },
        link: function(scope, element, attrs) {
            scope.table = TableService;

            if (angular.isDefined(attrs.database) && angular.isDefined(attrs.table)) {
                TableService.init(attrs.database, attrs.table);
            }

            // refresh the tooltips everytime a new set of columns is fetched
            scope.$watch(function() {
                return angular.isDefined(scope.table.columns) && scope.table.columns.$resolved;
            }, function(new_value) {
                if (new_value) {
                    var template = $templateCache.get('tooltip.html');

                    $timeout(function() {
                        angular.forEach(scope.table.columns, function(column, index) {
                            var isolated_scope = scope.$new(true);
                            isolated_scope.column = column;
                            isolated_scope.table = scope.table;

                            $('[data-column-index="' + index + '"] .info').popover({
                                title: '<strong>' + column.name + '</strong>',
                                content: $compile(template)(isolated_scope),
                                html: true,
                                trigger: 'hover',
                                placement: 'bottom',
                                container: '.daiquiri-table'
                            });
                        });
                    });
                }
            });

        }
    };
}])

.factory('TableService', ['$resource', '$document', function($resource, $document) {

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
            ordering: null,
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
            },
            'description': gettext('Description'),
            'unit': gettext('Unit'),
            'ucd': gettext('UCD'),
            'datatype': gettext('Data type'),
            'size': gettext('Size'),
            'principal': gettext('Principal'),
            'indexed': gettext('Indexed'),
            'std': gettext('STD'),
        },
        search_string: null,
        updated: false
    };

    service.init = function(database, table) {
        service.config.database = database;
        service.config.table = table;

        service.columns = resources.columns.query(service.config);
        service.reset();
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
        service.config.ordering = null;
        service.config.filter = null;
        service.filter_string = null;
        service.fetch();
    };

    service.filter = function() {
        service.config.filter = service.filter_string;
        service.fetch();
    };

    service.order = function(column_name) {
        if (service.config.ordering == column_name) {
            service.config.ordering = '-' + column_name;
        } else {
            service.config.ordering = column_name;
        }
        service.fetch();
    };

    service.resize = function (column_index) {
        var zero = event.pageX;
        var table = angular.element('.daiquiri-table-pane .table');
        var th = angular.element('[data-column-index="' + column_index + '"]');
        var width = th.width();

        table.addClass('no-select');
        function enterResize(event) {
            var newWidth = width + event.pageX - zero;
            if (newWidth >= 40) th.width(newWidth);
        }

        function exitResize() {
            table.removeClass('no-select');
            $document.off('mousemove',enterResize);
            $document.off('mouseup',exitResize);
        }

        $document.on('mousemove', enterResize);
        $document.on('mouseup', exitResize);
    };

    return service;
}]);
