# spdx-license-identifier: gpl-3.0-only
# Copyright (C) 2022 Michał Góral

from typing import Any, Optional, Dict, Union

import os
import sys
import base64
import logging
from urllib.parse import urljoin
from argparse import Namespace

import requests

from ns.config import Config


log = logging.getLogger(__name__)


def get_auth(c: Config) -> bytes:
    auth, creds = None, None
    enc = "utf-8"

    if c.token:
        return f"Bearer {c.token}".encode(enc)
    elif c.username or c.password:
        auth = "Basic "
        creds = f"{c.username}:{c.password}"
        return auth.encode(enc) + base64.b64encode(creds.encode(enc))

    return None


def set_header(name: str, headers: Dict[str, Union[str, bytes]], val: Optional[Any]):
    if val is not None:
        headers[name] = val


def send(args: Namespace, c: Config) -> bool:
    if not c.server:
        log.error("No server URL configured. Please use --server option.")
        sys.exit(1)

    url = urljoin(c.server, args.topic)

    headers = {}
    auth = get_auth(c)
    if auth:
        headers["Authorization"] = auth

    if args.priority:
        headers["Priority"] = str(args.priority)

    if args.title:
        headers["Title"] = str(args.title)

    if args.tags:
        headers["Tags"] = ",".join(args.tags)

    if args.attach:
        headers["Attach"] = args.attach

    if args.icon:
        headers["Icon"] = args.icon

    if args.click:
        headers["Click"] = args.click

    if args.at:
        headers["At"] = args.at

    if args.actions:
        headers["Actions"] = ";".join(args.actions)

    # message is a local path and should be treated as attachment
    if args.message and os.path.exists(args.message):
        with open(args.message, "rb") as mf:
            headers["Filename"] = os.path.basename(args.message)
            args.message = mf.read()

    kw = {"headers": headers}
    if args.message:
        kw["data"] = args.message
    resp = requests.post(url, **kw)

    if resp.text:
        log.info(resp.text.strip())

    if not resp.ok:
        log.error("Sending notification failed")
        return False

    return True
