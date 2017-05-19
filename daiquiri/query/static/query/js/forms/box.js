app.factory('BoxFormService', ['QueryService', function(QueryService) {

    var service = {
        values: {},
        errors: {}
    };

    service.activate = function() {
        QueryService.activateForm('box');
    };

    service.submit = function() {

    };

    return service;
}]);
