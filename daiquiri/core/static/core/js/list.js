// throttle/debounce the frequency of infinite-scroll events
angular.module('infinite-scroll').value('THROTTLE_MILLISECONDS', 100);

angular.module('list', ['core'])

.directive('orderList', ['ListService', function(ListService) {
    return {
        requite: 'th',
        restrict: 'A',
        transclude: true,
        scope: {
            column_name: '@orderList'
        },
        templateUrl: function(element, attrs) {
            var staticurl = angular.element('meta[name="staticurl"]').attr('content');
            return staticurl + 'core/html/order-list.html';
        },
        link: function(scope, element, attrs) {
            scope.list = ListService;
        }
    }
}])

.factory('ListService', ['$window', function($window) {

    var service = {
        ready: false,
        params: {
            page: 1,
            ordering: null,
            search: null
        },
        search_string: null,
        idle: true
    };

    service.init = function(resource) {
        service.resource = resource;
    };

    service.fetch = function() {
        if (service.idle && service.params.page) {
            service.idle = false;

            return service.resource.get(service.params, function(response) {
                service.count = response.count;
                if (service.params.page == 1) {
                    service.rows = response.results;
                } else {
                    service.rows = service.rows.concat(response.results);
                }

                service.params.page = null;
                if (response.next) {
                    var m = response.next.match(/page=(\d+)/);
                    if (m) {
                        service.params.page = parseInt(m[1]);
                    }
                }
                service.idle = true;
                service.ready = true;

                if (response.next) {
                    service.fetch();
                }
            }).$promise;
        }
    };

    service.search = function() {
        service.params.page = 1;
        service.params.search = service.search_string;
        service.fetch();
    };

    service.order = function(column_name) {
        if (service.params.ordering == column_name) {
            service.params.ordering = '-' + column_name;
        } else {
            service.params.ordering = column_name;
        }

        service.params.page = 1;
        service.fetch();
    };

    service.reset = function() {
        service.params.page = 1;
        service.params.ordering = null;
        service.params.search = null;
        service.fetch();
    };

    return service;
}]);
