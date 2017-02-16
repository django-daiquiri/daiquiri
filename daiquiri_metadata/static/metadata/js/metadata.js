angular.module('metadata', ['core'])

.factory('MetadataService', ['$http', '$resource', '$filter', '$timeout', 'BrowserService', function($http, $resource, $filter, $timeout, BrowserService) {

    /* get the base url */

    var baseurl = angular.element('meta[name="baseurl"]').attr('content');

    /* create the metadata service */

    var service = {
        browser: BrowserService
    };

    /* configure the resources */

    var resources = {
        'databases': $resource(baseurl + 'metadata/api/databases/:list_route/:id/'),
        'tables': $resource(baseurl + 'metadata/api/tables/:route/:id/'),
        'columns': $resource(baseurl + 'metadata/api/columns/:route/:id/'),
        'functions': $resource(baseurl + 'metadata/api/functions/:id/'),
        'groups': $resource(baseurl + 'metadata/api/groups/:id/'),
        'tabletypes': $resource(baseurl + 'metadata/api/tabletypes/:id/'),
    };

    /* configure the factory for new items */

    service.factory = {
        databases: function() {
            return {
                groups: []
            };
         },
        tables: function() {
            return {
                database: service.browser.getSelectedItem('databases', 0).id,
                groups: []
            };
        },
        columns: function() {
            return {
                table: service.browser.getSelectedItem('databases', 1).id,
                groups: []
            };
        },
        functions: function() {
            return {
                groups: []
            };
        }
    };

    /* define service functions */

    service.init = function() {
        service.tabletypes = resources.tabletypes.query();
        service.groups = resources.groups.query();

        BrowserService.init('databases', ['databases','tables','columns']);
        BrowserService.init('functions', ['functions']);

        service.initDatabasesBrowser();
        service.initFunctionsBrowser();
    };

    service.initDatabasesBrowser = function() {
        resources.databases.query({'list_route': 'nested'}, function(response) {
            service.databases = response;

            service.tables = [];
            angular.forEach(service.databases, function(database) {
                database.label = database.name;
                angular.forEach(database.tables, function(table) {
                    table.label = database.name + '.' + table.name;
                    service.tables.push(table);
                });
            });

            BrowserService.render('databases', service.databases, service.active);
        });
    };

    service.initFunctionsBrowser = function() {
        resources.functions.query(function(response) {
            service.functions = response;

            BrowserService.render('functions', service.functions, service.active);
        });
    };

    service.activateItem = function(resource, id) {
        return resources[resource].get({id: id}, function(item) {
            item.resource = resource;

            item.published_for = $filter('filter')(service.groups, function(group) {
                return item.groups.indexOf(group.id) !== -1;
            });

            service.active = item;
        });
    };

    service.openFormModal = function(resource, create) {
        service.errors = {};
        service.values = {};

        if (angular.isDefined(create) && create) {
            service.values = service.factory[resource]();
        } else {
            service.values = angular.copy(service.active);
        }

        $timeout(function() {
            $('#' + resource + '-form-modal').modal('show');
        });
    };

    service.submitFormModal = function(resource) {

        var promise;
        if (angular.isDefined(service.values.id)) {
            promise = resources[resource].update({id: service.values.id}, service.values).$promise;
        } else {
            promise = resources[resource].save(service.values).$promise;
        }

        promise.then(function(result) {
            $('#' + resource + '-form-modal').modal('hide');

            service.activateItem(resource, result.id).$promise.then(function () {
                if (resource === 'functions') {
                    service.initFunctionsBrowser();
                } else {
                    service.initDatabasesBrowser();
                }
            });

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
                service.initDatabasesBrowser();
            }
        });
    };

    service.discoverItem = function(resource) {
        var parameters = {
            route: 'discover'
        };

        if (resource === 'tables') {
            parameters['database'] = $filter('filter')(service.databases, {'id': service.values.database})[0].name;
            parameters['table'] = service.values.name;
        } else if (resource === 'columns') {
            var split = $filter('filter')(service.tables, {'id': service.values.table})[0].__str__.split('.');

            parameters['database'] = split[0];
            parameters['table'] = split[1];
            parameters['column'] = service.values.name;
        }

        return resources[resource].query(parameters, function(response) {
            angular.extend(service.values, response[0]);
        });
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
