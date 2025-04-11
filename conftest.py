import pytest
import socket
from threading import Thread
from echo_server import run_server


@pytest.fixture(scope="session")
def port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]


@pytest.fixture(scope="session")
def host():
    return "127.0.0.1"


@pytest.fixture(scope="session", autouse=True)
def server(host, port):
    server_thread = Thread(target=run_server, args=(host, port), daemon=True)
    server_thread.start()
    import time
    time.sleep(0.1)
    yield
