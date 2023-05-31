import sys
import logging

from dotenv import load_dotenv

from .utils import action

logging.basicConfig(format="%(asctime)s %(levelname)s: %(message)s", level=logging.INFO)
load_dotenv()


def basic(*args, **kwargs):
    logging.info("hello world")


def config(*args, **kwargs):
    logging.info("loading LOOP and DELAY from config map")
    action("LOOP", "DELAY")
    logging.info("command finished")


def secret(*args, **kwargs):
    logging.info("loading COUNT and SLEEP from secret")
    action("COUNT", "SLEEP")
    logging.info("command finished")


def no_action(*args, **kwargs):
    logging.error(f"no command: {args[0]}")
    logging.info(f"possible commands are: {', '.join(sorted(cmds))}")


cmds = {
    "basic": basic,
    "config": config,
    "secret": secret,
}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        no_action("None given")
        exit(1)
    
    arg = sys.argv[1:]
    cmd = arg[0]
    cmds.get(cmd, no_action)(*arg)
