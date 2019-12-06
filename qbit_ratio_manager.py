#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import argparse
import os
import json
from resources.CategoryProfile import CategoryProfile
from resources.QBitController import QBitController


def load_category_files_into_classes(args):
    categoryProfiles = []

    for file in os.listdir(args.config_folder):
        if not file.endswith(".qman"):
            continue

        with open(args.config_folder + "/" + file) as json_file:
            settings = json.load(json_file)

        if 'category' not in settings:
            continue

        category = settings['category']
        tracker = settings['tracker'] if 'tracker' in settings else ""

        settings_public = settings['public'] if 'public' in settings else {}
        public = {}
        public['min_seed_ratio'] = settings_public['min_ratio_public'] if 'min_ratio_public' in settings_public else args.min_ratio_public_global
        public['max_seed_ratio'] = settings_public['max_ratio_public'] if 'max_ratio_public' in settings_public else args.max_ratio_public_global
        public['min_seed_time'] = settings_public['min_seed_time'] if 'min_seed_time' in settings_public else args.min_seed_time_public_global
        public['max_seed_time'] = settings_public['max_seed_time'] if 'max_seed_time' in settings_public else args.max_seed_time_public_global

        settings_private = settings['private'] if 'private' in settings else {}
        private = {}
        private['min_seed_ratio'] = settings_private['min_ratio_public'] if 'min_ratio_public' in settings_private else args.min_ratio_private_global
        private['max_seed_ratio'] = settings_private['max_ratio_public'] if 'max_ratio_public' in settings_private else args.max_ratio_private_global
        private['min_seed_time'] = settings_private['min_seed_time'] if 'min_seed_time' in settings_private else args.min_seed_time_private_global
        private['max_seed_time'] = settings_private['max_seed_time'] if 'max_seed_time' in settings_private else args.max_seed_time_private_global

        categoryProfile = CategoryProfile(category, tracker, args.delete_files, public, private)

        categoryProfiles.append(categoryProfile)

    return categoryProfiles


def construct_argument_parser():
    parser = argparse.ArgumentParser(description='https://github.com/Hundter/qBittorrent-Ratio-Manager Reads .qman files for JSON settings on when to delete torrents from a qBittorrent client (Global default settings do not overwrite settings in files!)', usage="%(prog)s [options]", formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('--delete_files',
                    help='Delete files when removing them from qBittorrent', action='store_true')

    parser.add_argument('--min_ratio_public_global', default=2, metavar='',
                    help='Set the global default minimum ratio for public torrents.')

    parser.add_argument('--max_ratio_public_global', default=10000, metavar='',
                    help='Set the global default maximum ratio for public torrents.')

    parser.add_argument('--min_seed_time_public_global', default=1, metavar='',
                    help='Set the global default minimum seed time in hours for public torrents.')

    parser.add_argument('--max_seed_time_public_global', default=960, metavar='',
                    help='Set the global default maximum seed time in hours for public torrents.')

    parser.add_argument('--min_ratio_private_global', default=2, metavar='',
                    help='Set the global default minimum ratio for private torrents.')

    parser.add_argument('--max_ratio_private_global', default=10000, metavar='',
                    help='Set the global default maximum ratio for private torrents.')

    parser.add_argument('--min_seed_time_private_global', default=480, metavar='',
                    help='Set the global default minimum seed time in hours for private torrents.')

    parser.add_argument('--max_seed_time_private_global', default=960, metavar='',
                    help='Set the global default maximum seed time in hours for private torrents.')

    parser.add_argument('--url', default="http://127.0.0.1:8080/api/v2/", dest="qbit_url", metavar='',
                    help='Set the qbit API url and path, most likely ends in /api/v2/')

    parser.add_argument('--username', default="", dest="qbit_username", metavar='',
                    help='Set the qbit username')

    parser.add_argument('--password', default="", dest="qbit_password", metavar='',
                    help='Set the qbit password')

    parser.add_argument('--config_folder', default=os.path.dirname(os.path.realpath(__file__)) + "/configs/", metavar='',
                    help='Set the folder for category config files.')

    return parser.parse_args()

if __name__ == "__main__":
    args = construct_argument_parser()

    if not args.qbit_url.startswith("http://") and not args.qbit_url.startswith("https://"):
        args.qbit_url = "http://" + args.qbit_url

    QBitController.connect_to_qbit(args.qbit_url, args.qbit_username, args.qbit_password)

    categoryProfiles = load_category_files_into_classes(args)

    delete_counter = 0
    torrents_checked = set()
    for categoryProfile in categoryProfiles:
        categoryProfile.process_category()
        delete_counter += len(categoryProfile.torrent_hashes_to_delete)
        torrents_checked = torrents_checked.union(categoryProfile.torrents_checked)

    print("Checked " + str(len(torrents_checked)) + " torrents!")
    print("Deleted " + str(delete_counter) + " torrents!")
