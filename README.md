# picture-maps (KPC-Data orphan branch)
House rule (Brandon Oct 29 11:10 PM): official PICTURE maps (PDF / brochure / image, no coordinates) for parks with no GIS outline,
saved small for future bot-drawn maps. Never on main, never in KPC-Links.
- `maps/<park number>_<short-name>.jpg`: the boundary page only, JPEG, 2000 px long side, quality ~70, 3 MB at most.
- `rows/<same>.json`: one row per map (ref, name, agency, source URL, page, date, chat); `index.json` = all rows (rebuilt by the bot).
- How a map gets here: a chat files a look-up request kind `save-map` on the `lookup` branch:
  `{"chat": 3, "kind": "save-map", "ref": "US-9652", "name": "Grenada State Wildlife Area", "agency": "CPW", "url": "<PDF, picture, or the park page that links it>", "pages": 1, "hint": "granada"}`
- Deleted every Sunday once the park has an OFFICIAL outline in the key (kpc-lookup-tidy.yml on main). HQ squashes the branch past 300 MB.
- Nothing is traced from these pictures (G-ID3; R-G9 decides later).
