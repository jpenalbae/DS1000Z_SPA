# DS1000Z_SPA

Simple power analysis tool using the Rigol DS1000Z series oscilloscopes or 
loading from CSV files.

It uses SCPI over the network to communicate wirh the scope. It has been tested
with a DS1054Z but it might be portable to other scopes.

## Features

- Export graph data as CSV for later analysis
- Export markers as CSV for extra analysis
- Create markers and add notes on them
- Select a range and cut it from the graph
- Load data from DS1000Z series oscilloscopes over the network
- Load saved data from CSV files
- Enable and disable scope channels

## Usage

```
$ ./ds1000z_spa.py  -h
Usage: python3 ds1000z_spa.py <scope address>
```

The following controls can be used to interact with the graph:

- Click to add marker
- Click + drag over a marker to move it
- Ctrl+Click to remove marker
- Double click on the markers table to go to the marker
- Rigth click on the graph to export and change graph properties


## Icons

Icons used in this project are from fontawesome.com and are licensed under the
Creative Commons Attribution 4.0 International license.

https://creativecommons.org/licenses/by/4.0/
