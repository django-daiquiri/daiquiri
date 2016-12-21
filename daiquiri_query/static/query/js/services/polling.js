app.factory('PollingService', ['$timeout', function($timeout) {

    var service = {
        actions: {}
    };

    service.init = function() {
        service.poll();
    };

    service.poll = function() {
        angular.forEach(service.actions, function(action) {
            if (action.enabled) {
                action.callback();
            }
        });

        $timeout(service.poll, 5000);
    };

    service.register = function(key, callback, enabled) {
        if (angular.isUndefined(enabled)) {
            enabled = true;
        }

        service.actions[key] = {
            'callback': callback,
            'enabled': enabled
        };
    };

    service.unregister = function(key) {
        delete service.actions[key];
    };

    service.enable = function(key) {
        service.actions[key].enabled = true;
    };

    service.disable = function(key) {
        service.actions[key].enabled = false;
    };

    return service;
}]);
