"""Module to invoke Akamai Fastpurge via simple CLI utility."""
import os
import validators.url
import validators.utils
import click
from fastpurge import FastPurgeClient

# @click.group(name='purgeit')
# @click.pass_context
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

def mgpurge(paths: list, dryrun: bool) -> None:
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
    urlerrors = [(validators.url(path)) for path in paths if not validators.url(path)]
    # urlerrors = []
    # for path in paths:
    #     if not validators.url(path):
    #         urlerrors.append(path)

    if len(urlerrors) > 0:
        click.secho(message="THESE PATHS ARE INVALID!!!...", color=True, fg="bright_red")
        # pylint: disable=expression-not-assigned
        [(click.secho(message=error, color=True, fg="red")) for error in urlerrors]

        return

    click.echo(message="These paths will be purged...")
    # pylint: disable=expression-not-assigned
    [(click.secho(message=path, color=True, fg="blue")) for path in paths]

    if dryrun:
        return
    click.confirm(text='Would you like to proceed? [yes/no]', default=False, abort=True)
    # Start purge of some URLs
    # purge is a Future, if we want to ensure purge completed
    # we can block on the result:
    purge_cmd = client.purge_by_url(urls=paths)
    result = purge_cmd.result()
    click.secho(message="Purge Completed!", color=True, fg="green")
    click.secho(message=result, color=True, fg="black")

if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    mgpurge()
