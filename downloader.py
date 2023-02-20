from qbittorrent import Client
import csv
import time

with open("magnet.csv", 'r') as file:
  csvreader = csv.reader(file)
  magnet_links = [row[0] for row in csvreader]

# print(magnet_links)

# connect to the qbittorent Web UI
qb = Client("http://127.0.0.1:8080/")

# put the credentials (as you configured)
qb.login("admin", "adminadmin")

# start downloading
# this magnet is not valid, replace with yours
for magnet_link in magnet_links:
	qb.download_from_link(magnet_link, savepath="I:\\Scrapedownload")
# you can specify the save path for downloads
# qb.download_from_file(torrent_file, savepath="/the/path/you/want/to/save")

# pause all downloads
qb.pause_all()

# resume them
qb.resume_all()

time.sleep(2)

def get_size_format(b, factor=1024, suffix="B"):
    """
    Scale bytes to its proper byte format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    """
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if b < factor:
            return f"{b:.2f}{unit}{suffix}"
        b /= factor
    return f"{b:.2f}Y{suffix}"

# return list of torrents
torrents = qb.torrents()

for torrent in torrents:
    print("Torrent name:", torrent["name"])
    print("hash:", torrent["hash"])
    print("Seeds:", torrent["num_seeds"])
    print("File size:", get_size_format(torrent["total_size"]))
    print("Download speed:", get_size_format(torrent["dlspeed"]) + "/s")

# Torrent name: debian-10.2.0-amd64-netinst.iso
# hash: 86d4c80024a469be4c50bc5a102cf71780310074
# Seeds: 70
# File size: 335.00MB
# Download speed: 606.15KB/s