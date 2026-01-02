from dataclasses import dataclass


@dataclass
class ParsedArgs:
    dry_run: bool
    docker_args: str
    agent: str
    agent_args: list[str]
    entrypoint: str | None
    docker_socket: bool
    config_action: str | None
