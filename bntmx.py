"""
Copyright (c) 2023 Adrien Plazas <kekun.plazas@laposte.net>
zlib License, see LICENSE file.
"""

from PIL import Image
import argparse
import json
import logging
import os
import re
import PIL
import subprocess
import sys
import xml.etree.ElementTree as ET

def flatten(list_of_list):
    # Return a flattened list of lists.

    return [item for sublist in list_of_list for item in sublist]

def spans(list_of_list):
    # Return a list of (index,length) pairs for a list of lists, so it can
    # be flattened but its elements can still be found.

    index_length_list = []
    index = 0
    for l in list_of_list:
        length = len(l)
        index_length_list.append((index, length))
        index = index + length
    return index_length_list

def c_array(l):
    # Returns the C litteral array or struct for the elements in the list.

    return "{" + ",".join(map(str, l)) + "}"

def ids(l):
    return c_array(list(map(lambda i: i.id, flatten(l))))

def bg_size(size):
    # Return a size rounded up to the next 256 multiple. This helps
    # converting the size of a map into the size of its background images.

    return size if size % 256 == 0 else (size // 256 + 1) * 256

class MapObject:
    def __init__(self, x, y, id):
        self.x = x
        self.y = y
        self.id = id

    def cpp_object(self, namespace):
        return 'bntmx::map_object(bn::fixed_point({x}, {y}), {namespace}::{id})'.format(x=self.x, y=self.y, namespace=namespace, id=self.id)

class TSX:
    def __init__(self, filename):
        self._filename = os.path.realpath(filename)
        self._root = ET.parse(filename)

        self._n_tiles = int(self._root.find(".").get("tilecount"))
        self._tile_width = int(self._root.find(".").get("tilewidth"))
        self._tile_height = int(self._root.find(".").get("tileheight"))
        self._columns = int(self._root.find(".").get("columns"))
        self._lines = self._n_tiles // self._columns
        self._image = Image.open(self.image_filename())

    def filename(self):
        return self._filename

    def image_filename(self):
        directory = os.path.dirname(self._filename)
        return os.path.join(directory, self._root.find("./image").get("source"))

    def n_tiles(self):
        # Return the number of tiles in the set

        return self._n_tiles

    def compose(self, dst_image, tile_id, x, y):
        # Compose a tile on an image

        src_x = (tile_id % self._columns) * self._tile_width
        src_y = (tile_id // self._lines) * self._tile_height
        dst_image.alpha_composite(self._image, (x, y), (src_x, src_y, src_x + self._tile_width, src_y + self._tile_height))

class TMX:
    def __init__(self, filename):
        self._filename = os.path.realpath(filename)
        self._root = ET.parse(self._filename)

        self._columns = int(self._root.find(".").get("width"))
        self._lines = int(self._root.find(".").get("height"))

        self._tile_width = int(self._root.find(".").get("tilewidth"))
        self._tile_height = int(self._root.find(".").get("tileheight"))

        directory = os.path.dirname(self._filename)
        self._tilesets = []
        for tileset in self._root.findall("./tileset"):
            tsx = TSX(os.path.join(directory, tileset.get("source")))
            first_id = int(tileset.get("firstgid"))
            last_id = first_id + tsx.n_tiles() - 1
            self._tilesets.append((first_id, last_id, tsx))

    def _object_position(self, object_node):
        # While the origin of maps is their top-left corner, the origin of
        # objects is their bottom left one, hence we have to substract half
        # their height and not add it to get their center.
        x = int(object_node.get("x")) + int(object_node.get("width")) // 2
        y = int(object_node.get("y")) - int(object_node.get("height")) // 2
        return x, y

    def _tiles_layer_path_to_xpath(self, layer_path):
        # Convert a layer path from the JSON descriptor into the XPath to the layer's node

        layer_path_elements = layer_path.split("/")
        xpath = "."
        for group in layer_path_elements[:-1]:
            xpath += "/group[@name='" + group + "']"
        xpath += "/layer[@name='" + layer_path_elements[-1] + "']"

        return xpath

    def _objects_layer_path_to_xpath(self, layer_path):
        # Convert a layer path from the JSON descriptor into the XPath to the layer's node

        layer_path_elements = layer_path.split("/")
        xpath = "."
        for group in layer_path_elements[:-1]:
            xpath += "/group[@name='" + group + "']"
        xpath += "/objectgroup[@name='" + layer_path_elements[-1] + "']"

        return xpath

    def dependencies(self):
        deps = []
        for first, last, tsx in self._tilesets:
            deps.append(tsx.filename())
            deps.append(tsx.image_filename())
        return deps

    def dimensions_in_pixels(self):
        # Return the size of the map in pixels

        return (self._columns * self._tile_width, self._lines * self._tile_height)

    def dimensions_in_tiles(self):
        # Return the size of the map in tiles

        return (self._columns, self._lines)

    def tile_dimensions(self):
        # Return the size of the tiles in pixel

        return (self._tile_width, self._tile_height)

    def background_color(self):
        # Return the background color of the map.

        return self._root.find(".").get("backgroundcolor")

    def tilesets(self):
        # Return the tilesets.

        return self._tilesets

    def objects(self, layer_path):
        # Return the objects of a layer.

        objects = []
        xpath = self._objects_layer_path_to_xpath(layer_path) + "/object"
        for item_node in self._root.findall(xpath):
            item_id = item_node.get("name")
            item_x, item_y = self._object_position(item_node)
            if item_id is None or item_id == "":
                logging.warning("{filename}: Unnamed item object at position {x}:{y}.".format(filename=self._filename, x=item_x, y=item_y))
                continue
            objects.append(MapObject(item_x, item_y, item_id))
        return objects

    def compose(self, dst_image, layer_path, x, y):
        # Compose a layer on an image

        xpath = self._tiles_layer_path_to_xpath(layer_path) + "/data[@encoding='csv']"

        # The size of the map, in pixels
        src_width, src_height = self.dimensions_in_pixels()
        # The size of each individual background
        bg_width, bg_height = bg_size(src_width), bg_size(src_height)
        # The offset to center the layer on the background
        offset_x, offset_y = (bg_width - src_width) // 2, (bg_height - src_height) // 2

        y2 = 0
        for line in iter(self._root.find(xpath).text.splitlines()):
            if line == '':
                continue;

            x2 = 0
            for tile_id in line.split(","):
                if tile_id == '':
                    continue;

                tile_id = int(tile_id)

                if tile_id != 0:
                    for first, last, tsx in self._tilesets:
                        if tile_id >= first and tile_id <= last:
                            tsx.compose(dst_image, tile_id - first, x + x2 * self._tile_width + offset_x, y + y2 * self._tile_height + offset_y)

                x2 = x2 + 1
            y2 = y2 + 1

    def tiles(self, layer_path):
        # Return the tiles of a layer.

        xpath = self._tiles_layer_path_to_xpath(layer_path) + "/data[@encoding='csv']"
        lines = iter(self._root.find(xpath).text.splitlines())

        line_is_not_empty = lambda line: line != ''
        tile_id_to_enum_name = lambda tile_id: str(int(tile_id))
        line_tile_id_to_enum_name = lambda line: ",".join(list(map(tile_id_to_enum_name, line.strip(",").split(","))))

        return '        {{\n            {tiles}\n        }}' \
            .format(tiles=",\n            ".join(map(line_tile_id_to_enum_name, filter(line_is_not_empty, lines))))

class TMXConverter:
    def __init__(self, tmx_filename):
        self._tmx = TMX(tmx_filename)
        self._name = os.path.splitext(os.path.basename(tmx_filename))[0]
        descriptor = open(os.path.splitext(tmx_filename)[0] + ".json")
        self._descriptor = json.load(descriptor)

    def _spans(self, list_of_list):
        # Return a list of (index,length) pairs for a list of lists, so it can
        # be flattened but its elements can still be found.

        index_length_list = []
        index = 0
        for l in list_of_list:
            length = len(l)
            index_length_list.append((index, length))
            index = index + length
        return index_length_list

    def _flatten(self, list_of_list):
        # Return a flattened list of lists.

        return [item for sublist in list_of_list for item in sublist]

    def _objects(self):
        # Return the nested lists of objects for the list of object layers

        return list(map(lambda layer_path: self._tmx.objects(layer_path), self._descriptor["objects"]))

    def dependencies(self):
        return self._tmx.dependencies()

    def name(self):
        # Return the name of the map

        return self._name

    def regular_bg_image(self):
        # Convert the TMX into its regular background image.

        # The size of the map, in pixels
        src_width, src_height = self._tmx.dimensions_in_pixels()
        # The size of each individual background
        bg_width, bg_height = bg_size(src_width), bg_size(src_height)

        # Compose the layers into a single background image
        n_layers = len(self._descriptor["graphics"])
        gfx_im = Image.new("RGBA", (bg_width, bg_height * n_layers), self._tmx.background_color())
        for i, layer_path in enumerate(self._descriptor["graphics"]):
            self._tmx.compose(gfx_im, layer_path, 0, bg_height * i)

        # Make the image paletted
        gfx_im = gfx_im.quantize(256)

        return gfx_im

    def regular_bg_descriptor(self):
        # Convert the TMX into its regular background descriptor.

        _, src_height = self._tmx.dimensions_in_pixels()
        bg_height = bg_size(src_height)

        descriptor = '''\
{{
    "type": "regular_bg",
    "bpp_mode": "bpp_4_auto",
    "height": {bg_height}
}}
'''.format(bg_height=bg_height)

        return descriptor

    def cpp_header(self):
        # Convert the TMX into its C++ header.

        guard = "BNTMX_MAPS_" + self._name.upper() + "_H"
        width_in_pixels, height_in_pixels = self._tmx.dimensions_in_pixels()
        width_in_tiles, height_in_tiles = self._tmx.dimensions_in_tiles()
        tile_width, tile_height = self._tmx.tile_dimensions()
        n_graphics_layers = len(self._descriptor["graphics"])
        n_objects_layers = len(self._descriptor["objects"])
        n_tiles_layers = len(self._descriptor["tiles"])
        objects = self._objects()
        tileset_bounds = []
        for first, last, tsx in self._tmx.tilesets():
            enum_base = os.path.splitext(os.path.basename(tsx.filename()))[0].upper()
            tileset_bounds.append(enum_base + "=" + str(first))
            tileset_bounds.append(enum_base + "_LAST=" + str(last))
        tile_ids = c_array(tileset_bounds)

        header = '''\
#ifndef {guard}
#define {guard}

#include "bntmx_map.h"

namespace bntmx::maps
{{
    class {map_name} : public map
    {{
        public:
            enum object_id {object_ids};
            enum tile_id {tile_ids};

            constexpr {map_name}()
            {{
            }}

            constexpr ~{map_name}()
            {{
            }}

            constexpr bn::size dimensions_in_pixels() const
            {{
                return bn::size({width_in_pixels}, {height_in_pixels});
            }}

            constexpr bn::size dimensions_in_tiles() const
            {{
                return bn::size({width_in_tiles}, {height_in_tiles});
            }}

            constexpr bn::size tile_dimensions() const
            {{
                return bn::size({tile_width}, {tile_height});
            }}

            constexpr int width_in_pixels() const
            {{
                return {width_in_pixels};
            }}

            constexpr int height_in_pixels() const
            {{
                return {height_in_pixels};
            }}

            constexpr int width_in_tiles() const
            {{
                return {width_in_tiles};
            }}

            constexpr int height_in_tiles() const
            {{
                return {height_in_tiles};
            }}

            constexpr int tile_width() const
            {{
                return {tile_width};
            }}

            constexpr int tile_height() const
            {{
                return {tile_height};
            }}

            constexpr int n_graphics_layers() const
            {{
                return {n_graphics_layers};
            }}

            constexpr int n_objects_layers() const
            {{
                return {n_objects_layers};
            }}

            constexpr int n_tiles_layers() const
            {{
                return {n_tiles_layers};
            }}

            constexpr bn::regular_bg_item regular_bg_item() const;
            constexpr const bn::span<const bntmx::map_object> objects_layer(int objects_layer_index) const;
            constexpr const bn::span<const bntmx::map_tile> tiles(int tiles_layer_index) const;
    }};
}}

#endif
'''.format(guard=guard, map_name=self._name, object_ids=ids(objects), tile_ids=tile_ids, width_in_pixels=width_in_pixels, height_in_pixels=height_in_pixels, width_in_tiles=width_in_tiles, height_in_tiles=height_in_tiles, tile_width=tile_width, tile_height=tile_height, n_graphics_layers=n_graphics_layers, n_objects_layers=n_objects_layers, n_tiles_layers=n_tiles_layers, n_objects=len(objects))

        return header

    def cpp_source(self):
        # Convert the TMX into its C++ source.

        header_filename = "bntmx_maps_" + self._name + ".h"

        width_in_tiles, height_in_tiles = self._tmx.dimensions_in_tiles()
        n_graphics_layers = len(self._descriptor["graphics"])
        n_objects_layers = len(self._descriptor["objects"])
        n_tiles_layers = len(self._descriptor["tiles"])
        size = width_in_tiles * height_in_tiles

        tiles = ",\n".join(list(map(lambda layer_path: self._tmx.tiles(layer_path), self._descriptor["tiles"])))

        objects = self._objects()
        objects_spans = c_array(map(c_array, spans(objects)))
        flattened_objects = flatten(objects)
        # We can't have empty constexpr arrays, so let's have a dummy element
        # instead. It doesn't take much space and keeps the code more readable
        # than by dropping them.
        cpp_objects = "{bntmx::map_object(bn::fixed_point(0, 0), -1)}"
        if len(flattened_objects) > 0:
            cpp_objects = c_array(list(map(lambda i: i.cpp_object(self._name), flattened_objects)))

        source = '''\
#include "{header_filename}"

#include <bn_regular_bg_items_{map_name}.h>
#include <bn_vector.h>

namespace bntmx::maps
{{
    static constexpr bntmx::map_object _objects[] = {cpp_objects};
    static constexpr struct {{int index; int length;}} _objects_spans[] = {objects_spans};
    static const bntmx::map_tile _tiles[{n_tiles_layers}][{size}] = {{
{tiles}
    }};

    constexpr bn::regular_bg_item {map_name}::regular_bg_item() const
    {{
        return bn::regular_bg_items::{map_name};
    }}

    constexpr const bn::span<const bntmx::map_object> {map_name}::objects_layer(int objects_layer_index) const
    {{
        BN_ASSERT(objects_layer_index < {n_objects_layers}, "Invalid objects layer index: ", objects_layer_index);
        return bn::span(&_objects[_objects_spans[objects_layer_index].index], _objects_spans[objects_layer_index].length);
    }}

    constexpr const bn::span<const bntmx::map_tile> {map_name}::tiles(int tiles_layer_index) const
    {{
        BN_ASSERT(tiles_layer_index < {n_tiles_layers}, "Invalid tiles layer index: ", tiles_layer_index);
        return bn::span(_tiles[tiles_layer_index], {size});
    }}
}}
'''.format(header_filename=os.path.basename(header_filename), map_name=self._name, n_objects_layers=n_objects_layers, n_tiles_layers=n_tiles_layers, size=str(size), tiles=tiles, objects_spans=objects_spans, cpp_objects=cpp_objects)

        return source

def process(maps_dirs, build_dir):
    for maps_dir in maps_dirs:
        for map_file in os.listdir(maps_dir):
            if map_file.endswith('.tmx') and os.path.isfile(os.path.join(maps_dir, map_file)):
                build_graphics_dir = os.path.join(build_dir, "graphics")
                build_include_dir = os.path.join(build_dir, "include")
                build_src_dir = os.path.join(build_dir, "src")

                if not os.path.exists(build_dir):
                    os.makedirs(build_dir)
                if not os.path.exists(build_graphics_dir):
                    os.makedirs(build_graphics_dir)
                if not os.path.exists(build_include_dir):
                    os.makedirs(build_include_dir)
                if not os.path.exists(build_src_dir):
                    os.makedirs(build_src_dir)

                tmx_filename = os.path.join(maps_dir, map_file)
                converter = TMXConverter(tmx_filename)
                map_name = converter.name()

                tmx_json_filename = os.path.join(maps_dir, map_name + ".json")
                bmp_filename = os.path.join(build_dir, "graphics", map_name + ".bmp")
                bmp_json_filename = os.path.join(build_dir, "graphics", map_name + ".json")
                header_filename = os.path.join(build_dir, "include", "bntmx_maps_" + map_name + ".h")
                source_filename = os.path.join(build_dir, "src", "bntmx_maps_" + map_name + ".cpp")

                # Don't rebuild unchanged files
                input_mtime = max(map(lambda filename : os.path.getmtime(filename) if os.path.isfile(filename) else 0, [tmx_filename, tmx_json_filename] + converter.dependencies()))
                output_mtime = min(map(lambda filename : os.path.getmtime(filename) if os.path.isfile(filename) else 0, [bmp_filename, bmp_json_filename, header_filename, source_filename]))
                if input_mtime < output_mtime:
                    continue

                # Export the image
                gfx_im = converter.regular_bg_image()
                gfx_im.save(bmp_filename, "BMP")

                # Export the graphics descriptor
                bmp_json = converter.regular_bg_descriptor()
                bmp_json_file = open(bmp_json_filename, "w")
                bmp_json_file.write(bmp_json)
                bmp_json_file.close()

                # Export the C++ header
                header = converter.cpp_header()
                output_file = open(header_filename, "w")
                output_file.write(header)
                output_file.close()

                # Export the C++ source
                source = converter.cpp_source()
                output_file = open(source_filename, "w")
                output_file.write(source)
                output_file.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Compile Tiled maps into code and data usable by the game engine.')
    parser.add_argument('--build', required=True, help='build directory path')
    parser.add_argument('mapsdirs', metavar='mapsdir', nargs='+',
                        help='maps directories paths')
    args = parser.parse_args()
    process(args.mapsdirs, args.build)
