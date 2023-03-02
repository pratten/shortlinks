import argparse
import sys
import os
import qrcode

from textwrap import dedent
from pathlib import Path
from typing import List, Tuple

SCRIPT_PATH = Path(__file__).parent.absolute()


def main() -> int:
    # Handle program arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("link_file", help="File containing redirect rules")
    ap.add_argument("-o",
                    "--output",
                    help="Output directory",
                    default="build",
                    type=Path)
    args = ap.parse_args()

    # Parse the link file into a list of redirections
    redirects: List[Tuple[str, str]] = []
    with open(args.link_file, "r") as fp:
        for line in fp.readlines():
            line = line.strip()

            # Skip comments
            if line == "" or line.startswith("#"):
                continue

            # Split into source and destination URLs
            source, dest = line.split(" ", 1)
            if source.startswith("/"):
                source = source[1:]
            print(f"Found redirect: {source} -> {dest}")
            redirects.append((source, dest))

    # (re)create the output directory
    if os.path.exists(args.output):
        os.system(f"rm -rf {args.output}")
    os.mkdir(args.output)

    # Copy the 404 page
    os.system(f"cp {SCRIPT_PATH}/404.html {args.output}/404.html")

    # Create files for each link
    for source, dest in redirects:
        # Create the output directory
        out_dir = args.output / source
        out_dir.mkdir(parents=True, exist_ok=True)

        # Write the redirect HTML file
        out_dir.joinpath("index.html").write_text(
            dedent(f"""
            <!DOCTYPE html>
            <html>
                <head>
                    <meta http-equiv="refresh" content="0; url={dest}" />
                    <link rel="canonical" href="{dest}" />
                    <title>Redirecting...</title>
                </head>
                <body>
                    <h1>Redirecting...</h1>
                    <p>If your browser does not redirect you automatically, <a href="{dest}">click here</a>.</p>
                </body>
            </html>
            """))

        # Generate a QR code for the destination
        qr = qrcode.make(dest)

        # Write the QR code to a file
        qr.save(out_dir.joinpath("qr.png"))

    # Load the index, substitute in links, and write to output
    index = open(SCRIPT_PATH.joinpath("index.html"), "r").read()
    index = index.replace(
        "<LINK_LIST>", "\n".join([
            f"<li><a href='https://short.pratten.ca/{source}'>https://short.pratten.ca/{source}</a></li>"
            for source, _ in redirects
        ]))
    open(args.output.joinpath("index.html"), "w").write(index)

    return 0


if __name__ == "__main__":
    sys.exit(main())