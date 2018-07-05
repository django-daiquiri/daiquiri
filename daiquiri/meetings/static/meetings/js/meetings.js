angular.module('meetings', ['core', 'infinite-scroll'])

.factory('MeetingsService', ['$resource', '$q', 'ListService', function($resource, $q, ListService) {

    /* get the base url */

    var baseurl = angular.element('meta[name="baseurl"]').attr('content');

    /* configure the resources */

    var resources = {
        'meetings': $resource(baseurl + 'meetings/api/meetings/:id/'),
        'participants': $resource(baseurl + 'meetings/api/participants/:id/'),
        'contributions': $resource(baseurl + 'meetings/api/contributions/:id/'),
        'contribution_types': $resource(baseurl + 'meetings/api/contributiontypes/:id/'),
        'statuses': $resource(baseurl + 'meetings/api/statuses/:id/'),
        'payments': $resource(baseurl + 'meetings/api/payments/:id/')
    };

    /* create the metadata service */

    var service = {
        list: ListService,
        filters: {
            contribution_type: {},
            status: {},
            payment: {}
        }
    };

    /* define service functions */

    service.init = function(meeting_id) {
        service.meeting = resources.meetings.get({id: meeting_id});
        service.contribution_types = resources.contribution_types.query();
        service.statuses = resources.statuses.query();
        service.payments = resources.payments.query();

        $q.all([
            service.meeting.$promise,
            service.contribution_types.$promise,
            service.statuses.$promise,
            service.payments.$promise
        ]).then(function() {
            service.list.init(resources.participants);
            service.ready = true;
        })
    };

    service.modal = function(modal_id, index) {
        service.values = {};
        service.errors = {};

        if (modal_id === 'meetings-form-modal') {

            service.values = angular.copy(service.meeting);

        } else {

            service.current_index = index;
            service.current_row = service.list.rows[index];

            if (modal_id === 'participants-show-modal' || modal_id === 'participants-form-modal') {
                if (angular.isDefined(service.current_row)) {
                    service.values = angular.copy(service.current_row);
                } else {
                    service.values = {
                        meeting: service.meeting.id,
                        details: {}
                    }
                }
            } else if (modal_id === 'contributions-show-modal' || modal_id === 'contributions-form-modal') {
                if (service.current_row.contributions.length) {
                    service.values = angular.copy(service.current_row.contributions[0]);
                }
            }
        }

        $('#' + modal_id).modal('show');
    };

    service.reload = function() {
        service.update_filters();
        service.list.reload();
    };

    service.update_filters = function() {
        angular.forEach(['contribution_type', 'status', 'payment'], function(filter) {
            service.list.params[filter] = [];
            angular.forEach(service.filters[filter], function(value, key) {
                if (value) {
                    service.list.params[filter].push(key);
                }
            });
        });
    };

    service.store_meeting = function() {
        service.errors = {};

        resources.meetings.update({
            id: service.values.id
        }, service.values, function(response) {
            // copy the data back to the rows array and close the modal
            service.meeting = response;

            $('.modal').modal('hide');
        }, function(result) {
            service.errors = result.data;
        });
    };

    service.store_participant = function() {
        service.errors = {};

        if (angular.isDefined(service.values.id)) {
            resources.participants.update({
                id: service.values.id
            }, service.values, function(response) {
                // copy the data back to the rows array and close the modal
                service.list.rows[service.current_index] = response;

                $('.modal').modal('hide');
            }, function(result) {
                service.errors = result.data;
            });
        } else {
            resources.participants.save(service.values, function(response) {
                service.list.reload();
                $('.modal').modal('hide');
            }, function(result) {
                service.errors = result.data;
            });
        }
    };

    service.store_contribution = function() {
        service.errors = {};

        if (angular.isDefined(service.values.id) && service.values.id) {
            resources.contributions.update({id: service.values.id}, service.values, function(response) {
                service.current_row.contributions = [response]

                $('.modal').modal('hide');
            }, function(result) {
                service.errors = result.data;
            });
        } else if (angular.isDefined(service.values.contribution_type) && service.values.contribution_type) {
            service.values.participant = service.current_row.id;

            resources.contributions.save(service.values, function(response) {
                service.current_row.contributions = [response]

                $('.modal').modal('hide');
            }, function(result) {
                service.errors = result.data;
            });
        } else {
            $('.modal').modal('hide');
        }
    };

    service.accept_participant = function(index) {
        service.current_row = service.list.rows[index];
        service.current_row.status = 'ACCEPTED';

        resources.participants.update({id: service.current_row.id}, service.current_row);

        angular.forEach(service.current_row.contributions, function(contribution) {
            contribution.accepted = true
        });
    };

    service.reject_participant = function(index) {
        service.current_row = service.list.rows[index];
        service.current_row.status = 'REJECTED';

        resources.participants.update({id: service.current_row.id}, service.current_row);

        angular.forEach(service.current_row.contributions, function(contribution) {
            contribution.accepted = false
        });
    };

    return service;
}])

.controller('MeetingsController', ['$scope', 'MeetingsService', function($scope, MeetingsService) {

    $scope.service = MeetingsService;

}]);
