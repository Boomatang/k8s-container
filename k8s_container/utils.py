import os
import logging
import time

logging.basicConfig(format="%(asctime)s %(levelname)s: %(message)s", level=logging.INFO)


def get_env_as_digit(env: str) -> (int, int):
    value: str = os.getenv(env)
    if value is None:
        logging.error(f"env var {env} not set")
        return None, 1
    elif not value.isdigit():
        logging.error(f"env var {env} is not a digit")
        return None, 1
    else:
        value: int = int(value)
        return value, 0


def action(loop: str, delay: str):
    error = 0
    _loop, status = get_env_as_digit(loop)
    error += status

    _delay, status = get_env_as_digit(delay)
    error += status

    if error > 0:
        logging.critical("exited early due to errors")
        exit(1)

    for i in range(_loop):
        logging.info(f"loop {i+1} of {_loop}, sleep delay is: {_delay} second")
        time.sleep(_delay)
