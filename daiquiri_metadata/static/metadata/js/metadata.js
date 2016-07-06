angular.module('metadata', ['resources', 'browser'])

.config(['$httpProvider', '$interpolateProvider', function($httpProvider, $interpolateProvider) {
    $interpolateProvider.startSymbol('{$');
    $interpolateProvider.endSymbol('$}');
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
}])

.factory('MetadataService', ['$http', 'ResourcesService', 'BrowserService', function($http, ResourcesService, BrowserService) {

    /* get the base url */

    var baseurl = angular.element('meta[name="baseurl"]').attr('content');

    /* create the metadata service */

    var service = {};

    /* create and configure the resources service */

    var resources_service = ResourcesService;

    resources_service.init({
        service: service,
        urls: {
            'databases': baseurl + 'metadata/api/databases/',
            'tables': baseurl + 'metadata/api/tables/',
            'columns': baseurl + 'metadata/api/columns/',
            'functions': baseurl + 'metadata/api/functions/',
        },
        factory: function(resource) {
            if (resource === 'databases') {

            } else if (resource === 'tables') {

            } else if (resource === 'columns') {

            } else if (resource === 'functions') {

            }
        }
    });

    /* create and configure the browser service */

    var browser = BrowserService;

    browser.init({
        databases: {
            url: baseurl + 'metadata/api/databases/?nested=1',
            columns: ['databases','tables','columns']
        },
        functions: {
            url: baseurl + 'metadata/api/functions/?nested=1',
            columns: ['functions']
        }
    });

    service.init = function() {
        browser.initBrowser('databases');
        browser.initBrowser('functions');
    };

    // init databases browser
    // BrowserService.browser.databases = {
    //     'url': '/data/databases/',
    //     'colnames': ['databases','tables','columns']
    // };
    // BrowserService.initBrowser('databases');

    // BrowserService.browser.functions = {
    //     'url': '/data/functions/',
    //     'colnames': ['functions']
    // };
    // BrowserService.initBrowser('functions');

    // function fetchView(url) {
    //     $http.get(base + url).success(function(data) {
    //         view.showUrl   = url.substring(1);
    //         view.updateUrl = url.substring(1).replace('/show/','/update/');
    //         view.deleteUrl = url.substring(1).replace('/show/','/delete/');

    //         var model = url.match(/^\/data\/(.*?)\/show\//)[1];
    //         view.model = model.substring(0,1).toUpperCase() + model.substring(1,model.length-1);

    //         view.name = '';
    //         if (angular.isDefined(data.row.database)) {
    //             view.name += data.row.database + '.';
    //         }
    //         if (angular.isDefined(data.row.table)) {
    //             view.name += data.row.table + '.';
    //         }
    //         view.name += data.row.name;

    //         view.description = data.row.description;

    //         if (angular.isDefined(data.row.type)) {
    //             view.type = data.row.type;
    //         }
    //         if (angular.isDefined(data.row.unit)) {
    //             view.unit = data.row.unit;
    //         }
    //         if (angular.isDefined(data.row.ucd)) {
    //             view.ucd = data.row.ucd;
    //         }

    //         if (data.row.order !== null) {
    //             view.order = data.row.order;
    //         }

    //         view.description = data.row.description;

    //         if (data.row.publication_role !== 'false') {
    //             view.publication_role = data.row.publication_role;
    //         }

    //         var permissions = [];
    //         if (data.row.publication_select === '1') {
    //             permissions.push('select');
    //         }
    //         if (data.row.publication_update === '1') {
    //             permissions.push('update');
    //         }
    //         if (data.row.publication_insert === '1') {
    //             permissions.push('insert');
    //         }
    //         view.permissions = permissions.join();

    //         if (data.row.publication_role !== 'false') {
    //             view.publication_role = data.row.publication_role;
    //         }

    //         // store database or table ids for later
    //         if (model == 'databases') {
    //             active.database_id = data.row.id;
    //         } else {
    //             active.database_id = data.row.database_id;
    //         }
    //         if (model == 'tables') {
    //             active.table_id = data.row.id;
    //         } else {
    //             active.table_id = data.row.table_id;
    //         }
    //     });
    // }

    // function fetchHtml(url) {
    //     $http.get(url,{'headers': {'Accept': 'application/html'}}).success(function(html) {
    //         for (var value in values) delete values[value];
    //         for (var error in errors) delete errors[error];

    //         ModalService.modal.html = html;

    //         if (url.indexOf('/data/tables/create') != -1 && angular.isDefined(active.database_id)) {
    //             values.database_id = active.database_id;
    //         }
    //         if (url.indexOf('/data/columns/create') != -1 && angular.isDefined(active.table_id)) {
    //             values.table_id = active.table_id;
    //         }

    //         active.url = url;
    //         ModalService.open();
    //     });
    // }

    // function submitForm(submit) {
    //     if (submit) {
    //         var data = {
    //             'csrf': angular.element('#csrf').attr('value')
    //         };

    //         // merge with form values
    //         angular.extend(data,values);

    //         $http.post(active.url,$.param(data)).success(function(response) {
    //             for (var error in errors) delete errors[error];

    //             if (response.status === 'ok') {
    //                 ModalService.close();

    //                 var m = active.url.match(/\/data\/(\w+)\/(\w+)/);
    //                 var model = m[1];
    //                 var action = m[2];

    //                 if (model === 'functions') {
    //                     BrowserService.initBrowser('functions');
    //                 } else {
    //                     BrowserService.initBrowser('databases');
    //                 }

    //                 if (action === 'update') {
    //                     var id = active.url.match(/\/(\d+)$/)[1];
    //                     var url = base + '/data/' + model + '/show/id/' + id;
    //                     fetchView(url);
    //                 } else {
    //                     for (var value in view) delete view[value];
    //                 }
    //             } else if (response.status === 'error') {
    //                 angular.forEach(response.errors, function(error, key) {
    //                     errors[key] = error;
    //                 });
    //             } else {
    //                 errors['form'] = {'form': ['Error: Unknown response from server.']};
    //             }
    //         });
    //     } else {
    //         ModalService.close();
    //     }
    // }

    return service;
}])

.controller('MetadataController', ['$scope', 'MetadataService', function($scope, MetadataService) {

    $scope.service = MetadataService;
    $scope.service.init();

    // $scope.view = DataService.view;
    // $scope.databases = DataService.databases;
    // $scope.functions = DataService.functions;
    // $scope.values = DataService.values;
    // $scope.errors = DataService.errors;

    // $scope.fetchHtml = function(event) {
    //     DataService.fetchHtml(event.target.href);
    //     event.preventDefault();
    // };

    // $scope.submitForm = function() {
    //     DataService.submitForm($scope.submit);
    // };

    // $scope.$on('browserItemClicked', function(event,browsername,url) {
    //     DataService.fetchView(url);
    // });

}])
;
