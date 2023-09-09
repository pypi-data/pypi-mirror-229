
# Core Python imports.
import os
import sys

# Modify path so we can include the version of cruntils in this directory
# instead of relying on the user having it installed.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import our package.
import cruntils


# Define a list of trig pillar locations.
trig_pillar_locations_list = [
    { "name": "Outwood",        "grid_ref": "TQ 33246 45539", "wgs84_latlon": ["51 11 36.76 N", "000 05 40.22 W"]},
    { "name": "Chat Hill Farm", "grid_ref": "TQ 37978 48283" },
    { "name": "Gaywood Farm",   "grid_ref": "TQ 43190 48740" },
    { "name": "Mountjoy Farm",  "grid_ref": "TQ 51279 47834" },
    { "name": "Dry Hill",       "grid_ref": "TQ 43200 41606" },
    { "name": "Markbeech",      "grid_ref": "TQ 47758 42534" },
    { "name": "Smarts Hill",    "grid_ref": "TQ 51345 42253" },
    { "name": "Great Bounds",   "grid_ref": "TQ 57293 43566" },
    { "name": "Salehurst",      "grid_ref": "TQ 48431 39143" },
    { "name": "Cherry Garden",  "grid_ref": "TQ 51101 35644" },
    { "name": "Hindleap",       "grid_ref": "TQ 40354 32381" },
    { "name": "Gills Lap",      "grid_ref": "TQ 46859 31965" },
    { "name": "Crowborough",    "grid_ref": "TQ 51169 30761" }
]

# Need to do maths for grid to lat lon!









