import requests
import sys


class QBitController:
    qbit_url = ""  # Default qbit API url
    qbit_session = requests.Session()

    @staticmethod
    def get(request):
        return QBitController.qbit_session.get(QBitController.qbit_url + request)

    @staticmethod
    def connect_to_qbit(qbit_url, username, password):
        QBitController.qbit_url = qbit_url

        try:
            if username and password:
                r = QBitController.qbit_session.post(QBitController.qbit_url + "auth/login", data = {'username':username, 'password':password})
                
                if r.status_code == 403:
                    print("Your qbittorrent has banned your IP for too many login attempts. Restart qbittorrent to fix this")
                    sys.exit(1)

                if "SID" not in QBitController.qbit_session.cookies.get_dict().keys():
                    raise requests.exceptions.HTTPError
            else:
                r = QBitController.get("app/version")
                if r.status_code != 200:
                    raise requests.exceptions.HTTPError
        except requests.exceptions.HTTPError:
            print("Couldn't authenticate with qBittorrent, verify your username and password")
            sys.exit(1)
        except requests.exceptions.RequestException as err:
            print(err)
            sys.exit(1)


    @staticmethod
    def get_torrent_properties(torrent_hash):
        return QBitController.get("torrents/properties?hash=" + torrent_hash).json()

    @staticmethod
    def get_torrent_trackers(torrent_hash):
        return QBitController.get("torrents/trackers?hash=" + torrent_hash).json()

    @staticmethod
    def remove_torrent_hashes(torrent_hashes, delete_files):
        delete_files_string = "false"
        if delete_files:
            delete_files_string = "true"
        hashes_to_delete_string = '|'.join(torrent_hashes)
        QBitController.get("torrents/delete?hashes=" + hashes_to_delete_string + "&deleteFiles=" + delete_files_string)

    @staticmethod
    def get_torrents_by_category(category):
        return QBitController.get("torrents/info?category=" + category).json()
