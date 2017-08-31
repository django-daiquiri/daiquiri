app.factory('SqlFormService', ['$timeout', 'QueryService', 'BrowserService', function($timeout, QueryService, BrowserService) {

    /* get the base url */

    var baseurl = angular.element('meta[name="baseurl"]').attr('content');

    /* create the form service */

    var service = {
        values: {
            'query_language': QueryService.query_languages[0].id
        },
        errors: {},
        markers: []
    };

    /* create and configure the browser service */

    service.activate = function() {
        QueryService.activateForm('sql');

        $timeout(function() {
            angular.element('.CodeMirror').get(0).CodeMirror.refresh();
        });
    };

    service.submit = function() {
        // reset markers and errors
        angular.forEach(service.markers, function(marker) {
            marker.clear();
        });
        service.markers = [];
        service.errors = {};

        QueryService.submitJob(service.values)
            .then(function() {
                // success
            }, function (response) {
                // error
                service.errors = response.data;

                var editor = $('.CodeMirror')[0].CodeMirror;

                if (angular.isDefined(service.errors.query.positions)) {

                    var editor = $('.CodeMirror')[0].CodeMirror;

                    angular.forEach(angular.fromJson(service.errors.query.positions), function(position) {
                        service.markers.push(editor.markText(
                            {line: position[0] - 1, ch: position[1]},
                            {line: position[0] - 1, ch: position[1] + position[2].length},
                            {className: 'codemirror-error'},
                            {clearOnEnter: true}
                        ));
                    });

                    service.errors.query = service.errors.query.messages;
                }
            });
    };

    service.clearQuery = function(string) {
        service.values.query = '';
        $('.CodeMirror')[0].CodeMirror.focus();
    };

    service.pasteItem = function(resource, item) {
        var editor = $('.CodeMirror')[0].CodeMirror;
        editor.replaceSelection(item.query_string);
        editor.focus();
        $('.daiquiri-query-dropdowns .btn-group').removeClass('open');
    }

    service.pasteString = function(string) {
        var editor = $('.CodeMirror')[0].CodeMirror;
        editor.replaceSelection(string);
        editor.focus();
        $('.daiquiri-query-dropdowns .btn-group').removeClass('open');
    }

    service.copyQuery = function(query_language, query) {
        service.values.query_language = query_language;
        service.values.query = query;
        service.activate();
    }

    return service;
}]);
