# TMX Tiled Map Library for Butano

This is a [Tiled](https://www.mapeditor.org/) file map converter for Butano.
It takes `*.tmx` files and makes their graphics, objects and tiles easily
accessible from Butano.

## Maintainership Warning

This is an extremely low priority project for me and I have tons of much more
important things to do, so I may not reply at all.
In such case, feel free to fork the project.

## Setup

In your makefile create:
- the `MAPS` variable listing the `maps` directory

In your makefile:
- add the `$(BUILD)/src` directory to `SOURCES`
- add the `$(BUILD)/include` directory to `INCLUDES`
- include the `bntmx.mak` file after including Butano's `butano.mak`

Then, if you don't have an external tool defined in `EXTTOOL` in your makefile,
add `@$(PYTHON) -B bntmx.py --target=butano --build=$(BUILD) $(MAPS)` to
`EXTTOOL`.
If you already have a Python external tool, add this to it:
```python
import bntmx
bntmx.process("butano", "grit", ["maps"], "build")
```

The Butano target requires Butano 15.6.0 or greater.

## Usage

Given a map named *world*, you should have the following files:
- `maps/world.json`
- `maps/world.tmx`

The script will generate the following files:
- `build/world.bntmx.bmp`
- `build/include/bntmx_map_items_world.h`
- `build/src/bntmx_map_items_world.cpp`

Each map is converted into an object of type `bntmx::map_item` listed in the
`bntmx::map_items` namespace.
In our example, the class `bntmx::map_items::world` is created and can be
accessed via `bntmx_map_items_world.h`.

A map is rebuilt only if only of the files describing it changed, including the
tilesets and their graphics.

## Maps

A map file can contain multiple regular backgrounds, map tiles and map objects.

Multiple regular background layers are allowed by listing them in the `"layers"`
field. Each layer is drawn centered on the smallest possible image that can
contain it and whose sides are multiples of 256 pixels.

An example of the `*.json` files required for maps is the following:

```json
{
}
```

The fields for maps are the following:

- `"regular_bg"`: optional field which specifies the regular backgrounds, see
  the *Regular backgrounds* section below.
- `"map_objects"`: optional field which specifies the map objects, see the
  *Map objects* section below.
- `"map_tiles"`: optional field which specifies the map tiles, see the
  *Map tiles* section below.

### Regular backgrounds

A map file can contain multiple regular backgrounds. Each background can contain
up to 1024 tiles. The size of a small regular background (which are faster) must
be 256x256, 256x512, 512x256 or 512x512 pixels. Big regular backgrounds are
slower CPU wise, but can have any width or height multiple of 256 pixels.

Multiple regular background layers are allowed by listing them in the `"layers"`
field. Each background layer is drawn centered on the smallest possible image
that can contain it.

An example of the `*.json` files required for map regular backgrounds is the
following:

```json
{
    "regular_bg": {
        "layers": [
            []
        ]
    }
}
```

The fields for regular backgrounds are the following:

- `"layers"`: the list of tile layers to render as regular backgrounds. Layers
  must be referred to by their absolute path, separating layer groups from their
  children with `/`. For each regular background, you can use a tile layer or a
  list of tile layers, in which case each layer will be drawn on top of the
  previous one as a single background image.

If the conversion process has finished successfully, a
[bn::regular_bg_item](https://gvaliente.github.io/butano/classbn_1_1regular__bg__item.html)
should have been generated in the `build` folder.

For example, from two files named `world.tmx` and `world.json`, a header file
named `bntmx_map_items_world.h` is generated in the `build` folder.

You can use this header to create a regular background with only one line of
C++ code:

```c++
#include "bntmx_map_items_world.h"

bn::regular_bg_ptr regular_bg = bntmx::map_items::world_regular_bg.create_bg(0, 0);
```

### Map objects

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

### Map tiles

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
