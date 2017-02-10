app.factory('SqlFormService', ['$timeout', 'QueryService', function($timeout, QueryService) {

    var service = {
        values: {},
        errors: {}
    };

    service.activate = function() {
        QueryService.activateForm('sql');

        $timeout(function() {
            angular.element('.CodeMirror').get(0).CodeMirror.refresh();
        });
    };

    service.submit = function() {
        service.errors = {};

        QueryService.submitJob(service.values)
            .then(function() {
                // success
            }, function (response) {
                // error
                service.errors = response.data;

                var editor = $('.CodeMirror')[0].CodeMirror;
                var positions = angular.fromJson(service.errors.query.positions);
                angular.forEach(positions, function(position) {
                    editor.markText(
                        {line: position[0] - 1, ch: position[1]},
                        {line: position[0] - 1, ch: position[1] + position[2].length},
                        {className: 'codemirror-error'},
                        {clearOnEnter: true}
                    );
                });
            });
    };

    service.pasteQuery = function(query) {
        service.values.query = query;
        service.activate();
    }

    return service;
}]);
