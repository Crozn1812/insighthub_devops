"""Durable event worker with MCP facts and explicit capture/Slack transport."""
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
from .transport import CaptureTransport, ResultTransport, SlackTransport
from .model_summary import summarize
from .actions import route_action
from .intents import Intent

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
    result = asyncio.run(controller.process(event))
    action = route_action(event.text).action
    if action in {intent.value for intent in Intent if intent is not Intent.UNKNOWN}:
        return summarize(result, settings)
    return result


class Worker:
    def __init__(self, queue: EventQueue, transport: ResultTransport, settings: Settings) -> None:
        self.queue = queue
        self.transport = transport
        self.settings = settings

    def handle(self, event: ChatEvent) -> str:
        try:
            result = self.queue.result(event)
            if result is None:
                result = process_event(event)
                self.queue.save_result(event, result)
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
    if settings.transport == "slack":
        transport = SlackTransport(settings.slack_bot_token or "")
    elif settings.transport == "local":
        transport = CaptureTransport(client, settings.result_key)
    else:
        raise ValueError("Unsupported ChatOps transport")
    worker = Worker(queue, transport, settings)
    running = True

    def stop(_signum: int, _frame: object) -> None:
        nonlocal running
        running = False

    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)
    logger.info("worker_started transport=%s", settings.transport)
    # A crashed worker leaves the event in processing. A new exclusive consumer
    # recovers it; cached results prevent repeating an already completed action.
    lease = client.lock(settings.queue_key + ":consumer", timeout=300,
                        blocking_timeout=1)
    if not lease.acquire():
        raise RuntimeError("ChatOps consumer already running")
    try:
        queue.recover_pending()
        while running:
            lease.reacquire()
            queue.promote_due_retries()
            event = queue.dequeue(timeout=1)
            if event is not None:
                try:
                    worker.handle(event)
                except RuntimeError:
                    logger.warning("delivery_or_processing_failed event_id=%s", event.event_id)
                    if event.attempt + 1 >= settings.max_attempts:
                        queue.dead_letter(event)
                    else:
                        retry = ChatEvent(**{**event.__dict__, "attempt": event.attempt + 1})
                        queue.schedule_retry(retry, settings.retry_base_seconds * 2 ** event.attempt)
                    queue.acknowledge(event)
                else:
                    queue.acknowledge(event)
    finally:
        lease.release()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    run_forever()
