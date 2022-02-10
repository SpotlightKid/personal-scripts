#!/usr/bin/env python3
"""A script to send pastes to https://cpaste.org/."""

#######################################################################
#
# A script to paste to https://cpaste.org/
#
# Copyright (c) 2013-2019 Andreas Schneider <asn@samba.org>
# Copyright (c) 2013      Alexander Bokovoy <ab@samba.org>
# Copyright (c) 2022      Christopher Arndt <info@chrisarndt.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#######################################################################
#
# Requires: python3-requests
# Requires: python3-cryptography
#
# Optionally requires: python-Pygments
#

import argparse
import base64
import json
import os
import sys
import zlib
from mimetypes import guess_type

import requests
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

try:
    from pygments.lexers import guess_lexer, guess_lexer_for_filename

    guess_lang = True
except ImportError:
    guess_lang = False


def base58_encode(v):
    # 58 char alphabet
    alphabet = b"123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    alphabet_len = len(alphabet)

    if isinstance(v, str) and not isinstance(v, bytes):
        v = v.encode("ascii")

    nPad = len(v)
    v = v.lstrip(b"\0")
    nPad -= len(v)

    l = 0
    for (i, c) in enumerate(v[::-1]):
        if isinstance(c, str):
            c = ord(c)
        l += c << (8 * i)

    string = b""
    while l:
        l, idx = divmod(l, alphabet_len)
        string = alphabet[idx : idx + 1] + string

    return alphabet[0:1] * nPad + string


def json_encode(d):
    return json.dumps(d, separators=(",", ":")).encode("utf-8")


#
# The encryption format is described here:
# https://github.com/PrivateBin/PrivateBin/wiki/Encryption-format
#
def privatebin_encrypt(
    paste_passphrase,
    paste_password,
    paste_plaintext,
    paste_formatter,
    paste_attachment_name,
    paste_attachment,
    paste_compress,
    paste_burn,
    paste_opendicussion,
):
    if paste_password:
        paste_passphrase += bytes(paste_password, "utf-8")

    # PBKDF
    kdf_salt = bytes(os.urandom(8))
    kdf_iterations = 100000
    kdf_keysize = 256  # size of resulting kdf_key

    backend = default_backend()
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=int(kdf_keysize / 8),  # 256bit
        salt=kdf_salt,
        iterations=kdf_iterations,
        backend=backend,
    )
    kdf_key = kdf.derive(paste_passphrase)

    # AES-GCM
    adata_size = 128

    cipher_iv = bytes(os.urandom(int(adata_size / 8)))
    cipher_algo = "aes"
    cipher_mode = "gcm"

    compression_type = "none"
    if paste_compress:
        compression_type = "zlib"

    # compress plaintext
    paste_data = {"paste": paste_plaintext}
    if paste_attachment_name and paste_attachment:
        paste_data["attachment"] = paste_attachment
        paste_data["attachment_name"] = paste_attachment_name
        print(paste_attachment_name)
        print(paste_attachment)

    if paste_compress:
        zobj = zlib.compressobj(wbits=-zlib.MAX_WBITS)
        paste_blob = zobj.compress(json_encode(paste_data)) + zobj.flush()
    else:
        paste_blob = json_encode(paste_data)

    # Associated data to authenticate
    paste_adata = [
        [
            base64.b64encode(cipher_iv).decode("utf-8"),
            base64.b64encode(kdf_salt).decode("utf-8"),
            kdf_iterations,
            kdf_keysize,
            adata_size,
            cipher_algo,
            cipher_mode,
            compression_type,
        ],
        paste_formatter,
        int(paste_opendicussion),
        int(paste_burn),
    ]

    paste_adata_json = json_encode(paste_adata)

    aesgcm = AESGCM(kdf_key)
    ciphertext = aesgcm.encrypt(cipher_iv, paste_blob, paste_adata_json)

    # Validate
    # aesgcm.decrypt(cipher_iv, ciphertext, paste_adata_json)

    paste_ciphertext = base64.b64encode(ciphertext).decode("utf-8")

    return paste_adata, paste_ciphertext


def privatebin_send(
    paste_url,
    paste_password,
    paste_plaintext,
    paste_formatter,
    paste_attachment_name,
    paste_attachment,
    paste_compress,
    paste_burn,
    paste_opendicussion,
    paste_expire,
):
    paste_passphrase = bytes(os.urandom(32))

    paste_adata, paste_ciphertext = privatebin_encrypt(
        paste_passphrase,
        paste_password,
        paste_plaintext,
        paste_formatter,
        paste_attachment_name,
        paste_attachment,
        paste_compress,
        paste_burn,
        paste_opendicussion,
    )

    # json payload for the post API
    # https://github.com/PrivateBin/PrivateBin/wiki/API
    payload = {
        "v": 2,
        "adata": paste_adata,
        "ct": paste_ciphertext,
        "meta": {
            "expire": paste_expire,
        },
    }

    # http content type
    headers = {"X-Requested-With": "JSONHttpRequest"}

    r = requests.post(paste_url, data=json_encode(payload), headers=headers)
    r.raise_for_status()

    try:
        result = r.json()
    except:
        print("Oops, error: {}".format(r.text))
        sys.exit(1)

    paste_status = result["status"]
    if paste_status:
        paste_message = result["message"]
        print("Oops, error: {}".format(paste_message))
        sys.exit(1)

    paste_id = result["id"]
    paste_url_id = result["url"]
    paste_deletetoken = result["deletetoken"]

    print(
        "Delete paste: {}/?pasteid={}&deletetoken={}".format(
            paste_url, paste_id, paste_deletetoken
        )
    )
    print("")
    print(
        "### Paste ({}): {}{}#{}".format(
            paste_formatter,
            paste_url,
            paste_url_id,
            base58_encode(paste_passphrase).decode("utf-8"),
        )
    )


def guess_lang_formatter(paste_plaintext, paste_filename=None):
    paste_formatter = "plaintext"

    # Map numpy to python because the numpy lexer gives false positives
    # when guessing.
    lexer_lang_map = {"numpy": "python"}

    # If we have a filename, try guessing using the more reliable
    # guess_lexer_for_filename function.
    # If that fails, try the guess_lexer function on the code.
    lang = None
    if paste_filename:
        try:
            lang = guess_lexer_for_filename(
                paste_filename, paste_plaintext
            ).name.lower()
        except:
            print("No guess by filename")
            pass
    else:
        try:
            lang = guess_lexer(paste_plaintext).name.lower()
        except:
            pass

    if lang:
        if lang == "markdown":
            paste_formatter = "markdown"
        if lang != "text only":
            paste_formatter = "syntaxhighlighting"

    return paste_formatter


def main(args=None):
    ap = argparse.ArgumentParser(usage=__doc__.splitlines()[0])

    ap.add_argument(
        "-f",
        "--file",
        dest="filename",
        metavar="FILE",
        help="Read from a file instead of stdin",
    )
    ap.add_argument(
        "-p", "--password", metavar="PASSWORD", help="Create a password protected paste"
    )
    ap.add_argument(
        "-e",
        "--expire",
        default="1day",
        choices=["5min", "10min", "1hour", "1day", "1week", "1month", "1year", "never"],
        help="Expiration time of the paste (default: 1day)",
    )
    ap.add_argument(
        "-s",
        "--sourcecode",
        action="store_true",
        dest="source",
        default=False,
        help="Use source code highlighting",
    )
    ap.add_argument(
        "-m", "--markdown", action="store_true", help="Parse paste as markdown"
    )
    ap.add_argument("-b", "--burn", action="store_true", help="Burn paste after reading")
    ap.add_argument(
        "-o",
        "--opendiscussion",
        action="store_true",
        help="Allow discussion for the paste",
    )
    ap.add_argument(
        "-a",
        "--attachment",
        metavar="FILE",
        help="Specify path to a file to attachment to the paste",
    )

    args = ap.parse_args(args)

    paste_url = "https://cpaste.org"
    paste_formatter = "plaintext"
    paste_compress = True
    paste_expire = "1day"
    paste_opendicussion = 0
    paste_burn = 0
    paste_password = None
    paste_attachment_name = None
    paste_attachment = None

    if args.filename:
        f = open(args.filename)
        if not f:
            print("Oops, could not open file!")

        paste_plaintext = f.read()
        f.close()
    else:
        paste_plaintext = sys.stdin.read()

    if not paste_plaintext:
        print("Oops, we have no data")
        sys.exit(1)

    if args.burn:
        paste_burn = 1

    if args.opendiscussion:
        paste_opendiscussion = 1

    if args.source:
        paste_formatter = "syntaxhighlighting"
    elif args.markdown:
        paste_formatter = "markdown"
    elif guess_lang:
        paste_formatter = guess_lang_formatter(paste_plaintext, args.filename)

    if args.expire:
        paste_expire = args.expire

    if args.password:
        paste_password = args.password

    if args.attachment:
        paste_attachment_name = os.path.basename(args.attachment)
        mime = guess_type(args.attachment, strict=False)[0]
        if not mime:
            mime = "application/octet-stream"

        f = open(args.attachment)
        if not f:
            print("Oops, could not open file for attachment!")

        data = f.read()
        f.close()

        paste_attachment = "data:{};base64,".format(mime)
        paste_attachment += base64.b64encode(bytes(data, "utf-8")).decode("utf-8")

    privatebin_send(
        paste_url,
        paste_password,
        paste_plaintext,
        paste_formatter,
        paste_attachment_name,
        paste_attachment,
        paste_compress,
        paste_burn,
        paste_opendicussion,
        paste_expire,
    )

    sys.exit(0)


if __name__ == "__main__":
    sys.exit(main() or 0)
