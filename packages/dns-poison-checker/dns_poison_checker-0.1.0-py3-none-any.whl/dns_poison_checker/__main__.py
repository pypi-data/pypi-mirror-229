import os.path

import click

from dns_poison_checker import __version__
from dns.resolver import Resolver


def print_version(ctx: click.Context, _, value: str):
    if not value or ctx.resilient_parsing:
        return

    click.echo(__version__)
    ctx.exit()


@click.command()
@click.option('--version', help='Show version information.', is_flag=True, callback=print_version, expose_value=False,
              is_eager=True)
@click.option('-i', '--internal', help='Internal DNS server', type=str, required=True)
@click.option('-e', '--external', help='External DNS server', type=str, required=True)
@click.argument('domain', type=str)
def cli(internal: str, external: str, domain: str):
    """A tool to check spoofing between internal and external DNS servers."""

    poison_hosts = [
        line.strip() for line in
        open(os.path.join(os.path.dirname(__file__), 'poison_hosts'), 'r', encoding='ascii').readlines()
    ]

    in_resolver = Resolver()
    in_resolver.nameservers = [internal]

    ex_resolver = Resolver()
    ex_resolver.nameservers = [external]

    in_answers = [answer.to_text() for answer in in_resolver.query(domain, 'A')]
    ex_answers = [answer.to_text() for answer in ex_resolver.query(domain, 'A')]
    click.echo(f'Query for domain: {domain}')
    click.echo('External DNS answers:')
    for text in ex_answers:
        click.echo(f'      A {text}')

    click.echo('Internal DNS answers:')
    for text in in_answers:
        if text in ex_answers:
            click.echo(click.style(f' [OK] A {text}', fg='green'))
        elif text in poison_hosts:
            click.echo(click.style(f' [PO] A {text}', fg='red'))
        else:
            click.echo(click.style(f' [IN] A {text}', fg='yellow'))


if __name__ == '__main__':
    cli()
