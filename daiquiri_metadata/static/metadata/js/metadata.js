angular.module('metadata', ['core'])

.factory('MetadataService', ['$http', '$resource', '$filter', '$timeout', 'BrowserService', function($http, $resource, $filter, $timeout, BrowserService) {

    /* get the base url */

    var baseurl = angular.element('meta[name="baseurl"]').attr('content');

    /* create the metadata service */

    var service = {};

    /* configure the resources */

    var resources = {
        'databases': $resource(baseurl + 'metadata/api/databases/:id/'),
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

    /* create and configure the browser service */

    service.browser = BrowserService;

    service.browser.init({
        databases: {
            url: baseurl + 'metadata/api/databases/?nested=1',
            columns: ['databases','tables','columns']
        },
        functions: {
            url: baseurl + 'metadata/api/functions/?nested=1',
            columns: ['functions']
        }
    });

    /* define service functions */

    service.init = function() {
        service.tabletypes = resources.tabletypes.query();
        service.groups = resources.groups.query();

        service.initDatabasesBrowser();
        service.initFunctionsBrowser();
    };

    service.initDatabasesBrowser = function() {
        service.browser.initBrowser('databases', service.active).then(function() {
            service.databases = service.browser['databases'].data;

            service.tables = [];
            angular.forEach(service.browser['databases'].data, function(database) {
                service.tables = service.tables.concat(database.tables);
            });
        });
    };

    service.initFunctionsBrowser = function() {
        service.browser.initBrowser('functions', service.active).then(function() {
            service.functions = service.browser['functions'].data;
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
}]);
