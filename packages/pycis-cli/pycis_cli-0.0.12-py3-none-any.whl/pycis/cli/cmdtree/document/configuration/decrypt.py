
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


HELP_DOCUMENT = "A configuration document to decrypt."
HELP_PASSPHRASE = "A passphrase to use to decrypt the file."

@click.command("decrypt")
@click.option("--document", required=True, type=click.Path(exists=True, file_okay=True, dir_okay=False), help=HELP_DOCUMENT)
@click.option("--passphrase", required=True, help=HELP_PASSPHRASE)
@click.argument('filename', metavar='<testrun document>', type=click.Path(dir_okay=False))
def command_pycis_document_configuration_decrypt(document: str, passphrase: str, filename: str):

    from mojo.config.cryptography import (
        decrypt_content, generate_fernet_key
    )

    key = generate_fernet_key(passphrase)

    encrypted_config = None

    with open(document, 'r') as cf:
        encrypted_config =json.load(cf)

    if encrypted_config is not None:
        plain_config = None
        if "encrypted_content" in encrypted_config:
            cipher_config = encrypted_config["encrypted_content"]
            plain_config = decrypt_content(key, cipher_config)
        else:
            plain_config = encrypted_config

        with open(filename, 'w+') as pcf:
            json.dump(plain_config, pcf, indent=4)

    return
