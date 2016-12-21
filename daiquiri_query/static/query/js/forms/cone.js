app.factory('ConeFormService', ['QueryService', function(QueryService) {

    var service = {
        values: {},
        errors: {}
    };

    service.activate = function() {
        QueryService.activateForm('cone');
    };

    service.submit = function() {

    };

    return service;
}]);
