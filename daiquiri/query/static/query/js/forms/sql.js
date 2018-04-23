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
        QueryService.activate_form('sql');

        // check if a query was copied into the localStorage
        var stored_query_language = localStorage.getItem('stored_query_language'),
            stored_query = localStorage.getItem('stored_query');
        if (stored_query_language && stored_query) {
            localStorage.removeItem('stored_query_language');
            localStorage.removeItem('stored_query');

            service.copy_query(stored_query_language, stored_query)
        }

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

        QueryService.submit_job(service.values)
            .then(function() {
                // success
            }, function (response) {
                if (response.status == 400) {
                    // error
                    service.errors = response.data;

                    var editor = $('.CodeMirror')[0].CodeMirror;

                    if (angular.isDefined(service.errors.query) && angular.isDefined(service.errors.query.positions)) {

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
                } else {
                    service.errors = {
                        server_error: true
                    };
                }
            });
    };

    service.clear_query = function(string) {
        service.values.query = '';
        $('.CodeMirror')[0].CodeMirror.focus();
    };

    service.paste_item = function(resource, item) {
        // get the editor object
        var editor = $('.CodeMirror')[0].CodeMirror;

        if (resource == 'examples') {
            service.values.query = item.query_string;
            service.values.query_language = item.query_language;

            editor.refresh();
        } else {
            var query_language = $filter('filter')(QueryService.query_languages, {id: service.values.query_language})[0];
            var quote_char = query_language.quote_char;

            var query_strings = [];
            angular.forEach(item.query_strings, function(query_string) {
                query_strings.push(quote_char + query_string + quote_char);
            })

            var query_string = query_strings.join('.');

            editor.replaceSelection(query_string);
        }

        // focus the editor
        editor.focus();
    }

    service.paste_string = function(string) {
        var editor = $('.CodeMirror')[0].CodeMirror;
        editor.replaceSelection(string);
        editor.focus();
        $('.daiquiri-query-dropdowns .btn-group').removeClass('open');
    }

    service.copy_query = function(query_language, query) {
        service.values.query_language = query_language;
        service.values.query = query;
        service.activate();
    }

    service.toggle_dropdown = function(dropdown) {
        if (service.dropdown === dropdown) {
            service.dropdown = null;
        } else {
            service.dropdown = dropdown;
        }
    }

    return service;
}]);
