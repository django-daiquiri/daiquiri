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
;
