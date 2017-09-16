app.factory('SqlFormService', ['$timeout', '$filter', 'QueryService', 'BrowserService', function($timeout, $filter, QueryService, BrowserService) {

    /* get the base url */

    var baseurl = angular.element('meta[name="baseurl"]').attr('content');

    /* create the form service */

    var service = {
        values: {
            'query_language': QueryService.query_languages[0].id
        },
        errors: {},
        markers: [],
        dropdown: null
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
        var string = '';
        if (angular.isDefined(item.query_strings)) {
            var query_language = $filter('filter')(QueryService.query_languages, {id: service.values.query_language})[0];
            var quote_char = query_language.quote_char
            var strings = [];

            angular.forEach(item.query_strings, function(query_string) {
                strings.push(quote_char + query_string + quote_char);
            })

            string = strings.join('.')
        } else if (angular.isDefined(item.query_string)) {
            string = item.query_string;
        } else {
            string = item.name;
        }

        var editor = $('.CodeMirror')[0].CodeMirror;
        editor.replaceSelection(string);
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

    service.toggleDropdown = function(dropdown) {
        if (service.dropdown === dropdown) {
            service.dropdown = null;
        } else {
            service.dropdown = dropdown;
        }
    }

    return service;
}]);
