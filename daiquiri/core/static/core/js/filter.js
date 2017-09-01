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
;
