(function () {
    'use strict';

    angular.module('MenuApp', [])

    .controller('MenuController', ['$scope', '$log',
        function($scope, $log) {
            $scope.getResults = function() {
                $log.log("test");
            };
        }
    ]);
}());
