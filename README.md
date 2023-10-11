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
- the `$(BUILD)/include` directory to `INCLUDES`
- the `$(BUILD)/graphics` directory to `GRAPHICS`

Then, if you don't have an external tool defined in `EXTTOOL` in your makefile,
add `@$(PYTHON) -B bntmx.py --target=butano --build=$(BUILD) $(MAPS)` to
`EXTTOOL`.
If you already have a Python external tool, add this to it:
```python
import bntmx
bntmx.process("butano", ["maps"], "build")
```

The Butano target requires Butano 15.6.0 or greater.

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
- `"graphics"`: the paths to the layers to draw as a `bn::regular_bg_item`
- `"objects"`: the paths to the layers whose objects should be exported
- `"tiles"`: the paths to the layers whose tiles should be exported

The paths to layers are the names of the groups and layers from the *.tmx file
joined with the / separator.
You can access the layer "mylayer" in the group "mygroup" by writing a path with
the / separator like this : "mygroup/mylayer".

The layers they will be exported and indexed in the order they are listed.

Layers also be an array of layers that will be merged together to give you more
freedom in your file:
- graphics layers from an array will be drawn one onto the other to form a
  single layer
- objects layers from an array will have all their objects exported into a
  single layer
- tiles layers from an array will be merged one onto the other to form a
  single layer

Here is an example of what a *.json decriptor could look like:
```json
{
    "graphics": [
        "canopy",
        [
            "floor",
            "walls"
        ]
    ],
    "objects": [
        [],
        [
            "doors",
            "enemies",
            "npcs",
            "teleporters"
        ],
    ],
    "tiles": [
        "wall_collisions",
        "ground_collisions"
    ]
}
```

## Graphics

Each graphics layer is drawn centered on the smallest possible image whose width
and height are multiples of 256 and that can contain it.
These images are compiled into a single image and converted into a single
`bn::regular_bg_item` containing them all and named like your map.

You can access the graphics via `bntmx::map::regular_bg_item()` or like any
other bundled `bn::regular_bg_item` asset.

## Objects

Each objects layer is exported as lists of objects of type `bntmx::map_object`,
a list of object IDs and a list of object classes.
Objects have an unique ID and a position.
Object IDs are integers in the [0..65535] range, so you can have up to 65536
different objects in a map, which should be more than enough.

The names and classes of the objects are exported as IDs in `enum object_id` and
`enum object_class` found in the namespace of the generated map class.
Objects of each class as well as classless objects are stored separately from
each other for each layer.
Please use valid C++ enumeration value names for your object names and classes.

The ID of an object isn't the one defined in the map file, so you have to name
an object to refer to it.
The position of an object isn't the one defined in the map file but its center.

You can access the objects via `bntmx::map::objects()`.

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

## Name Mangling

To ensure compatibility with C and C++, map file names, tileset file names,
object names and object class names are mangled.
Name mangling can lead to collisions as two originaly different names can lead
to the same mangled name, please be sure to use different-enough names to avoid
that.

Names are mangled in the following way:
- leading characters that aren't ASCII letters are trimmed
- trailing characters that aren't ASCII letters or digits are trimmed
- sequences of characters that aren't ASCII letters or digits are replaced by a single underscore character
- names are lowercase in namespace names, type names, and function names
- names are uppercase in enumeration values, and inclusion guards

## To Do

Split the objects in 256x256 chunks to allow saving some collision detections.

Rename the script and maybe move it to a directory, if deemed relevant.
Maybe it should be `__init__.py`?

Find free graphics (tileset, objects) and build a map with them.

Maybe split the tile arrays in chunks, compress the chunks and decompress only a
few chunks  at a time in RAM. Or keep them

Allow parametrizing the BG and its type.

Maybe allow getting the layer (and class?) for a given object ID? And position
apart too.

Change ID to name where relevant
