# print("hello oexp 1")

import os
from distutils.util import strtobool

# print("hello oexp 2")

RE_GEN = os.getenv("RE_GEN")
VERBOSE = os.getenv("VERBOSE")
VERBOSE = False if VERBOSE is None else strtobool(VERBOSE)

# WARN_IF_OLD = os.getenv("WARN_IF_OLD")
# WARN_IF_OLD = True if WARN_IF_OLD is None else strtobool(WARN_IF_OLD)


# print("hello oexp 3")


def prepare_local_oexp():

    import subprocess
    from subprocess import PIPE, DEVNULL, STDOUT
    import sys
    from pathlib import Path
    from threading import Thread
    from typing import IO

    this_file = Path(__file__)
    out = PIPE if VERBOSE else DEVNULL
    process = subprocess.Popen(
        args=[
            "/Users/matthewgroth/registered/ide/all/gradlew",
            ":k:oexp:oexpGenSources",
        ],
        stdout=out,
        stderr=out,
        stdin=DEVNULL,
        cwd="/Users/matthewgroth/registered/ide/all/",
    )

    if VERBOSE:

        def relay_out(stream: IO, dest):
            for line in stream.readlines():
                print(line.decode(), file=dest)

        Thread(target=relay_out, args=(process.stderr, sys.stderr)).start()
        relay_out(process.stdout, sys.stdout)

    return_code = process.wait()

    if return_code != 0:
        raise Exception(f"Non-zero return code: {return_code}")

    sys.path.insert(
        0,
        str(this_file.parent.parent),
    )
    import oexp.jbridge

    if oexp.jbridge.LOCAL_JAR is None:
        raise Exception("LOCAL_JAR should be set appropriately if RE_GEN is true")


# print("hello oexp 4")

if RE_GEN:
    # print("hello oexp 5")
    prepare_local_oexp()
    # print("hello oexp 6")


from oexp.access import trial_manifest, gallery_trial, choice_trial, login

# print("hello oexp 7")

__all__ = [
    "login",
    "trial_manifest",
    "gallery_trial",
    "choice_trial",
]

# print("hello oexp 8")

import mstuff

# print("hello oexp 9")

mstuff.warn_if_old("oexp")

# print("hello oexp 10")
