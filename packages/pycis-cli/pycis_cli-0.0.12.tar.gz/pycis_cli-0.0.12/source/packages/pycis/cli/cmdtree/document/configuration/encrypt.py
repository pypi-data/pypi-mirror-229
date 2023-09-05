
__author__ = "Myron Walker"
__copyright__ = "Copyright 2023, Myron W Walker"
__credits__ = []
__version__ = "1.0.0"
__maintainer__ = "Myron Walker"
__email__ = "myron.walker@gmail.com"
__status__ = "Development" # Prototype, Development or Production
__license__ = "MIT"

import json

import click

HELP_DOCUMENT = "A configuration document to encrypt."
HELP_PASSPHRASE = "A passphrase to use to encrypt the file."

@click.command("encrypt")
@click.option("--document", required=True, type=click.Path(exists=True, file_okay=True, dir_okay=False), help=HELP_DOCUMENT)
@click.option("--passphrase", required=True, help=HELP_PASSPHRASE)
@click.argument('filename', metavar='<testrun document>', type=click.Path(dir_okay=False))
def command_pycis_document_configuration_encrypt(document: str, passphrase: str, filename: str):

    from mojo.config.cryptography import (
        create_encrypted_configuration, generate_fernet_key
    )

    key = generate_fernet_key(passphrase)

    encrypted_config = None

    with open(document, 'r') as cf:
        ccontent = cf.read()
        encrypted_config = create_encrypted_configuration(key, ccontent)

    if encrypted_config is not None:
        with open(filename, 'w+') as ecf:
            json.dump(encrypted_config, ecf, indent=4)

    return