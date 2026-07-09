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
- `"palette_item"`: optional field which specifies the name of the
  [bn::bg_palette_item](https://gvaliente.github.io/butano/classbn_1_1bg__palette__item.html)
  to use for this background.
- `"bpp_mode"`: optional field which specifies the bits per pixel of the regular
  background. This field is required if an external
  [bn::bg_palette_item](https://gvaliente.github.io/butano/classbn_1_1bg__palette__item.html)
  is referenced with `"palette_item"`:
  - `"bpp_8"`: up to 256 colors.
  - `"bpp_4_auto"`: up to 16 colors per
    [tile](https://gvaliente.github.io/butano/group__tile.html). Butano tries to
    quantize the image to fit the color palette into the required one. It is not
    supported if an external
    [bn::bg_palette_item](https://gvaliente.github.io/butano/classbn_1_1bg__palette__item.html)
    is referenced with `"palette_item"`.
  - `"bpp_4_manual"`: up to 16 colors per
    [tile](https://gvaliente.github.io/butano/group__tile.html). Butano expects
    that the image color palette is already valid for this mode.
  - `"bpp_4"`: `"bpp_4_manual"` alias.

The default is `"bpp_4_manual"` for 16 color images and `"bpp_8"` for 256 color
images.

- `"colors_count"`: optional field which specifies the background palette size
  [1..256].
- `"repeated_tiles_reduction"`: optional field which specifies if repeated tiles
  must be reduced or not (`true` by default).
- `"flipped_tiles_reduction"`: optional field which specifies if flipped tiles
  must be reduced or not (`true` by default).
- `"palette_reduction"`: optional field which specifies if repeated 16 color
  palettes must be reduced or not (`true` by default).
- `"big"`: optional boolean field which specifies if maps generated with this
  item are big or not. If this field is omitted, big maps are generated only if
  needed.
- `"tiles_compression"`: optional field which specifies the compression of the
  tiles data:
  - `"none"`: uncompressed data (this is the default option).
  - `"lz77"`: LZ77 compressed data.
  - `"run_length"`: run-length compressed data.
  - `"huffman"`: Huffman compressed data.
  - `"auto"`: uses the option which gives the smallest data size.
  - `"auto_no_huffman"`: uses the option which gives the smallest data size,
    excluding "huffman".
- `"palette_compression"`: optional field which specifies the compression of the
    colors data:
  - `"none"`: uncompressed data (this is the default option).
  - `"lz77"`: LZ77 compressed data.
  - `"run_length"`: run-length compressed data.
  - `"huffman"`: Huffman compressed data.
  - `"auto"`: uses the option which gives the smallest data size.
  - `"auto_no_huffman"`: uses the option which gives the smallest data size,
    excluding "huffman".
- `"map_compression"`: optional field which specifies the compression of the map
  data:
  - `"none"`: uncompressed data (this is the default option).
  - `"lz77"`: LZ77 compressed data.
  - `"run_length"`: run-length compressed data.
  - `"huffman"`: Huffman compressed data.
  - `"auto"`: uses the option which gives the smallest data size.
  - `"auto_no_huffman"`: uses the option which gives the smallest data size,
    excluding "huffman".
- `"compression"`: optional field which specifies the compression of the tiles,
  the colors and the map data:
  - `"none"`: uncompressed data (this is the default option).
  - `"lz77"`: LZ77 compressed data.
  - `"run_length"`: run-length compressed data.
  - `"huffman"`: Huffman compressed data.
  - `"auto"`: uses the option which gives the smallest data size.
  - `"auto_no_huffman"`: uses the option which gives the smallest data size,
    excluding "huffman".

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

### Affine backgrounds

A map file can contain multiple affine backgrounds. Each background can contain
up to 256 tiles. The size of a small affine background (which are faster) must
be 128x128, 256x256, 512x512 or 1024x1024 pixels. Big affine backgrounds are
slower CPU wise, but can have any width or height multiple of 256 pixels.

Multiple affine background layers are allowed by listing them in the `"layers"`
field. Each background layer is drawn centered on the smallest possible image
that can contain it.

An example of the `*.json` files required for affine backgrounds is the following:

```json
{
    "affine_bg": {
        "layers": [
            []
        ]
    }
}
```

The fields for affine backgrounds are the following:

- `"layers"`: the list of tile layers to render as affine backgrounds. Layers
  must be referred to by their absolute path, separating layer groups from their
  children with `/`. For each affine background, you can use a tile layer or a
  list of tile layers, in which case each layer will be drawn on top of the
  previous one as a single background image.
- `"palette_item"`: optional field which specifies the name of the
  [bn::bg_palette_item](https://gvaliente.github.io/butano/classbn_1_1bg__palette__item.html)
  to use for this background.
- `"colors_count"`: optional field which specifies the background palette size
  [1..256].
- `"repeated_tiles_reduction"`: optional field which specifies if repeated tiles
  must be reduced or not (`true` by default).
- `"big"`: optional boolean field which specifies if maps generated with this
  item are big or not. If this field is omitted, big maps are generated only if
  needed.
- `"draw_big"`: optional boolean field which specifies if the dimensions the
  layers are drawn into should favor generating small maps or not. For example,
  a 360x240 pixels map could generate a faster 512x512 pixels small map or a
  more memory efficient 512x256 pixels map. If this field is omitted, big maps
  are generated only if needed.
- `"tiles_compression"`: optional field which specifies the compression of the
  tiles data:
  - `"none"`: uncompressed data (this is the default option).
  - `"lz77"`: LZ77 compressed data.
  - `"run_length"`: run-length compressed data.
  - `"huffman"`: Huffman compressed data.
  - `"auto"`: uses the option which gives the smallest data size.
  - `"auto_no_huffman"`: uses the option which gives the smallest data size,
    excluding "huffman".
- `"palette_compression"`: optional field which specifies the compression of the
  colors data:
  - `"none"`: uncompressed data (this is the default option).
  - `"lz77"`: LZ77 compressed data.
  - `"run_length"`: run-length compressed data.
  - `"huffman"`: Huffman compressed data.
  - `"auto"`: uses the option which gives the smallest data size.
  - `"auto_no_huffman"`: uses the option which gives the smallest data size,
    excluding "huffman".
- `"map_compression"`: optional field which specifies the compression of the map
  data:
  - `"none"`: uncompressed data (this is the default option).
  - `"lz77"`: LZ77 compressed data.
  - `"run_length"`: run-length compressed data.
  - `"huffman"`: Huffman compressed data.
  - `"auto"`: uses the option which gives the smallest data size.
  - `"auto_no_huffman"`: uses the option which gives the smallest data size,
    excluding "huffman".
- `"compression"`: optional field which specifies the compression of the tiles,
  the colors and the map data:
  - `"none"`: uncompressed data (this is the default option).
  - `"lz77"`: LZ77 compressed data.
  - `"run_length"`: run-length compressed data.
  - `"huffman"`: Huffman compressed data.
  - `"auto"`: uses the option which gives the smallest data size.
  - `"auto_no_huffman"`: uses the option which gives the smallest data size,
    excluding "huffman".

If the conversion process has finished successfully, a
[bn::affine_bg_item](https://gvaliente.github.io/butano/classbn_1_1affine__bg__item.html)
should have been generated in the `build` folder.

For example, from two files named `world.tmx` and `world.json`, a header file
named `bntmx_map_items_world.h` is generated in the `build` folder.

You can use this header to create an affine background with only one line of
C++ code:

```c++
#include "bntmx_map_items_world.h"

bn::affine_bg_ptr affine_bg = bntmx::map_items::world_affine_bg.create_bg(0, 0);
```

### Map objects

A map file can contain multiple map objects layers. Each layer is exported as
a list of objects, and each object has an ID, aposition, a name, and an object
class. Object IDs is unique to its map, and multiple objects can have the same
name or class within or across maps. Object IDs are integers in the [0..65535]
range, so you can have up to 65536 different objects in a map.

**FIXME**
The names and classes of the objects are exported as IDs in `enum object_id` and
`enum object_class` found in the namespace of the generated map class.
Objects of each class as well as classless objects are stored separately from
each other for each layer.
Please use valid C++ enumeration value names for your object names and classes.

**FIXME**
The ID of an object isn't the one defined in the map file, so you have to name
an object to refer to it.
The position of an object isn't the one defined in the map file but its center.

An example of the `*.json` files required for map regular backgrounds is the
following:

```json
{
    "map_objects": {
        "layers": [
            []
        ]
    }
}
```

The fields for map objects are the following:

- `"layers"`: the list of map objects layers to export the objects from. Layers
  must be referred to by their absolute path, separating layer groups from their
  children with `/`. For each map objects layer, you can use an objects layer or
  a list of objects layers.
- `"class_enum_type"`: optional field which specifies the name of the
  enumeration type to use to generate a class ID to enumeration value pairing
  array from the map objects' class names. The Butano target will namespace
  class enum values with this type.
- `"class_enum_prefix"`: optional field which specifies the prefix to apply to
  the class names to make them match the class enumeration values. Used only for
  the C target to work around the lack of namespaces.

If the conversion process has finished successfully, a `bntmx::map_objects_item`
should have been generated in the `build` folder.

If there are object classes, a `bn::pair<uint16_t, bn::string_view>` array and
its matching span should have been generated alongside the
`bntmx::map_objects_item`. If you declared a class enumeration type, a similar
array and span should have been generated too.

For example, from two files named `world.tmx` and `world.json`, a header file
named `bntmx_map_items_world.h` is generated in the `build` folder.

You can use this header to access a map's objects with only one line of
C++ code:

```c++
#include "bntmx_map_items_world.h"

bntmx::map_object map_object = bntmx::map_items::world_map_objects.object(0);
```

You can use this header to access a map's object class names with only one line
of C++ code:

```c++
#include "bntmx_map_items_world.h"

bn::array<const bn::pair<uint16_t, bn::string_view>, 3> array = bntmx::map_items::world_map_object_class_names_array;
bn::span<const bn::pair<uint16_t, bn::string_view>> span = bntmx::map_items::world_map_object_class_names_span;
```

You can use this header to access a map's object class enum with only one line
of C++ code:

```c++
enum class object_class {
    bridge,
    house,
    tree,
}

#include "bntmx_map_items_world.h"

bn::array<const bn::pair<uint16_t, object_class>, 3> array = bntmx::map_items::world_map_object_class_enum_array;
bn::span<const bn::pair<uint16_t, object_class>> span = bntmx::map_items::world_map_object_class_enum_span;
```

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
