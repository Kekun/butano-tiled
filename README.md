# TMX Tiled Map Library for Butano

This is a Tiled .tmx file map converter for Butano. It looks for maps in the
maps/ directory and rasterizes them as graphics files for Butano and a matching
partially implemented C++ class containing information about the layers, tiles
and objects of the map.

It has been exported straight from a project it was tailored for, hence it isn't
generic in any way. If you can think of ways to genericize it please come
talking to me, I'll be interested. That being said, this is an extremely low
priority project for me and I have tons of much more important things to do, so
I may not reply at all. In such case, feel free to fork the project or to tell
me you want to take maintainership of it.

E.g. being able to parameterize maps via .json files would be neat, it would
allow the map converter to be more generic while making it feel like an integral
part of Butano.

## Usage

In your makefile add:
- `extrabuild/src` to `SOURCES`
- `extrabuild/include` to `INCLUDES`
- `extrabuild/graphics` to `GRAPHICS`
- `extrabuild` to `USERBUILD`
- `@$(PYTHON) -B extrabuilder.py --build=$(USERBUILD)` to `EXTTOOL`

Given a map named mymap, you should have the following files:
- `graphics/mymap_background.bmp`
- `graphics/mymap_background.json`
- `graphics/mymap_foreground.bmp`
- `graphics/mymap_foreground.json`
- `maps/mymap.tmx`

The script will generate the following files:
- `extrabuild/graphics/mymap_layers.bmp`
- `extrabuild/graphics/mymap_layers.json`
- `extrabuild/include/mw3_maps_mymap.h`
- `extrabuild/src/mw3_maps_mymap.cpp`

## Map Format

The .tmx file should have groups named `layer_n` where `n` is a natural number.
The numbers of the layers should be consecutive, starting from 0.

Each group should have the following layers:
- `graphics` which will be turned into `extrabuild/graphics/mymap_layers.bmp`
- `collisions` which will be accessed via `mw3::Map::collisions()`
- `objects` which will be accessed via `mw3::Map::get_item()`

The tiles are expected to be 16x16.
The collisions layer will have tiles matching `mw3::Tiles`.

## Map Logic

Each map is converted into an implementation of the abstract class `mw3::Map`
named `mw3::maps::mymap`. You still have to implement the following
logic-related methods:
- `mw3::maps::mymap::init()`
- `mw3::maps::mymap::enter()`
- `mw3::maps::mymap::leave()`
- `mw3::maps::mymap::deinit()`
- `mw3::maps::mymap::interact_with_item()`
- `mw3::maps::mymap::update_background()`
- `mw3::maps::mymap::update_foreground()`
- `mw3::maps::mymap::out_of_bounds()`
