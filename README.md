# qBittorrent Ratio Manager
Reads .qman files for JSON settings on when and how to delete torrents from a qBittorrent client


This program can delete all of your 500 torrents if allowed, so please be careful with the settings. Don't say i didn't warn you :)

## Usage
Just clone the github repo or download it as a zip. Then run:
```
python3 qbit_ratio_manager.py
```
To run it regularily i recommend setting up a cron job or a Windows equivalent

## Prerequisites
Python 3<br>
pip packages: jsonschema, requests
```
pip3 install jsonschema requests
```

## Command line reference
|Argument         |Explanation|
|---              |:-:|
|--url            |The url to the qBittorrent api. Ends in /api/v2/ unless you have a reverse proxy or similar.<br> (you probably know if it's different for you)|
|--username       |The username for the qBittorrent WebUI login|
|--password       |The password for the qBittorrent WebUI login|
|--config_folder  |Path to where the .qman files are stored. By default this is: (folder of the script)/config/|

## .qman config file explanation
The config files are in JSON and the file extensions have to be .qman


For every category / category+tracker configuration you create a new .qman file and fill in the settings for that specific category / category+tracker.



Multiple .qman files for the same category is allowed but should only be used in conjunction with the "tracker" setting


.qman example:
```
{
    "category": "test",
    "tracker": "tracker.coppersurfer.tk", # Optional, remove unless needed
    "public": {
        "min_seed_ratio": 2,
        "max_seed_ratio": 10000,
        "min_seed_time": 1,
        "max_seed_time": 960
    },
    "private": {
        "min_seed_ratio": 2,
        "max_seed_ratio": 10000,
        "min_seed_time": 480,
        "max_seed_time": 960
    },
    "delete_files": false,
    "custom_delete_files_path": "/home/hundter/downloads" # Optional, remove unless needed
}
```

Line by line explanation:


|Argument|Explanation|
|---|:-:|
|category|The name of the qBittorrent category that this .qman file applies to|
|tracker|Optional. Full tracker hostname, including subdomain if any (see example).<br>Only scans torrents that match both the category and tracker setting|
|public|The settings for public torrents|
|min_seed_ratio|The minimum share ratio to reach before deletion. Only deletes if both minimum settings are satisfied|
|max_seed_ratio|The maximum share ratio to reach before deletion, regardless of minimum settings|
|min_seed_time|The minimum time to seed in hours before deletion. Only deletes if both minimum settings are satisfied. Only use whole numbers!|
|max_seed_time|The maximum time to seed in hours before deletion, regardless of minimum settings. Only use whole numbers!|
|private|The settings for private torrents|
|delete_files|Whether qBittorrent should remove the files after deleting the torrent|
|custom_delete_files_path|Optional. A path to the category download location. Program then uses filesystem deletion directly instead of having qBittorrent delete the files. If the torrent is a folder it removes the folder regardless of any files in it. Overrides "delete_files" (Only use this if you understand what it does, you most likely don't need it)|
