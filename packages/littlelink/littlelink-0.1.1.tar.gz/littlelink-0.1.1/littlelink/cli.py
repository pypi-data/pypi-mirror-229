import argparse
from littlelink.generate import run


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--create-config",
        action='store_true',
        default=False,
        help="Creates an empty config file to add services and links.",
    )

    parser.add_argument(
        "--generate",
        action='store_true',
        default=False,
        help="Generate link Page",
    )

    options = parser.parse_args()
    run(vars(options))


if __name__ == '__main__':
    main()

