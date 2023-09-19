#!/bin/python

import argparse
import mapbuilder

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Compile source data into code and data usable by the game engine.')
    parser.add_argument('--build', required=True, help='build folder path')
    args = parser.parse_args()
    mapbuilder.process(args.build)
