app.factory('PlotService', ['$resource', '$q', '$filter', function($resource, $q, $filter) {

    /* get the base url */

    var baseurl = angular.element('meta[name="baseurl"]').attr('content');

    /* configure resources */

    var resources = {
        rows: $resource(baseurl + 'serve/api/rows/')
    }

    var service = {
        job: null,
        source: null,
        values: {},
        errors: {},
        data: {},
        page_size: 10000,
        idle: true
    };

    service.init = function(job) {
        service.job = job;

        service.values.x = job.columns[0].name;
        service.values.y = job.columns[1].name;

        service.update();
    };

    service.update = function() {
        if (service.idle) {
            service.idle = false;

            var canvas = $('#canvas');
            canvas.empty();

            x_column = $filter('filter')(service.job.columns, {name: service.values.x}, true)[0];
            y_column = $filter('filter')(service.job.columns, {name: service.values.y}, true)[0];

            if (['int', 'long', 'float', 'double'].indexOf(x_column.datatype) > -1) {
                service.errors.x = null;
            } else {
                service.errors.x = [interpolate(gettext('Columns of the type %s can not be plotted'), [x_column.datatype])];
            }
            if (['int', 'long', 'float', 'double'].indexOf(y_column.datatype) > -1) {
                service.errors.y = null;
            } else {
                service.errors.y = [interpolate(gettext('Columns of the type %s can not be plotted'), [y_column.datatype])];
            }

            if (service.errors.x === null && service.errors.y === null) {
                service.fetch().then(function() {
                    service.draw();
                    service.idle = true;
                });
            } else {
                service.source = null;
                service.idle = true;
            }
        }
    };

    service.fetch = function() {
        return $q.all([resources.rows.paginate({
            database: service.job.database_name,
            table: service.job.table_name,
            column: service.values.x,
            page_size: service.page_size
        }).$promise, resources.rows.paginate({
            database: service.job.database_name,
            table: service.job.table_name,
            column: service.values.y,
            page_size: service.page_size
        }).$promise]).then(function(results) {
            service.x = [].concat.apply([], results[0].results);
            service.y = [].concat.apply([], results[1].results);
        });
    };

    service.draw = function() {
        service.source = new Bokeh.ColumnDataSource({ data: {x: service.x, y: service.y} });

        var xmin = Math.min.apply(null, service.x),
            xmax = Math.max.apply(null, service.x),
            ymin = Math.min.apply(null, service.y),
            ymax = Math.max.apply(null, service.y);

        if (!isNaN(xmin) && !isNaN(xmax) && !isNaN(ymin) && !isNaN(ymax)) {

            // compute a 10% padding around the data
            var xpad, ypad;
            if (xmax == xmin) {
                xpad = 0.001 * xmax;
            } else {
                xpad = 0.1 * (xmax - xmin);
            }
            if (ymax == ymin) {
                ypad = 0.001 * ymax;
            } else {
                ypad = 0.1 * (ymax - ymin);
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
                x_range: x_range,
                y_range: y_range,
                plot_width: $('.col-md-9').width(),
                tools: tools,
                output_backend: 'webgl'
            });

            var circles = figure.circle({
                x: { field: "x" },
                y: { field: "y" },
                source: service.source,
            });

            Bokeh.Plotting.show(figure, $('#canvas'));
        }
    }

    return service;
}]);
