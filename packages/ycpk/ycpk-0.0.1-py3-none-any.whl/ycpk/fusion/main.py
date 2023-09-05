"""
Author: wind windzu1@gmail.com
Date: 2023-09-01 14:25:23
LastEditors: wind windzu1@gmail.com
LastEditTime: 2023-09-01 14:44:40
Description: fusion main function
Copyright (c) 2023 by windzu, All Rights Reserved. 
"""

from argparse import ArgumentParser

from .fusion import Fusion


def parse_args(argv):
    parser = ArgumentParser()
    parser.add_argument("--path", type=str, default="./config.yaml", help="config path")
    return parser.parse_args(argv)


def main(argv):
    args = parse_args(argv)

    # gif generator
    fusion = Fusion(path=args.path)
    fusion.fusion()


if __name__ == "__main__":
    main()
