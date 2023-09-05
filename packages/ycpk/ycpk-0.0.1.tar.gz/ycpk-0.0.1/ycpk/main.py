"""
Author: wind windzu1@gmail.com
Date: 2023-09-01 14:25:23
LastEditors: wind windzu1@gmail.com
LastEditTime: 2023-09-01 14:41:19
Description: 
Copyright (c) 2023 by windzu, All Rights Reserved. 
"""
import sys
from argparse import ArgumentParser


def parse_args():
    parser = ArgumentParser(description="yun chuang perception kit.")
    parser.add_argument("function", type=str, help="function name want to use")
    parser.add_argument("--version", action="version", version="%(prog)s 0.0.1")
    args, _ = parser.parse_known_args()
    return args


def main():
    args = parse_args()
    if (
        args.function == "s"
        or args.function == "slice"
        or args.function == "data_slice"
        or args.function == "data-slice"
    ):
        from ycpk import slice

        slice.main(args)
    elif (
        args.function == "cc"
        or args.function == "calib-camera"
        or args.function == "calib_camera"
    ):
        from ycpk import calib_camera

        calib_camera.main(sys.argv[2:])
    elif args.function == "fusion" or args.function == "gif_generator":
        from ycpk import fusion

        fusion.main(sys.argv[2:])
    elif args.function == "gif" or args.function == "gif_generator":
        from ycpk import gif_generator

        gif_generator.main(sys.argv[2:])
    elif args.function == "v2c" or args.function == "voc2coco":
        from ycpk import voc2coco

        voc2coco.main(sys.argv[2:])
    else:
        print("function name error")
    return 0
