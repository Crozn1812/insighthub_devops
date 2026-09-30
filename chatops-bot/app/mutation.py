"""Fixed, constrained scale executor using a dedicated kubeconfig."""
import json
import subprocess


class MutationError(RuntimeError):
    pass


class ScaleExecutor:
    def __init__(self, kubeconfig: str | None, kubectl_command: str = "kubectl") -> None:
        self.kubeconfig = kubeconfig
        self.kubectl_command = kubectl_command

    def scale_api(self, replicas: int) -> None:
        if type(replicas) is not int or not 1 <= replicas <= 5:
            raise MutationError("replica count is outside policy")
        if not self.kubeconfig:
            raise MutationError("mutation identity is not configured")
        patch = json.dumps({"spec": {"replicas": replicas}}, separators=(",", ":"))
        command = [
            self.kubectl_command, "--kubeconfig", self.kubeconfig,
            "-n", "insighthub-dev", "patch", "deployment", "insighthub-api",
            "--subresource=scale", "--type=merge", "-p", patch,
        ]
        try:
            completed = subprocess.run(command, shell=False, capture_output=True,
                                       text=True, timeout=20, check=False)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise MutationError("scale operation unavailable") from exc
        if completed.returncode != 0:
            raise MutationError("scale operation denied or failed")
