import pytest

from rpi_cmdline_config.rpi_cmdline_config import KernelParams

class TestFixtures:

    def test_fixtures(self, default_string, default_params):
        assert default_params.to_string() == default_string


class TestTokenize():

    def test_default_string(self, default_string, default_params):

        for i, val in enumerate(KernelParams(default_string).params):
            assert val == default_params.params[i]

    def test_empty_string(self, empty_string):
        params = KernelParams(empty_string)
        assert len(params.params) == 0



class TestAddparam():

    def test_param_presence(self, default_string, default_params):

        p = KernelParams(default_string)
        p.params.insert(3, {'key': 'testKey', 'value': ['testVal']})

        default_params.add_param(key = 'testKey',  values = ['testVal'], after='root')

        assert p.params == default_params.params


    def test_uniqueness(self, default_params):

        default_params.add_param('modules-load', ['dwc2'], 'rootwait', True)
        default_params.add_param('modules-load', ['g_ether'], 'rootwait', True)

        for p in default_params.params:
            if p['key'] == 'modules-load':
                assert 'dwc2' in p['value']
                assert 'g_ether' in p['value']


    def test_atom_uniqueness(self, default_params):

        default_params.add_param(
            key='modules-load',
            values=None,
            after='rootwait'
        )

        count = 0
        for p in default_params.params:
            if p['key'] == 'modules-load':
                count += 1
        assert count == 1


    def test_atom_non_uniqueness(self, default_params):

        default_params.add_param(
            key = 'modules-load',
            values = None,
            after = 'rootwait',
            unique = False
        )
        default_params.add_param(
            key = 'modules-load',
            values = None,
            after = 'rootwait',
            unique = False
        )

        count = 0
        for p in default_params.params:
            if p['key'] == 'modules-load':
                count += 1
        assert count == 2


    def test_non_uniqueness(self, default_params):

        default_params.add_param(
            key = 'modules-load',
            values = ['dwc2'],
            after = 'rootwait',
            unique = False
        )
        default_params.add_param(
            key = 'modules-load',
            values = ['g_ether'],
            after = 'rootwait',
            unique = False
        )

        count = 0
        for p in default_params.params:
            if p['key'] == 'modules-load':
                count += 1
                assert len(p['value']) == 1
                assert ('g_ether' in p['value']) ^ ('dwc2' in p['value'])
        assert count == 2


    def test_before(self, default_params):

        default_params.add_param(
            key = 'quiet',
            values = None,
            before = 'rootwait'
        )
        assert default_params.to_string().endswith(" quiet rootwait")


    def test_after(self, default_params):
        default_params.add_param(
            key = 'quiet',
            values = None,
            after='rootwait'
        )
        assert default_params.to_string().endswith(" rootwait quiet")


    def test_multiple_non_uniques(self, default_string):


        p = KernelParams("root=PARTUUID=0f6fe73a-02 rootfstype=ext4 fsck.repair=yes rootwait")
        p.add_param(
            key = 'console',
            values = ['serial0', '115200'],
            before = 'root',
        )
        p.add_param(
            key = 'console',
            values = ['tty1'],
            before = 'root',
            unique = False,
        )
        assert p.to_string() == default_string
        



class TestToString():

    def test_toString(self, default_string, default_params):

        assert default_string == default_params.to_string()


    def test_add_modules_load(self, default_string):

        test_string = KernelParams(default_string).add_param(
            key = 'modules-load',
            values = ['dwc2', 'g_ether'],
            after = 'rootwait'
        ).to_string()

        assert test_string == default_string + " modules-load=dwc2,g_ether"

