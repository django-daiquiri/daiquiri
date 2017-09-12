app.factory('PlotService', ['$resource', '$q', function($resource, $q) {

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
        data: {}
    };

    service.init = function(job) {
        service.database_name = job.database_name;
        service.table_name = job.table_name;

        service.values.x = job.columns[0].name;
        service.values.y = job.columns[1].name;

        service.fetch().then(function() {
            service.draw();
        });
    };

    service.update = function() {
        if (service.source) {
            service.fetch().then(function() {
                service.draw();
            });
        };
    };

    service.fetch = function() {
        return $q.all([resources.rows.paginate({
            database: service.database_name,
            table: service.table_name,
            column: service.values.x,
            page_size: 0
        }).$promise, resources.rows.paginate({
            database: service.database_name,
            table: service.table_name,
            column: service.values.y,
            page_size: 0
        }).$promise]).then(function(results) {
            service.x = [].concat.apply([], results[0].results);
            service.y = [].concat.apply([], results[1].results);
        });
    };

    service.draw = function() {
        var canvas = $('#canvas');
        canvas.empty();

        service.source = new Bokeh.ColumnDataSource({ data: {x: service.x, y: service.y} });

        var xmin = Math.min.apply(null, service.x),
            xmax = Math.max.apply(null, service.x),
            ymin = Math.min.apply(null, service.y),
            ymax = Math.max.apply(null, service.y);

        var xpad = (xmax - xmin) * 0.1,
            ypad = (ymax - ymin) * 0.1;

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

        Bokeh.Plotting.show(figure, canvas);
    }

    return service;
}]);
