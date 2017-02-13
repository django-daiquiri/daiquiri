app.factory('SqlFormService', ['$timeout', 'QueryService', 'BrowserService', function($timeout, QueryService, BrowserService) {

    /* get the base url */

    var baseurl = angular.element('meta[name="baseurl"]').attr('content');

    /* create the form service */

    var service = {
        values: {},
        errors: {}
    };

    /* create and configure the browser service */

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

    service.pasteItem = function(resource, item) {
        var editor = $('.CodeMirror')[0].CodeMirror;

        if (resource == 'databases') {
            editor.replaceSelection(item.name);
        } else if (resource == 'tables') {
            editor.replaceSelection(item.name);
        } else if (resource == 'columns') {
            editor.replaceSelection(item.name);
        } else if (resource == 'functions') {
            editor.replaceSelection(item.name + '()');
        }

        editor.focus();
        $('.daiquiri-query-btn-groups .btn-group').removeClass('open');
    }

    service.replaceQuery = function(query) {
        service.values.query = query;
        service.activate();
    }

    return service;
}]);
