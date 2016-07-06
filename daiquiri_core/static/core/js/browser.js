angular.module('browser',[])

.directive('daiquiriBrowser', ['BrowserService', function(BrowserService) {
    return {
        templateUrl: angular.element('meta[name="staticurl"]').attr('content') + 'core/html/browser.html',
        scope: {
            resource: '@'
        },
        link: function (scope, element, attrs) {
            scope.browser = BrowserService;

            scope.itemClicked = function(resource, item, column_index, row_index) {
                BrowserService.selectItem(resource, column_index, row_index);
                BrowserService.activateItem(resource, item);

                $scope.$emit('browserItemClicked', resource, item);
            };

            scope.itemDblClicked = function(resource, item, column_index, row_index) {
                $scope.$emit('browserDblItemClicked', resource, item);
            };
        }
    };
}])

.factory('BrowserService', ['$http','$timeout',function($http,$timeout) {
    var browser = {};

    browser.init = function (resources) {
        angular.forEach(resources, function (options, resource) {
            browser[resource] = {
                url: options.url,
                columns: []
            };

            angular.forEach(options.columns, function(column) {
                browser[resource].columns.push({
                    name: column,
                    items: []
                });
            });
        });
    };

    browser.initBrowser = function(resource) {
        return $http.get(browser[resource].url)
            .success(function(response) {
                browser[resource].data = response;

                // setup the first column
                browser[resource].columns[0].items = browser[resource].data;

                // activate the first item of the first column
                browser.selectItem(resource, 0, 0);
            });
    };

    browser.selectItem = function(resource, column_index, row_index) {

        var column1 = browser[resource].columns[0];
        var column2 = browser[resource].columns[1];
        var column3 = browser[resource].columns[2];

        // select the clicked item, if it wasn't in the last column
        if (column_index < browser[resource].columns.length - 1) {
            browser[resource].columns[column_index].selected = row_index;
        }

        // if an item in the first column was selected, update SECOND column and select the first entry
        if (column_index < 1 && angular.isDefined(column2)) {
            column2.items = browser[resource].data[row_index][column2.name];
            column2.selected = 0;
        }

        // if an item in the first or second column was selected, update THIRD column and select the first entry
        if (column_index < 2 && angular.isDefined(column2) && angular.isDefined(column3)) {
            var column1_row_index, column2_row_index;

            // for an item in the first column, use the clicked row and the first row of the second column
            // for an item in the second column, use the already selected row in the first column and the clicked row
            if (column_index < 1) {
                column1_row_index = row_index;
                column2_row_index = 0;
            } else {
                column1_row_index = column1.selected;
                column2_row_index = row_index;
            }

            column3.items = browser[resource].data[column1_row_index][column2.name][column2_row_index][column3.name];
            column3.selected = browser[resource].data[column1_row_index][column2.name][column2_row_index][column3.name][0];
        }
    };

    browser.activateItem = function(resource, item) {
        browser.active = item;
    };

    return browser;
}]);
