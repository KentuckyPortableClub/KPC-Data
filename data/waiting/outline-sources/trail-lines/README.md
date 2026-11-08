# Wired trail-line extracts (Nov 7 2026)

Small official line extracts for file-based wires in `trail-lines-wired-nov7.csv` (`file:` rows). Sources: USGS National
Transportation Dataset state GeoPackages (public domain), the Forest Service Wild and Scenic River / National Forest System
Trails official downloads already on disk, and municipal/ArDOT GeoJSON Research had already fetched. The weekly national
trail bot cannot query those files, so `kpc_wired_trails.py --install-files` copies them into `data/trails/` after the bot
rewrites `index.json`. Never commit the big state packages or the 12 GB national file here.
