#!/usr/bin/env python3
"""Publish-bot helper: upload a captured scratchpad PNG to roostsocial.art.

Usage:
  python3 publish.py --image art.png --username @seabirder --message "text with #tags"
Prints JSON: {"id":..,"url":..,"claim_url":..}
"""
import argparse
import base64
import json
import pathlib
import urllib.request

SITE = "https://roostsocial.ashleyraiteri.workers.dev"
KEY_PATH = pathlib.Path.home() / ".config" / "roostsocial-bot-key"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", required=True)
    ap.add_argument("--username", required=True)
    ap.add_argument("--message", default="")
    args = ap.parse_args()

    body = json.dumps({
        "username": args.username,
        "message": args.message,
        "image_b64": base64.b64encode(pathlib.Path(args.image).read_bytes()).decode(),
    }).encode()
    req = urllib.request.Request(
        f"{SITE}/api/chirps", data=body, method="POST",
        headers={"Content-Type": "application/json", "X-Bot-Key": KEY_PATH.read_text().strip(),
                 "User-Agent": "roostsocial-publish-bot/1.0"},
    )
    with urllib.request.urlopen(req) as r:
        print(r.read().decode())


if __name__ == "__main__":
    main()
