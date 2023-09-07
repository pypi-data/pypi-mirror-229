import typing as t
from datetime import datetime
from pathlib import Path

import pydantic


class DockerHealthcheckConfig(pydantic.BaseModel):
    """
    HealthcheckConfig holds configuration settings for the HEALTHCHECK feature.

    Test is the test to perform to check that the container is healthy.
    An empty slice means to inherit the default.
    The options are:
    {} : inherit healthcheck
    {"NONE"} : disable healthcheck
    {"CMD", args...} : exec arguments directly
    {"CMD-SHELL", command} : run command with system's default shell

    Reference:
        https://github.com/moby/moby/blob/791549508a3ed3b95d00556d53940b24a54d901a/image/spec/specs-go/v1/image.go
    """

    interval: t.Optional[pydantic.NonNegativeInt] = pydantic.Field(default=None, alias="Interval")
    timeout: t.Optional[pydantic.NonNegativeInt] = pydantic.Field(default=None, alias="Timeout")
    start_period: t.Optional[pydantic.NonNegativeInt] = pydantic.Field(
        default=None, alias="StartPeriod"
    )
    start_interval: t.Optional[pydantic.NonNegativeInt] = pydantic.Field(
        default=None, alias="StartInterval"
    )
    retries: t.Optional[pydantic.NonNegativeInt] = pydantic.Field(default=None, alias="Retries")


class DockerContainerConfig(pydantic.BaseModel):
    """
    Config contains the configuration data about a container.
    It should hold only portable information about the container.
    Here, "portable" means "independent from the host we are running on".
    Non-portable information *should* appear in HostConfig.
    All fields added to this struct must be marked `omitempty` to keep getting
    predictable hashes from the old `v1Compatibility` configuration.

    Reference:
        https://github.com/moby/moby/blob/791549508a3ed3b95d00556d53940b24a54d901a/api/types/container/config.go
    """

    hostname: str = pydantic.Field(default="", alias="Hostname")
    domainname: str = pydantic.Field(default="", alias="Domainname")
    user: str = pydantic.Field(default="", alias="User")
    attach_stdin: bool = pydantic.Field(default=False, alias="AttachStdin")
    attach_stdout: bool = pydantic.Field(default=False, alias="AttachStdout")
    attach_stderr: bool = pydantic.Field(default=False, alias="AttachStderr")
    exposed_ports: t.Optional[t.Set[pydantic.PositiveInt]] = pydantic.Field(
        default=None, alias="ExposedPorts"
    )
    tty: bool = pydantic.Field(default=False, alias="Tty")
    open_stdin: bool = pydantic.Field(default=False, alias="OpenStdin")
    stdin_once: bool = pydantic.Field(default=False, alias="StdinOnce")
    env: t.Optional[t.List[str]] = pydantic.Field(default=None, alias="Env")
    cmd: t.Optional[t.Union[str, t.List[str]]] = pydantic.Field(default=None, alias="Cmd")
    healthcheck: t.Optional[DockerHealthcheckConfig] = pydantic.Field(
        default=None, alias="Healthcheck"
    )
    args_escaped: bool = pydantic.Field(default=None, alias="ArgsEscaped")
    image: str = pydantic.Field(default="", alias="Image")
    volumes: t.Dict[str, str] = pydantic.Field(default_factory=dict, alias="Volumes")
    working_dir: str = pydantic.Field(default="", alias="WorkingDir")
    entrypoint: t.Optional[t.Union[str, t.List[str]]] = pydantic.Field(
        default=None, alias="Entrypoint"
    )
    network_disabled: t.Optional[bool] = pydantic.Field(default=None, alias="NetworkDisabled")
    mac_address: t.Optional[str] = pydantic.Field(default=None, alias="MacAddress")
    on_build: t.Optional[t.List[str]] = pydantic.Field(default=None, alias="OnBuild")
    labels: t.Optional[t.Dict[str, str]] = pydantic.Field(default=None, alias="Labels")
    stop_signal: t.Optional[str] = pydantic.Field(default=None, alias="StopSignal")
    stop_timeout: t.Optional[int] = pydantic.Field(default=None, alias="StopTimeout")
    shell: t.Optional[t.Union[str, t.List[str]]] = pydantic.Field(default=None, alias="Shell")


class DockerLayer(pydantic.BaseModel):
    id: str
    created_at: datetime = pydantic.Field(default_factory=datetime.utcnow, alias="created")
    parent_id: t.Optional[str] = pydantic.Field(default=None, alias="parent")


def create_file_layer(file_path: Path, layer_tar_path: Path):
    pass


def create_files_image(file_layer_tar_paths: t.List[Path], image_path: Path):
    pass
