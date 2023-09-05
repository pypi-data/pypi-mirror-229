"""
Author: wind windzu1@gmail.com
Date: 2023-08-27 18:34:41
LastEditors: wind windzu1@gmail.com
LastEditTime: 2023-08-28 19:14:33
Description: 
Copyright (c) 2023 by windzu, All Rights Reserved. 
"""

from argparse import ArgumentParser

from .slice import Slice


def parse_args(argv):
    parser = ArgumentParser()
    parser.add_argument("--path", type=str, default="./config.yaml", help="config path")
    return parser.parse_args(argv)


def main(argv):
    args = parse_args(argv)

    # gif generator
    slice = Slice(path=args.path)
    slice.slice()


if __name__ == "__main__":
    main()
