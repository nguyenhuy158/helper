"""Docker management commands for the helper CLI.

Split by concern:
- core:        Verbosity, check_docker, get_container_ports
- cli:         the `docker` click group
- containers:  ps, run, rm
- images:      rmi
- urls:        url (containers with their HTTP/HTTPS URLs)
- maintenance: clean, disk-used

Importing this package registers every subcommand on the group.
"""

# Importing these modules attaches their subcommands to the group.
from . import containers as containers
from . import images as images
from . import maintenance as maintenance
from . import urls as urls
from .cli import docker as docker
from .core import (
    Verbosity as Verbosity,
)
from .core import (
    check_docker as check_docker,
)
from .core import (
    format_output as format_output,
)
from .core import (
    get_container_ports as get_container_ports,
)
from .core import (
    get_verbosity as get_verbosity,
)
