from typing import Generator
import os
import argparse
import logging
import re

FILE_ENDINGS = [".h", ".c"]
SPECIAL_KEYS = ["autosar", "sip"]


def test_extract_conf_pair():
    s1 = "env.SetConfig(cpufamily='aurix')"
    s2 = "env.SetConfig(appStartAddr=0xA0020000)"
    s3 = "env.SetConfig(useEth=False)"

    k, v = extract_conf_pair(s1)
    assert k == "cpufamily"
    assert v == "aurix"
    k, v = extract_conf_pair(s2)
    assert k == "appStartAddr"
    assert v == 0xA0020000
    k, v = extract_conf_pair(s3)
    assert k == "useEth"
    assert v is False


def extract_conf_pair(line: str):
    regex = r".*SetConfig\(([^=]+)=([^)]+)\).*"
    match = re.match(regex, line)
    if match:
        return match.group(1), eval(match.group(2))
    else:
        return None


def parse_config(scons_file: str) -> dict:
    result = {}

    with open(scons_file) as f:
        for line in f:
            pair = extract_conf_pair(line)
            if pair:
                result[pair[0]] = pair[1]

    return result


def keep_configured(root, dirs, conf):
    if os.path.basename(os.path.dirname(root)) == "config":

        k = os.path.basename(root)
        try:
            v = conf[k]
        except KeyError:
            pass
        else:
            remove_all_but(dirs, v)


def remove_all_but(dirs, to_keep):
    for_removal = [x for x in dirs if x != to_keep]
    for remove_candidate in for_removal:
        dirs.remove(remove_candidate)


def keep_configured_special(dirs, conf):
    for key in SPECIAL_KEYS:
        v = conf[key]
        if v in dirs:
            remove_all_but(dirs, v)


def remove_unimportant(dirs):
    if "Metadata" in dirs:
        dirs.remove("Metadata")
    if "test" in dirs:
        dirs.remove("test")


def source_files(source_folder: str, conf: dict) -> Generator[str, None, None]:
    for root, dirs, files in os.walk(source_folder):
        remove_unimportant(dirs)
        keep_configured_special(dirs, conf)
        keep_configured(root, dirs, conf)
        for file_name in files:
            for ending in FILE_ENDINGS:
                if file_name.endswith(ending):

                    yield os.path.join(root, file_name).replace("/", "\\")


def main():
    parser = argparse.ArgumentParser(description="Desc.")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("scons_file", help="The consfile to parse config from.")
    parser.add_argument("source_folder", nargs="+", help="Source folders to search.")

    args = parser.parse_args()
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    logging.debug(args)
    conf = parse_config(args.scons_file)
    logging.debug(conf)
    for source_folder in args.source_folder:
        for path in source_files(source_folder, conf):
            print(path)


if __name__ == "__main__":
    main()
