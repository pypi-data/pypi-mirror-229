import argparse


class ArgParser:
    def __init__(self, description: str):
        self._parser = argparse.ArgumentParser(description)

    def flag(self, name: str, help: str, short: str = None):
        self._parser.add_argument(
            f"-{short}" if short is not None else f"-{name[0]}",
            f"--{name}",
            action="store_true",
            help=help
        )

    def int(self, name: str, help: str, short: str = None):
        self._parser.add_argument(
            f"-{short}" if short is not None else f"-{name[0]}",
            f"--{name}",
            help=help,
            type=int
        )

    def parse_args(self):
        return self._parser.parse_args()
