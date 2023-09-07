"""Generic utilities."""

import configparser
import os
import re
from datetime import datetime, timedelta, timezone
from enum import Enum
from functools import lru_cache, wraps
from http import HTTPStatus
from pathlib import Path
from time import sleep
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Tuple,
    TypeVar,
    Union,
    cast,
)

import plotext as plt
import requests
import typer
from rich.console import Console

from cyberfusion.ClusterApiCli import (
    METHOD_DELETE,
    METHOD_GET,
    METHOD_PATCH,
    METHOD_POST,
    METHOD_PUT,
    ClusterApiCallException,
)
from cyberfusion.ClusterSupport import ClusterSupport, TimeUnit
from cyberfusion.ClusterSupport._interfaces import APIObjectInterface
from cyberfusion.ClusterSupport.api_users_to_clusters import APIUserToCluster
from cyberfusion.ClusterSupport.cmses import CMS
from cyberfusion.ClusterSupport.databases_usages import DatabaseUsage
from cyberfusion.ClusterSupport.haproxy_listens_to_nodes import (
    HAProxyListenToNode,
)
from cyberfusion.ClusterSupport.mail_accounts_usages import MailAccountUsage
from cyberfusion.ClusterSupport.nodes import NodeGroup
from cyberfusion.ClusterSupport.task_collection_results import (
    TASK_STATES_DEFINITIVE,
)
from cyberfusion.ClusterSupport.unix_users_usages import UNIXUserUsage
from cyberfusion.ClusterSupport.virtual_hosts import (
    VirtualHostServerSoftwareName,
)
from cyberfusion.Common import convert_bytes_gib

# Set constants

EMTPY_TO_CLEAR_MESSAGE = "Leave empty to clear"
CONFIRM_MESSAGE = (
    "When --confirm is used, no confirmation prompt will be given"
)
DETAILED_MESSAGE = "Show more information"
RANDOM_PASSWORD_MESSAGE = "Use an empty string for a randomized password"
BOOL_MESSAGE = "[true|false]"

PATH_CONFIG_LOCAL = os.path.join(
    str(Path.home()), ".config", "cyberfusion", "cyberfusion.cfg"
)
PATH_CONFIG_SYSTEM = os.path.join(
    os.path.sep, "etc", "cyberfusion", "cyberfusion.cfg"
)
PATH_CONFIG_ENVIRONMENT = os.environ.get("CLUSTER_CONFIG_FILE", None)

console = Console()
err_console = Console(stderr=True)

# Set function type for decorators

F = TypeVar("F", bound=Callable[..., Optional[int]])

# Set Enums


class HttpMethod(str, Enum):
    """Enum for HTTP methods."""

    GET: str = METHOD_GET
    PATCH: str = METHOD_PATCH
    PUT: str = METHOD_PUT
    POST: str = METHOD_POST
    DELETE: str = METHOD_DELETE


# Error handlers needs to be defined before creating support


def handle_manual_error(message: str) -> None:
    """Handle manually raised error.

    Prints and exits.
    """
    typer.secho("An error occurred:", fg="red")
    typer.secho(message, fg="red")

    raise SystemExit(1)


def handle_api_error(obj: ClusterApiCallException) -> None:
    """Handle error from ClusterApiCallException."""
    typer.secho("An error occurred:", fg="red")

    if obj.status_code in (
        HTTPStatus.BAD_REQUEST,
        HTTPStatus.CONFLICT,
        HTTPStatus.FORBIDDEN,
        HTTPStatus.NOT_FOUND,
    ):
        typer.secho(obj.body["detail"], fg="red")
    elif obj.status_code == HTTPStatus.UNPROCESSABLE_ENTITY:
        for error in obj.body["detail"]:
            typer.secho(
                f"{error['loc'][1]} is invalid: {error['msg']}", fg="red"
            )
    else:
        typer.secho("An unexpected error occurred. Contact support.", fg="red")

    raise SystemExit(1)


def get_config_file_path() -> Optional[str]:
    """Get config file path."""
    if PATH_CONFIG_ENVIRONMENT:
        return PATH_CONFIG_ENVIRONMENT

    for path in [PATH_CONFIG_LOCAL, PATH_CONFIG_SYSTEM]:
        if not os.path.exists(path):
            continue

        return path

    return None


@lru_cache(maxsize=1)
def get_support() -> ClusterSupport:
    """Get ClusterSupport object.

    This is a singleton for efficiency (uses 'lru_cache' to avoid instantiating
    class in the root of this module, as we only want to create a ClusterSupport
    object when it is needed.
    """
    config_file_path = get_config_file_path()

    try:
        return ClusterSupport(
            config_file_path=config_file_path,
        )
    except configparser.Error:
        if config_file_path:
            handle_manual_error(
                f"The config file at '{config_file_path}' exists, but could not be read. If you are running this program on a cluster node, make sure that you're running this command as the root user."
            )
        else:
            handle_manual_error(
                f"Could not find config file. Run 'clusterctl setup' to create config file for the first time. (Tried paths: {PATH_CONFIG_LOCAL}, {PATH_CONFIG_SYSTEM})"
            )
    except ClusterApiCallException as e:
        handle_api_error(e)


# Callback options are kept in this dict
#
# task_check_interval: Interval in seconds for checking task progress. Checking task progress is disabled when this value is 0.

state = {"task_check_interval": 2.0}

# Generic functions


def get_object(
    objects: List[APIObjectInterface], **filters: Any
) -> APIObjectInterface:
    """Get single object, or error if non-existent."""
    try:
        return get_support()._filter_objects(objects, **filters)[0]
    except IndexError:
        name = type(objects[0]).__name__

        _count = 0

        attributes = ""

        for k, v in filters.items():
            _count += 1

            attributes += f"{k}={v}"

            if _count != len(filters.items()):
                attributes += ", "

        handle_manual_error(
            f"Object of type '{name}' with attributes matching '{attributes}' not found"
        )


def get_cms_by_virtual_host_domain(virtual_host_domain: str) -> CMS:
    """Get CMS by virtual host domain."""
    return get_object(
        get_support().cmses,
        virtual_host_id=get_object(
            get_support().virtual_hosts, domain=virtual_host_domain
        ).id,
    )


def get_haproxy_listen_to_node_by_multiple(
    haproxy_listen_name: str,
    node_hostname: str,
) -> HAProxyListenToNode:
    """Get HAProxy listen to node by HAProxy listen name and node hostname."""
    haproxy_listen = get_object(
        get_support().haproxy_listens, name=haproxy_listen_name
    )
    node = get_object(get_support().nodes, hostname=node_hostname)

    return get_object(
        get_support().haproxy_listens_to_nodes,
        haproxy_listen_id=haproxy_listen.id,
        node_id=node.id,
    )


def get_api_user_to_cluster_by_multiple(
    api_user_username: str,
    cluster_name: str,
) -> APIUserToCluster:
    """Get API user to cluster by API user username and cluster name."""
    api_user = get_object(get_support().api_users, username=api_user_username)
    cluster = get_object(get_support().clusters, name=cluster_name)

    return get_object(
        get_support().api_users_to_clusters,
        api_user_id=api_user.id,
        cluster_id=cluster.id,
    )


def get_first_found_virtual_host_server_software(
    cluster_id: int,
) -> Optional[VirtualHostServerSoftwareName]:
    """Get first found virtual host server software by nodes groups."""
    nodes = get_support().get_nodes(cluster_id=cluster_id)

    for node in nodes:
        if NodeGroup.NGINX in node.groups:
            return VirtualHostServerSoftwareName.NGINX

        elif NodeGroup.APACHE in node.groups:
            return VirtualHostServerSoftwareName.APACHE

    return VirtualHostServerSoftwareName.APACHE  # Default


def get_usages_timestamp(
    *, hours_before: Optional[int] = None, days_before: Optional[int] = None
) -> Tuple[datetime, TimeUnit]:
    """Get timestamp and time_unit for requesting usages."""

    # Exit if both are set OR neither is set

    if days_before and hours_before or not days_before and not hours_before:
        handle_manual_error("Use either --days-before OR --hours-before")

    timestamp = datetime.utcnow().replace(tzinfo=timezone.utc)
    time_unit = TimeUnit.HOURLY

    if hours_before:
        timestamp = timestamp - timedelta(hours=hours_before)

    if days_before:
        timestamp = timestamp - timedelta(days=days_before)
        time_unit = TimeUnit.DAILY

    return timestamp, time_unit


def get_usages_plot(
    *,
    usages: List[Union[DatabaseUsage, MailAccountUsage, UNIXUserUsage]],
) -> str:
    """Get plot.

    Hourly interval by default.
    """
    if not usages:
        handle_manual_error("No usages found")

    times = [
        plt.datetime.datetime_to_string(obj.datetime_object) for obj in usages
    ]

    # Convert usage in bytes to GiB

    usages = [convert_bytes_gib(obj.usage) for obj in usages]

    plt.plot_date(times, usages)

    plt.clear_color()
    plt.title("Disk Usage")
    plt.xlabel("Time")
    plt.ylabel("GiB")

    return plt.build()


def catch_api_exception(f: F) -> F:
    """Catch ClusterApiCallException and handle it."""

    @wraps(f)
    def wrapper(*args: tuple, **kwargs: dict) -> None:
        try:
            f(*args, **kwargs)
        except ClusterApiCallException as e:
            handle_api_error(e)

    return cast(F, wrapper)


def exit_with_status(f: F) -> F:
    """Exit with custom status code."""

    @wraps(f)
    def wrapper(*args: tuple, **kwargs: dict) -> None:
        status = f(*args, **kwargs)

        if status is None:
            return

        raise SystemExit(status)

    return cast(F, wrapper)


def wait_for_task(
    *,
    task_collection_uuid: str,
    detailed: bool = False,
    show_skip_message: bool = True,
) -> None:
    """Wait for task_collection to finish."""

    # Skip when task_check_interval is set to 0

    if not state["task_check_interval"]:
        return

    if show_skip_message:
        console.print("\nPress CTRL+C to skip waiting for task to complete")

    results = get_support().task_collection_results(
        task_collection_uuid=task_collection_uuid
    )

    while any(
        result.state not in TASK_STATES_DEFINITIVE for result in results
    ):
        results = get_support().task_collection_results(
            task_collection_uuid=task_collection_uuid
        )

        sleep(state["task_check_interval"])

    console.print("Done!\n")
    console.print(get_support().get_table(objs=results, detailed=detailed))


def delete_api_object(
    *,
    obj: APIObjectInterface,
    confirm: bool,
) -> None:
    """Delete API object."""
    console.print(
        "Data of objects (such as virtual hosts and databases) is not deleted on the cluster. Delete the data yourself if needed."
    )

    if not confirm:
        typer.confirm(
            "Are you sure you want to delete this object?", abort=True
        )

    obj.delete()


def validate_string(
    s: str, *, max_length: int = 253, regex: Optional[str] = None
) -> bool:
    """Validate string using regex.

    When no regex is given, a default will be used and the max length can be set.
    When a custom regex is given, max_length won't work
    """
    if not regex:
        regex = f"^[a-zA-Z0-9-_]{{1,{max_length}}}$"

    return bool(re.fullmatch(re.compile(regex), s))


def _fetch_wordpress_versions() -> Dict[str, str]:
    """Fetch WordPress versions."""
    response = requests.get("https://api.wordpress.org/core/stable-check/1.0/")
    response.raise_for_status()

    return response.json()


def get_latest_wordpress_version() -> str:
    """Get latest WordPress version."""
    try:
        versions = _fetch_wordpress_versions()
    except requests.exceptions.HTTPError:
        handle_manual_error("Could not fetch latest WordPress version")

    # Return the key with value "latest", throw error when key can't be found

    try:
        return list(versions.keys())[list(versions.values()).index("latest")]
    except ValueError:
        handle_manual_error("Could not fetch latest WordPress version")

    # This return will never be reached, but mypy was complaining

    return ""


class WordPressVersionStatus(Enum):
    """Enum for WordPress version status."""

    INSECURE = "insecure"
    OUTDATED = "outdated"
    LATEST = "latest"


def check_wordpress_version(version: str) -> Optional[WordPressVersionStatus]:
    """Check if wordpress version is outdated or insecure."""
    try:
        versions = _fetch_wordpress_versions()
    except requests.exceptions.HTTPError:
        return None

    try:
        if versions[version] == WordPressVersionStatus.INSECURE.value:
            return WordPressVersionStatus.INSECURE
        elif versions[version] == WordPressVersionStatus.OUTDATED.value:
            return WordPressVersionStatus.OUTDATED
        elif versions[version] == WordPressVersionStatus.LATEST.value:
            return WordPressVersionStatus.LATEST
    except KeyError:
        handle_manual_error(
            "Invalid WordPress version, specify a valid version"
        )

    return None


def print_warning(message: str) -> None:
    """Print warning message."""
    typer.secho(f"Warning: {message}", fg="yellow")


def apply_environment_variable(
    environment_variables_obj: Dict[str, str],
    environment_variable_string: str,
) -> None:
    """Parse and apply environment variable from string."""
    split_string = environment_variable_string.split("=", 1)

    if len(split_string) < 2:
        handle_manual_error("Invalid format. Use 'key=value'")

    environment_variables_obj[split_string[0]] = split_string[1]
