import pytest

@pytest.fixture
def default_string():
    return "console=serial0,115200 console=tty1 root=PARTUUID=0f6fe73a-02 rootfstype=ext4 fsck.repair=yes rootwait"


@pytest.fixture
def default_params():
    return [
        {
            'key': 'console',
            'value': ['serial0', '115200'],
        },
        {
            'key': 'console',
            'value': ['tty1'],
        },
        {
            'key': 'root',
            'value': ['PARTUUID=0f6fe73a-02'],
        },
        {
            'key': 'rootfstype',
            'value': ['ext4'],
        },
        {
            'key': 'fsck.repair',
            'value': ['yes'],
        },
        {
            'key': 'rootwait',
            'value': None,
        },
    ]


@pytest.fixture
def empty_string():
    return ""