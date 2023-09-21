#!/bin/python

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

def bounds(list_of_list):
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
    return "{" + ",".join(map(str, l)) + "}"

def ids(l):
    return c_array(list(map(lambda i: i.id, flatten(l))))

class MapItem:
    def __init__(self, x, y, id):
        self.x = x
        self.y = y
        self.id = id

    def cpp_object(self, namespace):
        return 'MapItem(bn::fixed_point({x}, {y}), {namespace}::{id})'.format(x=self.x, y=self.y, namespace=namespace, id=self.id)

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

    def _layer_path_to_xpath(self, layer_path):
        # Convert a layer path from the JSON descriptor into the XPath to the layer's node

        layer_path_elements = layer_path.split("/")
        xpath = "."
        for group in layer_path_elements[:-1]:
            xpath += "/group[@name='" + group + "']"
        xpath += "/layer[@name='" + layer_path_elements[-1] + "']"

        return xpath

    def dependencies(self):
        deps = []
        for first, last, tsx in self._tilesets:
            deps.append(tsx.filename())
            deps.append(tsx.image_filename())
        return deps

    def size(self):
        # Return the size of the map

        # FIXME Don't hardcode the tile size
        return (self._columns * 16, self._lines * 16)

    def columns(self):
        # Return the number of columns of the map

        return self._columns

    def lines(self):
        # Return the number of lines of the map

        return self._lines

    def n_layers(self):
        # Return the number of layers in the map.

        return len(self._root.findall("./group"))

    def background_color(self):
        # Return the background color of the map.

        return self._root.find(".").get("backgroundcolor")

    def items(self):
        # Return the items of the map.

        items = []
        for layer in range(self.n_layers()):
            layer_items = []
            for item_node in self._root.findall("./group[@name='layer_" + str(layer) + "']/objectgroup[@name='objects']/object"):
                item_id = item_node.get("name")
                item_x, item_y = self._object_position(item_node)
                if item_id is None or item_id == "":
                    logging.warning("{filename}: Unnamed item object at position {x}:{y}.".format(filename=self._filename, x=item_x, y=item_y))
                    continue
                layer_items.append(MapItem(item_x, item_y, item_id))
            items.append(layer_items)
        return items

    def compose(self, dst_image, layer_path, x, y):
        # Compose a layer on an image

        xpath = self._layer_path_to_xpath(layer_path) + "/data[@encoding='csv']"

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
                            tsx.compose(dst_image, tile_id - first, x + x2 * 16, y + y2 * 16)

                x2 = x2 + 1
            y2 = y2 + 1

    def collisions(self, layer):
        # Return the collisions of a layer. The colisions are defined as tiles
        # from the collision-tiles.tsx tileset and the bntmx::Tiles enumeration.

        tiles_enum_name = get_tiles_enum_name()
        tile_id_origin = int(self._root.find("./tileset[@source='collision-tiles.tsx']").get("firstgid"))
        xpath = "./group[@name='layer_" + str(layer) + "']/layer[@name='collisions']/data[@encoding='csv']"
        lines = iter(self._root.find(xpath).text.splitlines())

        line_is_not_empty = lambda line: line != ''
        tile_id_to_enum_name = lambda tile_id: tiles_enum_name[0 if tile_id == "0" else int(tile_id) - tile_id_origin]
        line_tile_id_to_enum_name = lambda line: ",".join(list(map(tile_id_to_enum_name, line.strip(",").split(","))))

        return '        {{\n            {collisions}\n        }}' \
            .format(collisions=",\n            ".join(map(line_tile_id_to_enum_name, filter(line_is_not_empty, lines))))

class TMXConverter:
    def __init__(self, tmx_filename):
        self._tmx = TMX(tmx_filename)
        self._name = os.path.splitext(os.path.basename(tmx_filename))[0]
        descriptor = open(os.path.splitext(tmx_filename)[0] + ".json")
        self._descriptor = json.load(descriptor)

    def _bounds(self, list_of_list):
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

    def dependencies(self):
        return self._tmx.dependencies()

    def name(self):
        # Return the name of the map

        return self._name

    def bg_size(self, size):
        # Return a size rounded up to the next 256 multiple. This helps
        # converting the size of a map into the size of its background images.

        return size if size % 256 == 0 else (size // 256 + 1) * 256

    def regular_bg_image(self):
        # Convert the TMX into its regular background image.

        # The size of the map, in pixels
        src_width, src_height = self._tmx.size()
        # The size of each individual background
        bg_width, bg_height = self.bg_size(src_width), self.bg_size(src_height)

        # Compose the layers into a single background image
        n_layers = self._tmx.n_layers()
        gfx_im = Image.new("RGBA", (bg_width, bg_height * n_layers), self._tmx.background_color())
        for i, layer_path in enumerate(self._descriptor["graphics"]):
            self._tmx.compose(gfx_im, layer_path, 0, bg_height * i)

        # Make the image paletted
        gfx_im = gfx_im.quantize(256)

        return gfx_im

    def regular_bg_descriptor(self):
        # Convert the TMX into its regular background descriptor.

        _, src_height = self._tmx.size()
        bg_height = self.bg_size(src_height)

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

        guard = "BNTMX_MAPS_" + self._name.upper() + "_COLLISIONS_H"
        width = self._tmx.columns()
        height = self._tmx.lines()
        n_layers = self._tmx.n_layers()
        items = self._tmx.items()

        header = '''\
#ifndef {guard}
#define {guard}

#include <bn_display.h>
#include <bn_regular_bg_position_hbe_ptr.h>
#include "bntmx_map.h"

namespace bntmx::maps
{{
    class {map_name} : public Map
    {{
        private:
            static const uint16_t _width = {width};
            static const uint16_t _height = {height};

        public:
            enum ObjectId {item_ids};

            {map_name}();
            ~{map_name}();

            constexpr uint16_t width() const
            {{
                return {width};
            }}

            constexpr uint16_t height() const
            {{
                return {height};
            }}

            constexpr uint8_t n_layers() const
            {{
                return {n_layers};
            }}

            constexpr uint8_t n_items(uint8_t layer_index) const;
            constexpr const uint8_t* collisions(uint8_t layer_index) const;

            MapItem get_item(uint8_t layer_index, uint8_t item_index) const;

            bn::regular_bg_ptr create_layer(uint8_t layer_index) const;
    }};
}}

#endif
'''.format(guard=guard, map_name=self._name, item_ids=ids(items), width=width, height=height, n_layers=n_layers, n_items=len(items))

        return header

    def cpp_source(self):
        # Convert the TMX into its C++ source.

        header_filename = "bntmx_maps_" + self._name + ".h"

        n_layers = self._tmx.n_layers()
        width = self._tmx.columns()
        height = self._tmx.lines()

        collisions = ",\n".join(list(map(lambda layer: self._tmx.collisions(layer), range(n_layers))))

        items =self._tmx.items()
        items_bounds = c_array(map(c_array, bounds(items)))
        flattened_items = flatten(items)
        # We can't have empty constexpr arrays, so let's have a dummy element
        # instead. It doesn't take much space and keeps the code more readable
        # than by dropping them.
        cpp_items = "{MapItem(bn::fixed_point(0, 0), -1)}"
        if len(flattened_items) > 0:
            cpp_items = c_array(list(map(lambda i: i.cpp_object(self._name), flattened_items)))

        source = '''\
#include "{header_filename}"

#include <bn_regular_bg_items_{map_name}_layers.h>
#include <bn_regular_bg_position_hbe_ptr.h>
#include <bn_vector.h>
#include "bntmx_tiles.h"

namespace bntmx::maps
{{
    static constexpr MapItem _items[] = {cpp_items};
    static constexpr struct {{uint8_t index; uint8_t length;}} _items_bounds[] = {items_bounds};
    static const uint8_t _collisions[{n_layers}][{size}] = {{
{collisions}
    }};

    {map_name}::{map_name}()
    {{
    }}

    {map_name}::~{map_name}()
    {{
    }}

    constexpr uint8_t {map_name}::n_items(uint8_t layer_index) const
    {{
        BN_ASSERT(layer_index < {n_layers}, "Invalid layer index: ", layer_index);
        return _items_bounds[layer_index].length;
    }}

    constexpr const uint8_t* {map_name}::collisions(uint8_t layer_index) const
    {{
        BN_ASSERT(layer_index < {n_layers}, "Invalid layer index: ", layer_index);

        return _collisions[layer_index];
    }}

    MapItem {map_name}::get_item(uint8_t layer_index, uint8_t item_index) const
    {{
        BN_ASSERT(layer_index < {n_layers}, "Invalid layer index: ", layer_index);
        BN_ASSERT(item_index < _items_bounds[layer_index].length, "Invalid item index: ", item_index);
        return _items[_items_bounds[layer_index].index + item_index];
    }}

    bn::regular_bg_ptr {map_name}::create_layer(uint8_t layer_index) const
    {{
        BN_ASSERT(layer_index < {n_layers}, "Invalid layer index: ", layer_index);

        return bn::regular_bg_items::{map_name}_layers.create_bg((bn::regular_bg_items::{map_name}_layers.map_item().dimensions().width() * 8 - bn::display::width()) / 2,
                                                                 (bn::regular_bg_items::{map_name}_layers.map_item().dimensions().height() * 8 - bn::display::height()) / 2,
                                                                 layer_index);
    }}
}}
'''.format(header_filename=os.path.basename(header_filename), map_name=self._name, n_layers=n_layers, size=str(width * height), collisions=collisions, items_bounds=items_bounds, cpp_items=cpp_items)

        return source

def process(build_dir):
    # FIXME Don't hardcode the maps directory, use args, there may be multiple ones.
    maps_dir = "maps"

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

            bmp_filename = os.path.join(build_dir, "graphics", map_name + "_layers.bmp")
            json_filename = os.path.join(build_dir, "graphics", map_name + "_layers.json")
            header_filename = os.path.join(build_dir, "include", "bntmx_maps_" + map_name + ".h")
            source_filename = os.path.join(build_dir, "src", "bntmx_maps_" + map_name + ".cpp")

            # Don't rebuild unchanged files
            input_mtime = max(map(lambda filename : os.path.getmtime(filename) if os.path.isfile(filename) else 0, [tmx_filename] + converter.dependencies()))
            output_mtime = min(map(lambda filename : os.path.getmtime(filename) if os.path.isfile(filename) else 0, [bmp_filename, json_filename, header_filename, source_filename]))
            if input_mtime < output_mtime:
                continue

            # Export the image
            gfx_im = converter.regular_bg_image()
            gfx_im.save(bmp_filename, "BMP")

            # Export the graphics descriptor
            json = converter.regular_bg_descriptor()
            json_file = open(json_filename, "w")
            json_file.write(json)
            json_file.close()

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


def get_tiles_enum_name():
    # Parse bntmx_tiles.h to extract the names of the tiles from the bntmx::Tiles
    # enum who match the the collision-tiles.tsx tileset.

    header = open("include/bntmx_tiles.h")
    return re.findall("enum Tiles[\n\s]*?{([\n\s\w,]*?)}", header.read(), re.MULTILINE)[0].replace("\n", "").replace(" ", "").strip(",").split(",")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Compile Tiled maps into code and data usable by the game engine.')
    parser.add_argument('--build', required=True, help='build folder path')
    args = parser.parse_args()
    process(args.build)
