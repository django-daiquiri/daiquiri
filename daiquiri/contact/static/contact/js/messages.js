var app = angular.module('messages', ['list', 'infinite-scroll']);

app.factory('MessagesService', ['$resource', '$timeout', 'ListService', function($resource, $timeout, ListService) {

    /* get the base url */

    var baseurl = angular.element('meta[name="baseurl"]').attr('content');

    /* configure resources */

    var resources = {
        messages: $resource(baseurl + 'contact/api/messages/:id/')
    }

    /* init the list service */

    ListService.init(resources.messages);

    /* create the messages service */

    var service = {
        list: ListService
    };

    service.init = function() {
        service.list.params.spam = false;
    };

    service.modal = function(modal_id, index) {
        service.current_index = index;
        service.current_row = angular.copy(service.list.rows[index]);
        service.errors = {};

        $timeout(function() {
            $('#' + modal_id).modal('show');
        });
    };

    service.updateMessage = function(row, status) {
        row.status = status;

        resources.messages.update({id: row.id}, row, function(response) {
            row.status_label = response.status_label;
        });
    }

    service.toggleSpam = function() {
        service.list.params.spam = !service.list.params.spam;
        service.list.params.page = 1;
        service.list.fetch();
    };

    return service;
}]);

app.controller('MessagesController', ['$scope', 'MessagesService', function($scope, MessagesService) {

    $scope.service = MessagesService;
    $scope.service.init();

}]);
