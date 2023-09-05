'use strict';

// the module should depend on 'core' to use the stock services & components
angular.module('ajenti.dns_api', ['core']);


'use strict';

angular.module('ajenti.dns_api').config(function ($routeProvider) {
    $routeProvider.when('/view/dns_api', {
        templateUrl: '/dns_api:resources/partial/index.html',
        controller: 'DnsAPIIndexController'
    });
});


'use strict';

angular.module('ajenti.dns_api').controller('DnsAPIIndexController', function ($scope, $http, pageTitle, gettext, notify, messagebox) {
    pageTitle.set(gettext('DNS API'));
    $scope.detailsVisible = false;

    $scope.supported_types = ['A', 'AAAA', 'ALIAS', 'CNAME', 'MX', 'NS', 'PTR', 'SPF', 'TXT'];

    $http.get('/api/dns_api/domains').then(function (resp) {
        $scope.domains = resp.data[0];
        $scope.provider = resp.data[1];
        if ($scope.domains.length > 0) {
            $scope.domains.active = $scope.domains[0];
            $scope.get_records();
        } else {
            $scope.domains.active = '';
        }
    });

    $scope.get_records = function () {
        $http.get('/api/dns_api/domain/' + $scope.domains.active + '/records').then(function (resp) {
            $scope.records = resp.data;
        });
    };

    $scope.openDialog = function (record) {
        if (record) {
            $scope.DNSdialog = {
                'type': record.type,
                'ttl': record.ttl,
                'name': record.name,
                'value': record.values.join(' '),
                'mode': 'update'
            };
        } else {
            $scope.DNSdialog = {
                'type': 'A',
                'ttl': 10800,
                'name': '',
                'value': '',
                'mode': 'add'
            };
        }
        $scope.detailsVisible = true;
    };

    $scope.add = function () {
        $http.post('/api/dns_api/domain/' + $scope.domains.active + '/records/' + $scope.DNSdialog.name, {
            'ttl': $scope.DNSdialog.ttl,
            'type': $scope.DNSdialog.type,
            'values': $scope.DNSdialog.value }).then(function (resp) {
            code = resp.data[0];
            msg = resp.data[1];
            if (code >= 200 && code < 300) {
                notify.success(msg);
                $scope.get_records();
            } else {
                notify.error(msg);
            }
        });
        $scope.detailsVisible = false;
    };

    $scope.update = function () {
        $http.put('/api/dns_api/domain/' + $scope.domains.active + '/records/' + $scope.DNSdialog.name, {
            'ttl': $scope.DNSdialog.ttl,
            'type': $scope.DNSdialog.type,
            'values': $scope.DNSdialog.value }).then(function (resp) {
            code = resp.data[0];
            msg = resp.data[1];
            if (code >= 200 && code < 300) {
                notify.success(msg);
                $scope.get_records();
            } else {
                console.log(msg);
                notify.error(msg);
            }
        });
        $scope.detailsVisible = false;
    };

    $scope.delete = function (record) {
        messagebox.show({
            text: gettext('Really delete the entry "' + record.name + ' ' + record.type + ' ' + record.values + '"?'),
            positive: gettext('Delete'),
            negative: gettext('Cancel')
        }).then(function () {
            $http.delete('/api/dns_api/domain/' + $scope.domains.active + '/records/' + record.type + '/' + record.name).then(function (resp) {
                code = resp.data[0];
                msg = resp.data[1];
                if (code >= 200 && code < 300) {
                    notify.success(msg);
                    $scope.get_records();
                } else {
                    notify.error(msg);
                }
            });
        });
    };

    $scope.closeDialog = function () {
        return $scope.detailsVisible = false;
    };
});


