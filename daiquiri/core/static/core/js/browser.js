angular.module('core')

.directive('daiquiriBrowser', ['BrowserService', function(BrowserService) {
    return {
        templateUrl: angular.element('meta[name="staticurl"]').attr('content') + 'core/html/browser.html',
        scope: {
            browserId: '@'
        },
        link: function (scope, element, attrs) {
            scope.browser = BrowserService;

            scope.itemClicked = function(browser_id, item, column_index, row_index) {
                BrowserService.selectItem(browser_id, column_index, row_index);
                BrowserService.activateItem(browser_id, column_index, row_index);

                var resource = BrowserService[browser_id].columns[column_index].name;
                scope.$emit('browserItemClicked', resource, item);
            };

            scope.itemDblClicked = function(browser_id, item, column_index, row_index) {
                var resource = BrowserService[browser_id].columns[column_index].name;
                scope.$emit('browserDblItemClicked', resource, item);
            };
        }
    };
}])

.factory('BrowserService', ['$timeout', '$filter', function($timeout, $filter) {
    var browser = {};

    browser.init = function(browser_id, columns, filter) {
        browser[browser_id] = {
            'columns': columns.map(function(column) { return { name: column, items: [] }; }),
            'filter': filter
        };
    };

    browser.render = function(browser_id, data, active_item) {
        // set the the data structure
        browser[browser_id].data = data;

        // define shortcuts
        var column0 = browser[browser_id].columns[0],
            column1 = browser[browser_id].columns[1],
            column2 = browser[browser_id].columns[2];

        // set up the first column
        column0.items = browser[browser_id].data;

        if (angular.isDefined(active_item) && active_item) {
            browser.findActiveItem(browser_id, active_item);
        } else {
            if (angular.isDefined(column1) && angular.isDefined(column1.selected) && column1.selected) {
                // something in the SECOND column has been selected before:
                // first select the selected item in the FIRST column
                // then the selected item in the SECOND column
                var column0_selected = column0.selected,
                    column1_selected = column1.selected;

                browser.selectItem(browser_id, 0, column0_selected);
                browser.selectItem(browser_id, 1, column1_selected);

            } else if (angular.isDefined(column0) && angular.isDefined(column0.selected) && column0.selected) {
                // something in the FIRST row has been selected before: select it again
                browser.selectItem(browser_id, 0, column0.selected);
            } else {
                // nothing has been selected yet, select the first item of the FIRST column
                browser.selectItem(browser_id, 0, 0);
            }

            if (angular.isDefined(active_item) && active_item === false)  {
                // do nothing it active_item is set to false
            } else if (angular.isDefined(browser.active) && browser.active.browser_id == browser_id) {
                browser.activateItem(browser_id, browser.active.column_index, browser.active.row_index);
            }
        }
    };

    browser.selectItem = function(browser_id, column_index, row_index) {

        // define shorcuts
        var data = browser[browser_id].data,
            column0 = browser[browser_id].columns[0],
            column1 = browser[browser_id].columns[1],
            column2 = browser[browser_id].columns[2];

        // select the clicked item, if it wasn't in the last column
        if (column_index < browser[browser_id].columns.length - 1) {
            browser[browser_id].columns[column_index].selected = row_index;
        }

        // if an item in the first column was selected, update SECOND column and select the first entry
        if (column_index < 1 && angular.isDefined(column1)) {
            if (angular.isDefined(data[row_index]) &&
                angular.isDefined(data[row_index][column1.name])) {

                column1.items = data[row_index][column1.name];
                column1.selected = 0;
            } else {
                column1.items = [];
                column1.selected = false;
            }
        }

        // if an item in the first or second column was selected, update THIRD column and select the first entry
        if (column_index < 2 && angular.isDefined(column1) && angular.isDefined(column2)) {
            var column0_row_index, column1_row_index;

            // for an item in the FIRST column:
            // use the clicked row and the first row of the SECOND column
            // for an item in the SECOND column:
            // use the already selected row in the FIRST column and the clicked row
            if (column_index < 1) {
                column0_row_index = row_index;
                column1_row_index = 0;
            } else {
                column0_row_index = column0.selected;
                column1_row_index = row_index;
            }

            if (angular.isDefined(data[column0_row_index]) &&
                angular.isDefined(data[column0_row_index][column1.name]) &&
                angular.isDefined(data[column0_row_index][column1.name][column1_row_index]) &&
                angular.isDefined(data[column0_row_index][column1.name][column1_row_index][column2.name])) {

                column2.items = browser[browser_id].data[column0_row_index][column1.name][column1_row_index][column2.name];
                column2.selected = browser[browser_id].data[column0_row_index][column1.name][column1_row_index][column2.name][0];
            } else {
                column2.items = [];
                column2.selected = false;
            }
        }
    };

    browser.getSelectedItem = function(browser_id, column_index) {
        if (angular.isDefined(browser[browser_id])) {
            var selected = browser[browser_id].columns[column_index].selected;
            return browser[browser_id].columns[column_index].items[selected];
        }
    };

    browser.activateItem = function(browser_id, column_index, row_index) {
        browser.active = {
            browser_id: browser_id,
            column_index: column_index,
            row_index: row_index
        };
    };

    browser.isActive = function(browser_id, column_index, row_index) {
        if (angular.isDefined(browser.active)) {
            return browser.active.browser_id == browser_id &&
                   browser.active.column_index == column_index &&
                   browser.active.row_index == row_index;
        } else {
            return false;
        }
    };

    browser.findActiveItem = function(browser_id, item) {
        // define shorcuts
        var column0 = browser[browser_id].columns[0],
            column1 = browser[browser_id].columns[1],
            column2 = browser[browser_id].columns[2];

        var index = browser[browser_id].data.map(function(item0, index0) {
            if (item.resource == column0.name) {
                if (item0.id == item.id) return [index0];
            } else {
                if (item0[column1.name].length > 0) {
                    return item0[column1.name].map(function(item1, index1) {
                        if (item.resource == column1.name) {
                            if (item1.id == item.id) return [index0, index1];
                        } else {
                            if (item1[column2.name].length > 0) {
                                return item1[column2.name].map(function(item2, index2) {
                                    if (item.resource == column2.name) {
                                        if (item2.id == item.id) return [index0, index1, index2];
                                    }
                                }).reduce(function(previous, current, index, array) {
                                    return (angular.isDefined(current)) ? current : previous;
                                });
                            }
                        }
                    }).reduce(function(previous, current, index, array) {
                        return (angular.isDefined(current)) ? current : previous;
                    });
                }
            }
        }).reduce(function(previous, current, index, array) {
            return (angular.isDefined(current)) ? current : previous;
        });

        if (index && angular.isDefined(index[0])) {
            browser.selectItem(browser_id, 0, index[0]);

            if (angular.isDefined(index[1])) {
                browser.selectItem(browser_id, 1, index[1]);

                if (angular.isDefined(index[2])) {
                    browser.activateItem(browser_id, 2, index[2]);
                } else {
                    browser.activateItem(browser_id, 1, index[1]);
                }

            } else {
                browser.activateItem(browser_id, 0, index[0]);
            }
        }
    };

    return browser;
}]);
