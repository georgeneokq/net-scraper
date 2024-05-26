import argparse


def file_path_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("file_path", type=str)
    args = parser.parse_args()

    return {"file_path": args.file_path}
