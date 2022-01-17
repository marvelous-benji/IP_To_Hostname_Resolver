
import pytest

from main import IPResolver, FILE_PATH



@pytest.fixture
def init_instance():
    return IPResolver()

@pytest.fixture
def run_script(init_instance):
    init_instance.execute_request()


def test_constant_variables():
    assert IPResolver.IP_RESOLVER_BASE_URL == "http://ipwhois.app/json", "API url must be set"

def test_initializer(init_instance):
    assert isinstance(init_instance._ip_container,set), "IP container must be a set"
    assert isinstance(init_instance._response, dict), "Response must be a dict"
    assert init_instance._ip_container != set(), "IP container cannot be empty after initialization"

def test_result(run_script, init_instance):
    assert init_instance._response != {}