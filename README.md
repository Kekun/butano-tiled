# TMX Tiled Map Library for Butano

This is a Tiled file map converter for Butano.
It takes *.tmx files and makes their graphics, objects and tiles easily
accessible from Butano.

## Maintainership Warning

This is an extremely low priority project for me and I have tons of much more
important things to do, so I may not reply at all.
In such case, feel free to fork the project.

## Setup

In your makefile create:
- the `MAPS` variable listing the `maps` directory

In your makefile add:
- the `$(BUILD)/src` directory to `SOURCES`
- the `$(BUILD)/include` and `bntmx/include` directories to `INCLUDES`
- the `$(BUILD)/graphics` directory to `GRAPHICS`

Then, if you don't have an external tool defined in `EXTTOOL` in your makefile,
add `@$(PYTHON) -B bntmx.py --build=$(BUILD) $(MAPS)` to `EXTTOOL`.
If you already have a Python external tool, add this to it:
```python
import bntmx
bntmx.process(["maps"], "build")
```

## Usage

Given a map named *mymap*, you should have the following files:
- `maps/mymap.json`
- `maps/mymap.tmx`

The script will generate the following files:
- `build/graphics/mymap.bmp`
- `build/graphics/mymap.json`
- `build/include/bntmx_maps_mymap.h`
- `build/src/bntmx_maps_mymap.cpp`

Each map is converted into an implementation of the abstract class `bntmx::map`
listed in the `bntmx::maps` namespace.
In our example, the class `bntmx::maps::mymap` is created and can be accessed
via `bntmx_maps_mymap.h`.

A map is rebuilt only if only of the files describing it changed, including the
tilesets and their graphics.

## Maps

Maps are *.tmx files you can build with [Tiled](https://www.mapeditor.org/).

Each map must have a *.json descriptor whose root object expects the following
fields:
- `"graphics"`: the names of the layers to draw as a `bn::regular_bg_item`
- `"objects"`: the names of the layers whose objects should be exported
- `"tiles"`: the names of the layers whose tiles should be exported

The names of the layers are the ones from the *.tmx file, they will be exported
and indexed in the order they are listed.

You can access the layer "mylayer" in the group "mygroup" by writing a path with
the / separator like this : "mygroup/mylayer".

## Graphics

Each graphics layer is drawn centered on the smallest possible image whose width
and height are multiples of 256 and that can contain it.
These images are compiled into a single image and converted into a single
`bn::regular_bg_item` containing them all and named like your map.

You can access the graphics via `bntmx::map::regular_bg_item()` or like any
other bundled `bn::regular_bg_item` asset.

## Objects

## Tiles

Each tiles layer is exported as a list of tile IDs of type `bntmx::map_tile`
ordered from left to right and from top to bottom.
Tile IDs are integers in the [0..65535] range, so you can have up to 65536
different tiles in a map, which should be more than enough.

The bounds of each tileset is exported as IDs in `enum tile_id` found in the
namespace of the generated map class.
Tiles in tilesets are indexed from left to right and from top to bottom.

Given a tileset named "mytileset", the ID of its first tile is `MYTILESET`, and
the ID of its last tile is `MYTILESET_LAST`, the tileset contains
`MYTILESET_LAST + 1 - MYTILESET` tiles, and the 3rd tile in the set is
`MYTILESET + 2`.

You can access the tiles via `bntmx::map::tiles()`.

## To Do

Draw multiple layers as one, e.g. a `"village"` layer could be replaced by the
`["ground","buildings"]` list of layers drawn one over the other.

Split the objects in 256x256 chunks to allow saving some collision detections.

How to handle the classes of objects? With a separate set accessible e.g. via a
"class" enum parameter? What to do with unnamed objects? And with duplicated
objects? E.g. `objects_layer(int objects_layer_index)`

Rename the script and maybe move it to a directory, if deemed relevant.

Find free graphics (tileset, objects) and build a map with them.

Directly store the object spans.

Maybe split the tile arrays in chunks, compress the chunks and decompress only a
few chunks  at a time in RAM. Or keep them

Allow parametrizing the BG and its type.
