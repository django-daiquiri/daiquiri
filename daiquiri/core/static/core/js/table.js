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
        active: {},
        modal: {},
        getter: {
            row_id: function(row) {
                return JSON.stringify(row);
            },
            file_url: function(row, column_index) {
                return service.files_url + row[column_index];
            },
            reference_url: function(row, column_index) {
                var key = service.columns[column_index].name,
                    value = row[column_index];

                return service.references_url + key + '/' + value + '/';
            },
            link_url: function(row, column_index) {
                return row[column_index];
            },
            datalink_url: function(row, column_index) {
                if (service.params.job) {
                    return service.datalink_url + row[column_index] + '?job=' + service.params.job;
                } else {
                    return service.datalink_url + row[column_index];
                }
            }
        }
    };

    service.init = function(opt) {
        service.ready = false;

        // set up resources and urls
        if (angular.isDefined(opt.rows_url)) {
            resources.rows = $resource(baseurl + opt.rows_url);
        }
        if (angular.isDefined(opt.columns_url)) {
            resources.columns = $resource(baseurl + opt.columns_url);
        }
        if (angular.isDefined(opt.files_url)) {
            service.files_url = baseurl + opt.files_url;
        }
        if (angular.isDefined(opt.references_url)) {
            service.references_url = baseurl + opt.references_url;
        }
        if (angular.isDefined(opt.datalink_url)) {
            service.datalink_url = baseurl + opt.datalink_url;
        }

        // update params
        if (angular.isDefined(opt.params)) {
            angular.extend(service.params, opt.params);
        }

        // set pages_sizes
        if (angular.isDefined(opt.page_sizes)) {
            service.page_sizes = opt.page_sizes;
            service.params.page_size = opt.page_sizes[0];
        }

        // set custom getter functions
        if (angular.isDefined(opt.getter)) {
            angular.forEach(opt.getter, function(func, key) {
                service.getter[key] = func;
            })
        }

        // set additional options
        angular.forEach(opt, function(value, key) {
            if ([
                'rows_url',
                'columns_url',
                'files_url',
                'references_url',
                'datalink_url',
                'params',
                'page_sizes',
                'getter'
            ].indexOf(key) == -1) {
                service[key] = opt[key];
            }
        });

        // add params from the dom to service.params and fetch the data
        if (angular.isUndefined(opt.fetch) || opt.fetch) {

            resources.columns.query(service.params, function(response) {
                service.columns = response;

                // check column ucds for display mode
                angular.forEach(service.columns, function(column) {
                    // the default display mode is 'text'
                    column.meta = 'text'

                    if (column.ucd) {
                        if (column.ucd.indexOf('meta.ref') > -1) {
                            if (column.ucd.indexOf('meta.note') > -1) {
                                column.meta = 'note';
                            } else if (column.ucd.indexOf('meta.image') > -1) {
                                column.meta = 'image';
                            } else if (column.ucd.indexOf('meta.file') > -1) {
                                column.meta = 'file';
                            } else if (column.ucd.indexOf('meta.ref.url') > -1) {
                                column.meta = 'link';
                            } else if (column.ucd.indexOf('meta.id') > -1) {
                                column.meta = 'datalink'
                            } else {
                                column.meta = 'reference';
                            }
                        }
                    }
                });

                if (service.tooltips) {
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
                    });
                }

                if (service.column_widths) {
                    $timeout(function() {
                        angular.forEach(service.column_widths, function(column_width, column_index) {
                            angular.element('[data-column-index="' + column_index + '"]').width(column_width);
                        });
                    });
                }

                service.reset();
            });
        }
    };

    service.clear = function() {
        service.columns = [];
        service.rows = [];
        service.ready = true;
    };

    service.fetch = function() {
        return resources.rows.paginate(service.params, function(response) {
            service.count = response.count;
            service.rows = response.results;

            service.page_count = Math.ceil(service.count / service.params.page_size);

            service.first_page = (service.params.page == 1);
            service.last_page = (service.params.page * service.params.page_size >= service.count);

            if (service.checkboxes) {
                service.update_checked_all();
            }

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
        service.checked = {};
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
    };

    service.check_all = function() {
        angular.forEach(service.rows, function(row) {
            service.checked[service.getter.id(row)] = service.checked_all;
        })
    };

    service.update_checked_all = function() {
        service.checked_all = service.rows.map(function(row) {
            return service.checked[service.getter.id(row)];
        }).every(function(element) {
            return element === true;
        });
    };


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
    };

    service.modal_update = function() {
        var column = service.columns[service.active.column_index];
        if (column.meta == 'datalink') {
            service.modal.url = service.getter.datalink_url(service.rows[service.active.row_index], service.active.column_index);
        } else {
            service.modal.url = service.getter.file_url(service.rows[service.active.row_index], service.active.column_index);
        }
        service.modal.title = service.rows[service.active.row_index][service.active.column_index];

        // compute up, down, left, right index
        service.modal.up_row_index = service.modal_up_row_index()
        service.modal.down_row_index = service.modal_down_row_index()
        service.modal.left_row_index = service.modal_left_row_index()
        service.modal.right_row_index = service.modal_right_row_index()

        if (column.meta == 'note') {
            return $http.get(service.modal.url).then(function(result) {
                service.modal.rows = null;
                service.modal.pre = result.data;
                service.modal.src = null;
            });
        } else if (column.meta == 'image') {
            service.modal.rows = null;
            service.modal.pre = null;
            service.modal.src = service.modal.url;

            return $q.when();
        } else if (column.meta == 'datalink') {
            return $http.get(service.modal.url + '&RESPONSEFORMAT=application/json').then(function(result) {
                service.modal.links = result.data.links;
                service.modal.pre = null;
                service.modal.src = null;
            });
        } else {
            return $q.when();
        }
    };

    service.modal_up_row_index = function() {
        if (service.active.row_index > 0) {
            return service.active.row_index - 1;
        } else if (service.first_page) {
            return false;
        } else {
            return -1;
        }
    };

    service.modal_down_row_index = function() {
        if (service.active.row_index < service.rows.length - 1) {
            return service.active.row_index + 1;
        } else if (service.last_page) {
            return false;
        } else {
            return -1;
        }
    };

    service.modal_left_row_index = function() {
        for (var index = service.active.column_index - 1; index >= 0; index--) {
            if (service.columns[index].meta == 'note' || service.columns[index].meta == 'image') {
                return index;
            }
        }
        return false;
    };

    service.modal_right_row_index = function() {
        for (var index = service.active.column_index + 1; index < service.columns.length; index++) {
            if (service.columns[index].meta == 'note' || service.columns[index].meta == 'image') {
                return index;
            }
        }
        return false;
    };

    service.modal_up = function() {
        if (service.modal.up_row_index == -1) {
            // first load previous page
            service.previous().then(function() {
                // set row_index to the last row and update modal
                service.active.row_index = service.rows.length - 1;
                service.modal_update();
            });
        } else if (service.modal.up_row_index !== false) {
            // decrement the row_index and update modal
            service.active.row_index = service.modal.up_row_index;
            service.modal_update();
        }
    };

    service.modal_down = function() {
        if (service.modal.down_row_index == -1) {
            // first load next page
            service.next().then(function() {
                // set row_index to 0 and update modal
                service.active.row_index = 0;
                service.modal_update();
            });
        } else if (service.modal.down_row_index !== false) {
            // increment the row_index and update modal
            service.active.row_index = service.modal.down_row_index;
            service.modal_update();
        }
    };

    service.modal_left = function() {
        service.active.column_index = service.modal.left_row_index;
        service.modal_update();
    };

    service.modal_right = function() {
        service.active.column_index = service.modal.right_row_index;
        service.modal_update();
    };

    return service;
}]);
