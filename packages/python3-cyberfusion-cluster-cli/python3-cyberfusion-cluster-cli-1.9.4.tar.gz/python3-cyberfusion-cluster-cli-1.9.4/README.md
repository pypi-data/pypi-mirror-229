# python3-cyberfusion-cluster-cli

CLI for Cyberfusion Cluster API.

# Install

## PyPI

Run one of the following commands to install the package from PyPI.

### Recommended

    pip3 install python3-cyberfusion-cluster-cli

### Optional: with Borg support

    pip3 install python3-cyberfusion-cluster-cli[borg]

This installs dependencies needed to manage Borg, which do not work on all operating systems.

## Generic

Run the following command to create a source distribution:

    python3 setup.py sdist

# Configure

When running the CLI for the first time, run the following command:

    clusterctl setup

The command will prompt you for API credentials.

This creates a config file in `~/.config/cyberfusion/cyberfusion.cfg`.

# Usage

The CLI provides commands for all relevant API endpoints.

Run the following command for help:

    clusterctl -h

# Tests

No tests are present.
