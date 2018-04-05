angular.module('core')

.filter('ucfirst', function() {
    return function(input, arg) {
        return input.charAt(0).toUpperCase() + input.slice(1);
    };
})

.filter('removeUnderscores', function() {
    return function(input, arg) {
        return input.replace(/_/g, ' ');
    };
})

.filter('filterAgainstList', function() {
    return function(input_values, opt) {
        var key = Object.keys(opt)[0];
        var list = opt[key];

        var output_values = [];
        angular.forEach(input_values, function(values) {
            if (list.indexOf(values[key]) > -1) {
                output_values.push(values);
            }
        });

        return output_values;
    };
})

.filter('encodeURIComponent', function() {
    return window.encodeURIComponent;
})

.filter('bytes', function() {
    return function(bytes) {
        if (angular.isUndefined(bytes) || isNaN(parseFloat(bytes)) || !isFinite(bytes)) return '';
        if (bytes === 0 || bytes === '0' ) return '0 bytes';

        var units = ['bytes', 'kB', 'MB', 'GB', 'TB', 'PB'];
        var number = Math.floor(Math.log(bytes) / Math.log(1000));

        return (bytes / Math.pow(1000, Math.floor(number))).toFixed(1) +  ' ' + units[number];
    };
})
;
