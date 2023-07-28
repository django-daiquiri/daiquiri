angular.module('metadata', ['core'])

.factory('MetadataService', ['$resource', '$q', '$filter', '$timeout', 'BrowserService', function($resource, $q, $filter, $timeout, BrowserService) {

    /* get the base url */

    var baseurl = angular.element('meta[name="baseurl"]').attr('content');

    /* create the metadata service */

    var service = {
        ready: false,
        browser: BrowserService
    };

    /* configure the resources */

    var resources = {
        'schemas': $resource(baseurl + 'metadata/api/schemas/:list_action/:id/'),
        'tables': $resource(baseurl + 'metadata/api/tables/:list_action/:id/'),
        'columns': $resource(baseurl + 'metadata/api/columns/:list_action/:id/'),
        'functions': $resource(baseurl + 'metadata/api/functions/:list_action/:id/'),
        'tabletypes': $resource(baseurl + 'metadata/api/tabletypes/:id/'),
        'licenses': $resource(baseurl + 'metadata/api/licenses/:id/'),
        'accesslevels': $resource(baseurl + 'metadata/api/accesslevels/:id/'),
        'groups': $resource(baseurl + 'auth/api/groups/:id/'),
    };

    /* configure the factory for new items */

    service.factory = {
        schemas: function() {
            return {
                access_level: 'PRIVATE',
                metadata_access_level: 'PRIVATE',
                discover: true,
                groups: []
            };
         },
        tables: function() {
            return {
                schema: service.browser.getSelectedItem('schemas', 0).id,
                access_level: 'PRIVATE',
                metadata_access_level: 'PRIVATE',
                discover: true,
                groups: []
            };
        },
        columns: function() {
            return {
                table: service.browser.getSelectedItem('schemas', 1).id,
                access_level: 'PRIVATE',
                metadata_access_level: 'PRIVATE',
                groups: []
            };
        },
        functions: function() {
            return {
                access_level: 'PRIVATE',
                metadata_access_level: 'PRIVATE',
                groups: []
            };
        },
        persons: function() {
            return {
                name: '',
                first_name: '',
                last_name: '',
                orcid: ''
            }
        }
    };

    /* define service functions */

    service.init = function() {
        service.tabletypes = resources.tabletypes.query();
        service.groups = resources.groups.query();
        service.licenses = resources.licenses.query();
        service.accesslevels = resources.accesslevels.query();

        BrowserService.init('schemas', ['schemas','tables','columns']);
        BrowserService.init('functions', ['functions']);

        schemas_promise = service.initSchemasBrowser();
        functions_promise = service.initFunctionsBrowser();

        $q.all([schemas_promise, functions_promise]).then(function() {
            service.ready = true;
        })
    };

    service.initSchemasBrowser = function() {
        return resources.schemas.query({'list_action': 'management'}, function(response) {
            service.schemas = response;

            service.tables = [];
            angular.forEach(service.schemas, function(schema) {
                schema.label = schema.name;
                angular.forEach(schema.tables, function(table) {
                    table.label = schema.name + '.' + table.name;
                    service.tables.push(table);
                });
            });

            BrowserService.render('schemas', service.schemas, service.active);
        }).$promise;
    };

    service.initFunctionsBrowser = function() {
        return resources.functions.query({'list_action': 'management'}, function(response) {
            service.functions = response;

            BrowserService.render('functions', service.functions, service.active);
        }).$promise;
    };

    service.activateItem = function(resource, id) {
        return resources[resource].get({id: id}, function(item) {
            item.resource = resource;

            // create a string for the groups
            if (angular.isDefined(item.groups)) {
                item.published_for = $filter('filter')(service.groups, function(group) {
                    return item.groups.indexOf(group.id) !== -1;
                }).map(function(group) {
                    return group.name;
                }).join(', ');
            }

            service.active = item;
        });
    };

    service.openFormModal = function(resource, create, modal) {
        service.errors = {};
        service.values = {};

        if (angular.isDefined(create) && create) {
            service.values = service.factory[resource]();
        } else {
            service.values = angular.copy(service.active);
        }

        $timeout(function() {
            var modal_id;
            if (angular.isDefined(modal) && modal) {
                modal_id = '#' + resource + '-' + modal + '-form-modal';
            } else {
                modal_id = '#' + resource + '-form-modal';
            }

            $(modal_id).modal('show');

            $timeout(function() {
                if (angular.element(modal_id + ' .CodeMirror').length) {
                    angular.element(modal_id + ' .CodeMirror')[0].CodeMirror.refresh();
                }
            });
        });
    };

    service.submitFormModal = function(resource, close) {

        var promise;
        if (angular.isDefined(service.values.id)) {
            promise = resources[resource].update({id: service.values.id}, service.values).$promise;
        } else {
            promise = resources[resource].save(service.values).$promise;
        }

        promise.then(function(result) {
            if (angular.isUndefined(close) || close) {
                $('.modal').modal('hide');

                service.activateItem(resource, result.id).$promise.then(function () {
                    if (resource === 'functions') {
                        service.initFunctionsBrowser();
                    } else {
                        service.initSchemasBrowser();
                    }
                });
            }
        }, function(result) {
            service.errors = result.data;
        });
    };

    service.openDeleteModal = function(resource) {
        service.values = service.active;
        $('#' + resource + '-delete-modal').modal('show');
    };

    service.submitDeleteModal = function(resource) {
        return resources[resource].remove({id: service.values.id}, function() {
            $('#' + resource + '-delete-modal').modal('hide');

            service.active = false;

            if (resource === 'functions') {
                service.initFunctionsBrowser();
            } else {
                service.initSchemasBrowser();
            }
        });
    };

    service.discoverItem = function(resource) {
        var parameters = {
            list_action: 'discover'
        };

        if (resource === 'tables') {
            parameters['schema'] = $filter('filter')(service.schemas, {'id': service.values.schema})[0].name;
            parameters['table'] = service.values.name;
        } else if (resource === 'columns') {
            var split = $filter('filter')(service.tables, {'id': service.values.table})[0].label.split('.');

            parameters['schema'] = split[0];
            parameters['table'] = split[1];
            parameters['column'] = service.values.name;
        }

        return resources[resource].query(parameters, function(response) {
            angular.extend(service.values, response[0]);
        });
    };

    service.addPerson = function(person_type) {
        if (service.values[person_type] === null) {
            service.values[person_type] = []
        }
        service.values[person_type].push(service.factory.persons());
    };

    service.removePerson = function(person_type, index) {
        service.values[person_type].splice(index, 1);
    };

    return service;
}])

.controller('MetadataController', ['$scope', 'MetadataService', function($scope, MetadataService) {

    $scope.service = MetadataService;
    $scope.service.init();

    $scope.$on('browserItemClicked', function(event, resource, item) {
        MetadataService.activateItem(resource, item.id);
    });

    $scope.$on('browserDblItemClicked', function(event, resource, item) {
        MetadataService.openFormModal(resource);
    });
}]);
