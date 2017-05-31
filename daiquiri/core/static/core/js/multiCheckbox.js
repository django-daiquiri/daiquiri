angular.module('core')

.directive('multiCheckbox', function() {

    return {
        restrict: 'A',
        require: 'ngModel',
        link: function(scope, element, attrs, ngModelController) {
            if (attrs.type === 'checkbox') {

                ngModelController.$parsers.push(function(view_value) {
                    var value = parseInt(attrs.value, 10);
                    var model_values = (ngModelController.$modelValue) ? model_values = ngModelController.$modelValue : [];
                    var index = model_values.indexOf(value);

                    if (view_value === true && index === -1) {
                        model_values.push(value);
                    } else if (view_value === false && index !== -1) {
                        model_values.splice(index, 1);
                    }

                    return model_values.sort();
                });

                ngModelController.$formatters.push(function(model_values) {
                    var value = parseInt(attrs.value, 10);
                    if (angular.isDefined(model_values) && model_values.indexOf(value) !== -1) {
                        return true;
                    } else {
                        return false;
                    }
                });
            }
        }
    };
});
