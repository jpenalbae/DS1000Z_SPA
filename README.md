# DS1000Z_SPA

Simple power analysis tool using the Rigol DS1000Z series oscilloscopes or 
loading from CSV files.

It uses SCPI over the network to communicate wirh the scope. It has been tested
with a DS1054Z but it might be portable to other scopes.

![spa](https://github.com/jpenalbae/DS1000Z_SPA/assets/8380459/b5a18bc7-d459-42cd-846d-4e3ba7530d8f)


## Features

- Export graph data as CSV for later analysis
- Export markers as CSV for extra analysis
- Create markers and add notes on them
- Select a range and cut it from the graph
- Load data from DS1000Z series oscilloscopes over the network
- Load saved data from CSV files
- Enable and disable scope channels
- Support to store multiple captures and change between them

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

To cut a capture region:
1. Push the select a range button
2. Drag the selection start and end points
3. Push the cut selected range button

You can handle multiple captures at the same time by pressing the download or
open button multiple times and switching between them with the combo box. If
you need to compare two captures at the same time you can open multiple
instances of the program.


## Icons

Icons used in this project are from fontawesome.com and are licensed under the
Creative Commons Attribution 4.0 International license.

https://creativecommons.org/licenses/by/4.0/
