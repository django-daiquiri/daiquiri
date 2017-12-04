angular.module('core')

.factory('TableService', ['$http', '$resource', '$q', '$document', '$timeout', '$rootScope', '$compile', '$templateCache',  function($http, $resource, $q, $document, $timeout, $rootScope, $compile, $templateCache) {

    /* get the base url */

    var baseurl = angular.element('meta[name="baseurl"]').attr('content');

    /* configure the resources */

    var resources = {};

    /* create the metadata service */

    var service = {
        params: {
            page: 1,
            page_size: 10,
            ordering: null,
            search: null
        },
        page_sizes: [10, 20, 100],
        search_string: null,
        files: false,
        active: {},
        modal: {},
        round: false
    };

    service.init = function(opt) {
        service.ready = false;

        // set up resources
        if (angular.isDefined(opt.rows_url)) {
            resources.rows = $resource(baseurl + opt.rows_url);
        }
        if (angular.isDefined(opt.columns_url)) {
            resources.columns = $resource(baseurl + opt.columns_url);
        }

        // setup files url and reference
        if (angular.isDefined(opt.files_url)) {
            service.files_url = baseurl + opt.files_url;
        }
        if (angular.isDefined(opt.references_url)) {
            service.references_url = baseurl + opt.references_url;
        }

        // update pages_sizes
        if (angular.isDefined(opt.page_sizes)) {
            service.page_sizes = opt.page_sizes;
            service.params.page_size = opt.page_sizes[0];
        }

        // setup initial column width and rounding of cells
        if (angular.isDefined(opt.column_widths)) {
            service.column_widths = opt.column_widths;
        }
        if (angular.isDefined(opt.column_round)) {
            service.column_round = opt.column_round;
        }

        // add params from the dom to service.params and fetch the data
        if (angular.isDefined(opt.params)) {
            angular.extend(service.params, opt.params);

            resources.columns.query(service.params, function(response) {
                service.columns = response;

                // check column ucds for display mode
                angular.forEach(service.columns, function(column) {
                    // the default display mode is 'text'
                    column.display = 'text'

                    if (column.ucd) {
                        if (column.ucd.indexOf('meta.note') > -1) {
                            if (service.files_url) {
                                column.display = 'modal';
                            } else {
                                column.display = 'link';
                            }
                        } else if (column.ucd.indexOf('meta.preview') > -1) {
                            if (service.files_url) {
                                column.display = 'modal';
                            } else {
                                column.display = 'link';
                            }
                        } else if (column.ucd.indexOf('meta.file') > -1) {
                            if (service.files_url) {
                                column.display = 'file';
                            } else {
                                column.display = 'link';
                            }
                        } else if (column.ucd.indexOf('meta.ref') > -1) {
                            if (service.references_url) {
                                column.display = 'reference';
                            } else {
                                column.display = 'link';
                            }
                        } else if (column.ucd.indexOf('meta.ref.uri') > -1) {
                            column.display = 'link';
                        } else if (column.ucd.indexOf('meta.ref.url') > -1) {
                            column.display = 'link';
                        }
                    }
                });

                $timeout(function() {
                    var template = $templateCache.get('tooltip.html');

                    angular.forEach(service.columns, function(column, index) {
                        var isolated_scope = $rootScope.$new(true);
                        isolated_scope.column = column;
                        isolated_scope.table = service;

                        $('[data-column-index="' + index + '"] .info').popover({
                            title: '<strong>' + column.name + '</strong>',
                            content: $compile(template)(isolated_scope),
                            html: true,
                            trigger: 'hover',
                            placement: 'bottom',
                            container: '.daiquiri-table'
                        });
                    });

                    angular.forEach(service.column_widths, function(column_width, column_index) {
                        angular.element('[data-column-index="' + column_index + '"]').width(column_width);
                    });
                });

                service.reset();
            });
        }
    };

    service.clear = function() {
        service.columns = [];
        service.rows = [];
        service.ready = true;
    }

    service.fetch = function() {
        return resources.rows.paginate(service.params, function(response) {
            service.count = response.count;
            service.rows = response.results;

            service.page_count = Math.ceil(service.count / service.params.page_size);

            service.first_page = (service.params.page == 1);
            service.last_page = (service.params.page * service.params.page_size >= service.count);

            service.ready = true;
        }).$promise;
    };

    service.first = function() {
        if (!service.first_page) {
            service.params.page = 1;
            service.fetch();
        }
    };

    service.previous = function() {
        if (!service.first_page) {
            service.params.page -= 1;
            return service.fetch();
        }
    };

    service.next = function() {
        if (!service.last_page) {
            service.params.page += 1;
            return service.fetch();
        }
    };

    service.last = function() {
        if (!service.last_page) {
            service.params.page = Math.ceil(service.count / service.params.page_size);
            service.fetch();
        }
    };

    service.reset = function() {
        service.params.page = 1;
        service.params.ordering = null;
        service.params.search = null;
        service.search_string = null;
        service.fetch();
    };

    service.search = function() {
        service.params.search = service.search_string;
        service.fetch();
    };

    service.order = function(column_name) {
        if (service.params.ordering == column_name) {
            service.params.ordering = '-' + column_name;
        } else {
            service.params.ordering = column_name;
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

    service.activate = function(column_index, row_index) {
        service.active = {
            column_index: column_index,
            row_index: row_index
        }
    }

    service.modal_open = function(event, column_index, row_index) {
        event.preventDefault();
        event.stopPropagation();

        service.modal.pre = null;
        service.modal.src = null;

        service.activate(column_index, row_index);

        service.modal_update().then(function() {
            // add a litte delay to the modal so that a change in service.modal.src
            // does not make the image flicker/change in size after opening.
            $timeout(function() {
                $('#daiquiri-table-modal').modal('show');
            }, 100);
        })
    }

    service.modal_update = function() {
        var file_path = service.rows[service.active.row_index][service.active.column_index];
        var url = service.files_url + '?search=' + file_path;
        var column = service.columns[service.active.column_index];

        service.modal.title = file_path;

        if (column.ucd.indexOf('meta.note') > -1) {
            return $http.get(url).then(function(result) {
                service.modal.pre = result.data;
                service.modal.src = null;
            });
        } else if (column.ucd.indexOf('meta.preview') > -1) {
            service.modal.pre = null;
            service.modal.src = url;

            return $q.when();
        } else {
            return $q.when();
        }
    };

    service.modal_up = function() {
        if (service.active.row_index > 0) {
            // decrement the row_index and update modal
            service.active.row_index -= 1;
            service.modal_update();
        } else if (!service.first_page) {
            // first load previous page
            service.previous().then(function() {
                // set row_index to the last row and update modal
                service.active.row_index = service.rows.length - 1;
                service.modal_update();
            });
        }
    }

    service.modal_down = function() {
        if (service.active.row_index < service.rows.length - 1) {
            // increment the row_index and update modal
            service.active.row_index += 1;
            service.modal_update();
        } else if (!service.last_page) {
            // first load next page
            service.next().then(function() {
                // set row_index to 0 and update modal
                service.active.row_index = 0;
                service.modal_update();
            });
        }
    }

    service.modal_left = function() {
        var next_column_index = null,
            current_column_index = service.active.column_index;

        while(next_column_index === null) {
            if (current_column_index > 0) {
                current_column_index -= 1;
            } else {
                current_column_index = service.columns.length - 1;
            }

            var column = service.columns[current_column_index];
            if (column.ucd !== null && (column.ucd.indexOf('meta.note') > -1 || column.ucd.indexOf('meta.preview') > -1)) {
                next_column_index = current_column_index;
            }
        }

        service.active.column_index = current_column_index;
        service.modal_update();
    }

    service.modal_right = function() {
        var next_column_index = null,
            current_column_index = service.active.column_index;

        while(next_column_index === null) {
            if (current_column_index < service.columns.length - 1) {
                current_column_index += 1;
            } else {
                current_column_index = 0;
            }

            var column = service.columns[current_column_index];
            if (column.ucd !== null && (column.ucd.indexOf('meta.note') > -1 || column.ucd.indexOf('meta.preview') > -1)) {
                next_column_index = current_column_index;
            }
        }

        service.active.column_index = current_column_index;
        service.modal_update();
    }

    return service;
}]);
