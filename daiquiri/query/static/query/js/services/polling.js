app.factory('PollingService', ['$timeout', function($timeout) {

    var service = {
        actions: {}
    };

    service.init = function() {
        service.poll();
    };

    service.poll = function() {
        angular.forEach(service.actions, function(action, polling_id) {
            if (action.enabled) {
                action.callback(action.callback_options);
            }
        });

        // 4 seconds matches on rotation of the spinning Queued icon
        $timeout(service.poll, 4000);
    };

    service.register = function(polling_id, callback, callback_options, enabled) {
        if (angular.isUndefined(callback_options)) {
            callback_options = {};
        }
        if (angular.isUndefined(enabled)) {
            enabled = true;
        }

        service.actions[polling_id] = {
            'callback': callback,
            'callback_options': callback_options,
            'enabled': enabled
        };
    };

    service.unregister = function(polling_id) {
        delete service.actions[polling_id];
    };

    service.enable = function(polling_id) {
        service.actions[polling_id].enabled = true;
    };

    service.disable = function(polling_id) {
        service.actions[polling_id].enabled = false;
    };

    service.isRegistered = function(polling_id) {
        return angular.isDefined(service.actions[polling_id]);
    };

    return service;
}]);
