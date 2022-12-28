import pytest

from rpi_cmdline_config.rpi_cmdline_config import tokenize, add_param, to_string

class TestTokenize():

    def test_default_string(self, default_string, default_params):

        for i, val in enumerate(tokenize(default_string)):
            assert val == default_params[i]

    def test_empty_string(self, empty_string):
        params = tokenize(empty_string)
        assert len(params) == 0



class TestAddparam():

    def test_param_presence(self, default_string, default_params):

        params = tokenize(default_string)
        params.insert(3, {'key': 'testKey', 'value': 'testVal'})
        testParams = add_param(default_params, 'testKey', 'testVal', after='root')

        assert params == testParams

    def test_uniqueness(self, default_params):

        testParams = add_param(default_params, 'modules-load', ['dwc2'], 'rootwait', True)
        testParams = add_param(default_params, 'modules-load', ['g_ether'], 'rootwait', True)

        for p in testParams:
            if p['key'] == 'modules-load':
                assert 'dwc2' in p['value']
                assert 'g_ether' in p['value']


    def test_atom_uniqueness(self, default_params):

        testParams = add_param(default_params, 'modules-load', None, 'rootwait', True)
        testParams = add_param(default_params, 'modules-load', None, 'rootwait', True)

        count = 0
        for p in testParams:
            if p['key'] == 'modules-load':
                count += 1
        assert count == 1


    def test_atom_non_uniqueness(self, default_params):

        testParams = add_param(default_params, 'modules-load', None, 'rootwait', False)
        testParams = add_param(default_params, 'modules-load', None, 'rootwait', False)

        count = 0
        for p in testParams:
            if p['key'] == 'modules-load':
                count += 1
        assert count == 2


    def test_non_uniqueness(self, default_params):

        testParams = add_param(default_params, 'modules-load', ['dwc2'], 'rootwait', False)
        testParams = add_param(default_params, 'modules-load', ['g_ether'], 'rootwait', False)

        count = 0
        for p in testParams:
            if p['key'] == 'modules-load':
                count += 1
                assert len(p['value']) == 1
                assert ('g_ether' in p['value']) ^ ('dwc2' in p['value'])
        assert count == 2



class TestToString():

    def test_toString(self, default_string, default_params):

        assert default_string == to_string(default_params)


    def test_add_modules_load(self, default_string):

        test_string = to_string(add_param(tokenize(default_string), 'modules-load', ['dwc2', 'g_ether'], 'rootwait'))
        assert test_string == default_string + " modules-load=dwc2,g_ether"

