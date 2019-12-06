from urllib.parse import urlparse

def is_torrent_private(torrent_trackers):
    # Check msg in DHT tracker. For now this is the only
    # indicator of whether the torrent is "private" or not
    if torrent_trackers[0]['msg'] == "This torrent is private":
        return True
    else:
        return False


def does_torrent_contain_tracker(torrent_trackers, tracker_to_match):
    tracker_hostnames = []

    for tracker  in torrent_trackers:
        urlparsed = urlparse(tracker['url'])
        if urlparsed.hostname:
            tracker_hostnames.append(urlparsed.hostname)

    if tracker_to_match in tracker_hostnames:
        return True
    else:
        return False