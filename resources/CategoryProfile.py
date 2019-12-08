import os
import shutil
from resources.QBitController import QBitController
import resources.Helper as Helper


class CategoryProfile:

    def __init__(self, category, tracker, delete_files, custom_delete_files_path, public_settings_array, private_settings_array):
        self.category = category
        self.tracker = tracker
        self.delete_files = delete_files
        self.custom_delete_files_path = custom_delete_files_path
        self.public = public_settings_array
        self.private = private_settings_array
        self.torrents_to_delete = {}
        self.torrents_checked = set()

    def delete_files_directly(self):
        for torrent_path in self.torrents_to_delete.values():
            full_path = self.custom_delete_files_path + "/" + torrent_path
            if os.path.isfile(full_path):
                os.remove(full_path)
            elif os.path.isdir(full_path):
                shutil.rmtree(full_path)
            else:
                print("Could not find path or file: " + full_path)

    def should_torrent_be_deleted(self, torrent_hash):
        torrent_properties = QBitController.get_torrent_properties(torrent_hash)
        torrent_seeding_time_in_hours = (torrent_properties['seeding_time'] / 60 / 60)
        torrent_trackers  = QBitController.get_torrent_trackers(torrent_hash)

        if self.tracker and Helper.does_torrent_contain_tracker(torrent_trackers, self.tracker) == False:
            return False

        limit_array = self.private if Helper.is_torrent_private(torrent_trackers) else self.public

        if (torrent_properties['share_ratio'] >= limit_array['max_seed_ratio']) or (torrent_seeding_time_in_hours >= limit_array["max_seed_time"]):
            return True

        if (torrent_properties['share_ratio'] >= limit_array['min_seed_ratio']) and (torrent_seeding_time_in_hours >= limit_array["min_seed_time"]):
            return True

        return False

    def process_category(self):
        torrents = QBitController.get_torrents_by_category(self.category)
        if not torrents:
            return

        for torrent in torrents:
            self.torrents_checked.add(torrent['hash'])

            if torrent['progress'] != 1:  # Ignore if download is not finished
                continue

            if self.should_torrent_be_deleted(torrent['hash']):
                self.torrents_to_delete[torrent['hash']] = torrent['name']

        if self.torrents_to_delete:
            QBitController.remove_torrent_hashes(self.torrents_to_delete.keys(), self.delete_files)

            if self.custom_delete_files_path:
                self.delete_files_directly()
