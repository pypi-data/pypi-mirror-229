"""Module to invoke Akamai Fastpurge via simple CLI utility."""
import os
import click
from fastpurge import FastPurgeClient


@click.command()
@click.option(
    "paths",
    "--path",
    "-p",
    multiple=True,
    help="A single URL to Purge (This option is repeatable for additional URLs)",
)
@click.option(
    "--dryrun",
    "-d",
    is_flag=True,
    help="Just print the command and args that will be run and exit",
)
def mgpurge(paths: list[str], dryrun: bool) -> None:
    """
    Module to invoke Akamai Fastpurge via simple CLI utility.
    :param list[str] paths: List of paths to purge from Akamai cache.
    :param bool dryrun: Just print the command and args that will be run and exit
    """
    # Omit credentials to read from ~/.edgerc
    client = FastPurgeClient(
        auth={
            "client_secret": os.environ['AKAMAI_DEFAULT_CLIENT_SECRET'],
            "host": os.environ['AKAMAI_DEFAULT_HOST'],
            "access_token": os.environ['AKAMAI_DEFAULT_ACCESS_TOKEN'],
            "client_token": os.environ['AKAMAI_DEFAULT_CLIENT_TOKEN'],
        }
    )
    if dryrun:
        print("These paths will be purged:")
        for path in paths:
            click.secho(message=path, color=True, fg='bright_white')
            click.confirm(text='Would you like to proceed? [yes/no]', default=False, abort=True)
        return
        # Start purge of some URLs
    # purge is a Future, if we want to ensure purge completed
    # we can block on the result:
    purge_cmd = client.purge_by_url(urls=paths)
    # purge is a Future, if we want to ensure purge completed
    # we can block on the result:
    result = purge_cmd.result()
    print("Purge completed:", result)


if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    mgpurge()
