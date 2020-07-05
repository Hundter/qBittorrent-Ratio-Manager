#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import argparse
import os
import json
import logging
from jsonschema import validate
from jsonschema import ValidationError
from resources.CategoryProfile import CategoryProfile
from resources.QBitController import QBitController


qman_schema = {
    "type" : "object",
    "properties" : {
        "category" : {"type" : "string"},
        "public" : {
            "type" : "object",
            "properties" : {
                "min_seed_ratio": {"type" : "number"},
                "max_seed_ratio": {"type" : "number"},
                "min_seed_time": {"type" : "integer"},
                "max_seed_time": {"type" : "integer"},
                "required_seeders" : {"type" : "integer"}
            },
            "required": ["min_seed_ratio", "max_seed_ratio", "min_seed_time", "max_seed_time"]
        },
        "private" : {
            "type" : "object",
            "properties" : {
                "min_seed_ratio": {"type" : "number"},
                "max_seed_ratio": {"type" : "number"},
                "min_seed_time": {"type" : "integer"},
                "max_seed_time": {"type" : "integer"},
                "required_seeders" : {"type" : "integer"}
            },
            "required": ["min_seed_ratio", "max_seed_ratio", "min_seed_time", "max_seed_time"]
        },
        "tracker" : {"type" : "string"},
        "delete_files" : {"type" : "boolean"},
        "custom_delete_files_path" : {"type" : "string"}
    },
    "required": ["category", "public", "private", "delete_files"]
}


def load_category_files_into_classes(args):
    categoryProfiles = {}

    for file in os.listdir(args.config_folder):
        if not file.endswith(".qman"):
            continue

        with open(args.config_folder + "/" + file) as json_file:
            settings = json.load(json_file)

        try:
            validate(instance=settings, schema=qman_schema)
        except ValidationError as e:
            print("Failed to load '" + file + "'...\n*** " + e.message + " ***\n.qman example files can be found here: aaa")
            sys.exit(1)

        # Set default values
        if 'tracker' not in settings: settings['tracker'] = ""
        if 'custom_delete_files_path' not in settings: settings['custom_delete_files_path'] = ""
        if 'required_seeders' not in settings['public']: settings['public']['required_seeders'] = -1
        if 'required_seeders' not in settings['private']: settings['private']['required_seeders'] = -1

        # Verify path availability
        if settings['custom_delete_files_path']:
            if not os.path.isdir(settings['custom_delete_files_path']):
                print("Error while parsing '" + file + "'. custom_delete_files_path: specified path is not a valid directory")
                sys.exit(1)
            settings['delete_files'] = False # Override delete_files if custom_delete_files_path is set

        categoryProfile = CategoryProfile(settings['category'], settings['tracker'], settings['delete_files'], settings['custom_delete_files_path'], settings['public'], settings['private'])
        categoryProfiles[settings['category']] = categoryProfile

    return categoryProfiles


def construct_argument_parser():
    parser = argparse.ArgumentParser(description='https://github.com/Hundter/qBittorrent-Ratio-Manager Reads .qman files for JSON settings on when and how to delete torrents from a qBittorrent client', usage="%(prog)s [options]", formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('--url', default="http://127.0.0.1:8080/api/v2/", dest="qbit_url", metavar='',
                    help='Set the qbit API url and path, most likely ends in /api/v2/')

    parser.add_argument('--username', default="", dest="qbit_username", metavar='',
                    help='Set the qbit username')

    parser.add_argument('--password', default="", dest="qbit_password", metavar='',
                    help='Set the qbit password')

    parser.add_argument('--config_folder', default=os.path.dirname(os.path.realpath(__file__)) + "/configs/", metavar='',
                    help='Set the folder for category config files.')

    parser.add_argument('--verbose', '-v', default=0, dest="verbose", help='Set the verbosity level. 0 = only warnings, 1 = info, 2 = debug.', action='count')

    return parser.parse_args()

if __name__ == "__main__":
    args = construct_argument_parser()

    if not args.qbit_url.startswith("http://") and not args.qbit_url.startswith("https://"):
        args.qbit_url = "http://" + args.qbit_url

    levels = [logging.WARNING, logging.INFO, logging.DEBUG]
    level = levels[min(2, args.verbose)]
    logging.basicConfig(level=level)

    QBitController.connect_to_qbit(args.qbit_url, args.qbit_username, args.qbit_password)

    categoryProfiles = load_category_files_into_classes(args)

    torrents = QBitController.get_torrents()

    delete_counter = 0
    torrents_checked = set()
    for torrent in torrents:
        if torrent["category"] in categoryProfiles.keys():
            categoryProfiles[torrent["category"]].process_torrent(torrent)
            torrents_checked.add(torrent['hash'])
        elif "*" in categoryProfiles.keys():
            categoryProfiles["*"].process_torrent(torrent)
            torrents_checked.add(torrent['hash'])

    for categoryProfile in categoryProfiles.values():
        categoryProfile.delete_torrents_to_be_deleted()
        delete_counter += len(categoryProfile.torrents_to_delete)

    print("Checked " + str(len(torrents_checked)) + " torrents!")
    print("Deleted " + str(delete_counter) + " torrents!")
