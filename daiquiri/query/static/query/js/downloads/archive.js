app.factory('ArchiveDownloadService', ['QueryService', function(QueryService) {

    var service = {
        columns: []
    };

    service.init = function() {
        service.columns = [];
        angular.forEach(QueryService.job.columns, function(column) {
            if (column.ucd && column.ucd.indexOf('meta.ref') > -1) {
                angular.forEach(['meta.note', 'meta.image', 'meta.file'], function(key) {
                    if (column.ucd.indexOf(key) > -1) {
                        service.columns.push(column.name);
                    }
                });
            }
        });
    }

    return service;
}]);
