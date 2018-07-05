import json

import pytest
from ansible.module_utils import basic
from ansible.module_utils.six import StringIO
from ansible.module_utils.six.moves.urllib.error import HTTPError
from units.modules.utils import set_module_args, AnsibleFailJson, exit_json, fail_json, AnsibleExitJson

from library.generated import ftd_deployment


class TestFtdDeployment(object):
    module = ftd_deployment

    @pytest.fixture
    def module_args(self):
        return {
            'hostname': 'http://testhost.com',
            'access_token': 'ACCESS_TOKEN',
            'refresh_token': 'REFRESH_TOKEN'
        }

    @pytest.fixture
    def module_mock(self, mocker):
        mocker.patch('time.sleep')
        return mocker.patch.multiple(basic.AnsibleModule, exit_json=exit_json, fail_json=fail_json)

    @pytest.fixture
    def open_url_mock(self, mocker):
        return mocker.patch('library.generated.ftd_deployment.open_url')

    @pytest.mark.parametrize('missing_parameter', ['hostname', 'access_token', 'refresh_token'])
    def test_module_should_fail_without_required_arguments(self, module_args, module_mock, missing_parameter):
        del module_args[missing_parameter]

        set_module_args(module_args)
        with pytest.raises(AnsibleFailJson) as ex:
            self.module.main()

        assert ("missing required arguments: %s" % missing_parameter) in str(ex)

    def test_module_should_fail_when_deployment_request_fails(self, module_args, module_mock, open_url_mock):
        open_url_mock.side_effect = self.http_error(400, {'err': 'There is already a deployment task pending.'})

        set_module_args(module_args)
        with pytest.raises(AnsibleFailJson) as ex:
            self.module.main()

        result = ex.value.args[0]
        assert result['error_code'] == 400
        assert 'There is already a deployment task pending.' in str(result)

    def test_module_should_fail_when_deployment_fails(self, module_args, module_mock, open_url_mock):
        open_url_mock.side_effect = [
            StringIO(json.dumps({'id': '123123'})),
            StringIO(json.dumps({'endTime': -1, 'state': 'DEPLOYING'})),
            StringIO(json.dumps({'endTime': 1529575653, 'state': 'DEPLOY_FAILED'})),
        ]

        set_module_args(module_args)
        with pytest.raises(AnsibleFailJson) as ex:
            self.module.main()

        result = ex.value.args[0]
        assert not result['changed']
        assert result['status']['state'] == 'DEPLOY_FAILED'

    def test_module_should_pass_when_deployment_completes(self, module_args, module_mock, open_url_mock):
        open_url_mock.side_effect = [
            StringIO(json.dumps({'id': '123123'})),
            StringIO(json.dumps({'endTime': -1, 'state': 'DEPLOYING'})),
            StringIO(json.dumps({'endTime': 1529575653, 'state': 'DEPLOYED'})),
        ]

        set_module_args(module_args)
        with pytest.raises(AnsibleExitJson) as ex:
            self.module.main()

        result = ex.value.args[0]
        assert result['changed']
        assert result['status']['state'] == 'DEPLOYED'

    def test_module_should_fail_when_timeout_exceeded(self, module_args, module_mock, open_url_mock, mocker):
        open_url_mock.side_effect = [
            StringIO(json.dumps({'id': '123123'})),
            StringIO(json.dumps({'endTime': -1, 'state': 'DEPLOYING'})),
            StringIO(json.dumps({'endTime': -1, 'state': 'DEPLOYING'})),
        ]
        time_mock = mocker.patch('time.time')
        time_mock.side_effect = [10, 16]
        module_args['timeout'] = 5

        set_module_args(module_args)
        with pytest.raises(AnsibleFailJson) as ex:
            self.module.main()

        assert "Deployment Timeout. The job was not completed within the given time limits." in str(ex)

    @staticmethod
    def http_error(status_code, body):
        err_msg = StringIO(json.dumps(body))
        return HTTPError('http://testhost.com', status_code, '', {}, err_msg)
