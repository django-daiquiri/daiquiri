angular.module('core')

.directive('formgroup', ['$sce', function($sce) {

    return {
        replace: true,
        scope: {
            id: '@',
            label: '@',
            help: '@',
            model: '=',
            errors: '=',
            mode: '@',
            options: '=',
            optionsId: '@',
            optionsLabel: '@',
            optionsFilter: '=',
            optionsNull: '@',
            optionsEmpty: '@'
        },
        templateUrl: function(element, attrs) {
            var staticurl = angular.element('meta[name="staticurl"]').attr('content');
            return staticurl + 'core/html/formgroup_' + attrs.type + '.html';
        },
        link: function(scope, element, attrs) {
            if (!attrs.optionsId) {
                attrs.optionsId = 'id';
            }

            scope.label = $sce.trustAsHtml(scope.label);
        }
    };
}]);
