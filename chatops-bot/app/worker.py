"""Bounded local worker skeleton; MCP and real Slack are intentionally absent."""
import logging
import signal
import asyncio

from redis import Redis

from .config import Settings
from .chatops_service import ChatOpsService, clients_from_settings
from .actions import ActionController
from .approvals import ApprovalStore
from .mutation import ScaleExecutor
from .permissions import PermissionEngine
from .queue import ChatEvent, EventQueue
from .transport import CaptureTransport, ResultTransport

logger = logging.getLogger("chatops-bot.worker")


class TransientProcessingError(RuntimeError):
    pass


def process_event(event: ChatEvent) -> str:
    settings = Settings.from_env()
    prometheus, kubernetes = clients_from_settings(settings)
    client = Redis.from_url(settings.redis_url, decode_responses=True)
    controller = ActionController(
        PermissionEngine(),
        ApprovalStore(client, settings.approval_prefix, settings.approval_ttl_seconds),
        ScaleExecutor(settings.mutator_kubeconfig, settings.kubectl_command),
        ChatOpsService(prometheus, kubernetes),
    )
    return asyncio.run(controller.process(event))


class Worker:
    def __init__(self, queue: EventQueue, transport: ResultTransport, settings: Settings) -> None:
        self.queue = queue
        self.transport = transport
        self.settings = settings

    def handle(self, event: ChatEvent) -> str:
        try:
            result = process_event(event)
        except TransientProcessingError:
            next_attempt = event.attempt + 1
            if next_attempt >= self.settings.max_attempts:
                self.transport.send(event, "retry limit reached", status="failed")
                return "failed"
            retry = ChatEvent(**{**event.__dict__, "attempt": next_attempt})
            delay = self.settings.retry_base_seconds * (2 ** event.attempt)
            self.queue.schedule_retry(retry, delay)
            return "retry"
        self.transport.send(event, result)
        return "ok"


def run_forever() -> None:
    settings = Settings.from_env()
    client = Redis.from_url(settings.redis_url, decode_responses=True)
    queue = EventQueue(client, settings)
    worker = Worker(queue, CaptureTransport(client, settings.result_key), settings)
    running = True

    def stop(_signum: int, _frame: object) -> None:
        nonlocal running
        running = False

    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)
    logger.info("worker_started transport=%s", settings.transport)
    while running:
        queue.promote_due_retries()
        event = queue.dequeue(timeout=1)
        if event is not None:
            worker.handle(event)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    run_forever()
