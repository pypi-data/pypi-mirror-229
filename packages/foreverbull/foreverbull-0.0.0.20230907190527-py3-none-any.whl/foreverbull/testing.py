import time
from contextlib import contextmanager
from socket import gethostname

import pytest

from foreverbull import Foreverbull, broker, models
from foreverbull.broker.socket.client import ContextClient, SocketClient


class Execution:
    def __init__(self, execution: models.backtest.Execution, foreverbull: Foreverbull, socket: ContextClient):
        self.execution = execution
        self._socket = socket
        self._fb = foreverbull

    def run(self):
        self._fb.run_execution()
        self._socket.send(models.service.Request(task="run_execution"))
        rsp = self._socket.recv()
        if rsp.error:
            raise Exception("run_execution failed: ", rsp.error)
        for _ in range(10):
            # Seems like we are a bit too fast sometimes
            try:
                return self._fb.get_backtest_result(self.execution.id)
            except Exception as exc:
                if exc.code != "NoSuchKey":
                    raise
                time.sleep(0.2)
        raise Exception("backtest finish, but could not find results")


class BacktestSession:
    def __init__(self, backtest: str):
        self.backtest = backtest
        self._session: dict

    def __enter__(self):
        self._session = broker.backtest.new_session(self.backtest, "test", gethostname())
        while self._session["socket"] is None:
            if self._session["error"]:
                raise Exception("backtest failed to start: ", self._session["error"])
            time.sleep(0.2)
            self._session = broker.backtest.get_session(self.backtest, self._session["id"])
        socket_config = models.service.SocketConfig(
            host="127.0.0.1",
            port=self._session["socket"]["port"],
            socket_type=models.service.SocketType.REQUESTER,
            listen=False,
            recv_timeout=60000,
            send_timeout=60000,
        )
        self._socket = SocketClient(socket_config)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.process(models.service.Request(task="stop"))
        self._socket.close()

    def process(self, request: models.service.Request) -> models.service.Response:
        sock = self._socket.new_context()
        sock.send(request)
        return sock.recv()

    @contextmanager
    def new_execution(self, execution: models.backtest.Execution, algo: callable) -> Execution:
        rsp = self.process(models.service.Request(task="new_execution", data=execution))
        if rsp.error:
            raise Exception("new_execution failed: ", rsp.error)

        execution = models.backtest.Execution(**rsp.data)
        Foreverbull.set_algo(algo)
        foreverbull = Foreverbull()
        foreverbull.start()
        foreverbull.setup()
        try:
            ctx_socket = self._socket.new_context()
            ctx_socket.send(models.service.Request(task="get_configuration"))
            rsp = ctx_socket.recv()
            configuration = models.backtest.Execution(**rsp.data)
            configuration.socket.host = "127.0.0.1"  # HACK
            foreverbull.configure_execution(configuration)
            yield Execution(execution, foreverbull, ctx_socket)
        finally:
            foreverbull.stop()
            ctx_socket.close()


@pytest.fixture(scope="function")
def execution():
    execution = Execution()
    with execution:
        yield execution
