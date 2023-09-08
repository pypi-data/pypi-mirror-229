"""Automatically rich highlight arbitrary text output in your terminal."""
import sys
from argparse import ArgumentParser
from rich.console import Console

def run():
    """Run richify on input via stdin and return output on stdout."""
    parser = ArgumentParser(description='Rich format arbitrary text input')
    parser.add_argument('--color', choices=['never', 'auto', 'always'], default='auto')
    args = parser.parse_args()

    console = Console(
        force_terminal=(args.color == 'always') or None,
        highlight=(args.color != 'never')
    )

    while True:
        try:
            line = sys.stdin.readline()
        except UnicodeDecodeError:
            continue
        except KeyboardInterrupt:
            break
        except (BrokenPipeError, IOError):
            sys.stderr.close()
            sys.exit()
        if not line:
            break
        console.print(line, end='')

if __name__ == "__main__":
    run()
