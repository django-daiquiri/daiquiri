app.factory('PlotService', ['$resource', '$q', '$filter', function($resource, $q, $filter) {

    /* get the base url */

    var baseurl = angular.element('meta[name="baseurl"]').attr('content');

    /* configure resources */

    var resources = {
        rows: $resource(baseurl + 'serve/api/rows/')
    }

    var service = {
        params: {
            page_size: 10000,
        },
        columns: null,
        values: {},
        errors: {},
        labels: {},
        ready: false
    };

    service.init = function(rows_url, params, columns) {
        service.ready = false;

        angular.extend(service.params, params);
        service.columns = columns;

        if (angular.isDefined(service.columns[0])) {
            service.values.x = service.columns[0].name;
        } else {
            service.values.x = null;
        }

        if (angular.isDefined(service.columns[1])) {
            service.values.y = service.columns[1].name;
        } else {
            service.values.y = null;
        }

        service.update();
    };

    service.update = function() {
        service.clear();

        if (service.values.x) {
            var x_column = $filter('filter')(service.columns, {name: service.values.x}, true)[0];

            if (['int', 'long', 'float', 'double'].indexOf(x_column.datatype) > -1) {
                service.errors.x = null;

                service.labels.x = x_column.name;
                if (x_column.unit && x_column.unit.length > 0) {
                    service.labels.x += ' [' + x_column.unit + ']';
                }
            } else {
                service.errors.x = [interpolate(gettext('Columns of the type %s can not be plotted'), [x_column.datatype])];
            }
        } else {
            service.errors.x = [gettext('No column selected')];
        }

        if (service.values.y) {
            var y_column = $filter('filter')(service.columns, {name: service.values.y}, true)[0];

            if (['int', 'long', 'float', 'double'].indexOf(y_column.datatype) > -1) {
                service.errors.y = null;

                service.labels.y = y_column.name;
                if (y_column.unit && y_column.unit.length > 0) {
                    service.labels.y += ' [' + y_column.unit + ']';
                }
            } else {
                service.errors.y = [interpolate(gettext('Columns of the type %s can not be plotted'), [y_column.datatype])];
            }
        } else {
            service.errors.y = [gettext('No column selected')];
        }

        if (service.errors.x === null && service.errors.y === null) {
            service.fetch().then(function() {
                service.draw();
                service.ready = true;
            });
        } else {
            service.ready = true;
        }
    };

    service.clear = function() {
        $('#canvas').empty();
    }

    service.fetch = function() {

        var x_params = angular.extend({}, service.params, {
            column: service.values.x
        });
        var y_params = angular.extend({}, service.params, {
            column: service.values.y
        });

        return $q.all([
            resources.rows.paginate(x_params).$promise,
            resources.rows.paginate(y_params).$promise
        ]).then(function(results) {
            service.source = new Bokeh.ColumnDataSource({
                data: {
                    x: results[0].results,
                    y: results[1].results
                }
            });
        });
    };

    service.draw = function() {
        var xmin = Math.min.apply(null, service.source.data.x),
            xmax = Math.max.apply(null, service.source.data.x),
            ymin = Math.min.apply(null, service.source.data.y),
            ymax = Math.max.apply(null, service.source.data.y);

        if (!isNaN(xmin) && !isNaN(xmax) && !isNaN(ymin) && !isNaN(ymax)) {

            // compute a 1% padding around the data
            var xpad, ypad;
            if (xmax == xmin) {
                xpad = 0.001 * xmax;
            } else {
                xpad = 0.01 * (xmax - xmin);
            }
            if (ymax == ymin) {
                ypad = 0.001 * ymax;
            } else {
                ypad = 0.01 * (ymax - ymin);
            }

            // create some ranges for the plot
            var x_range = new Bokeh.Range1d({
                start: xmin - xpad,
                end: xmax + xpad
            });
            var y_range = new Bokeh.Range1d({
                start: ymin - ypad,
                end: ymax + ypad
            });

            // make the plot
            var tools = "pan,crosshair,wheel_zoom,box_zoom,reset,save";
            var figure = new Bokeh.Plotting.figure({
                height: 840,
                height: 500,
                x_range: x_range,
                y_range: y_range,
                plot_width: $('.col-md-9').width(),
                tools: tools,
                output_backend: 'webgl',
                background_fill_color: '#f5f5f5'
            });

            figure.xaxis.axis_label = service.labels.x;
            figure.xaxis.axis_label_text_font = 'DroidSans'

            figure.yaxis.axis_label = service.labels.y;
            figure.yaxis.axis_label_text_font = 'DroidSans'

            figure.toolbar.active_scroll = figure.toolbar.wheel_zoom;
            figure.outline_line_color = '#dddddd';
            figure.toolbar.logo = null;

            var circles = figure.circle({
                x: { field: "x" },
                y: { field: "y" },
                source: service.source,
                fill_alpha: 0.5
            });

            Bokeh.Plotting.show(figure, $('#canvas'));
            $('.bk-button-bar-list[type="scroll"] .bk-toolbar-button').click();
            $('.bk-button-bar-list[type="inspectors"] .bk-toolbar-button').click();
        }
    }

    return service;
}]);
