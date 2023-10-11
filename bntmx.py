"""
Copyright (c) 2023 Adrien Plazas <kekun.plazas@laposte.net>
zlib License, see LICENSE file.
"""

from PIL import Image
from tmx import TMX
import argparse
import json
import os
import re
import bntemplate
import ctemplate

_targets = ['butano', 'c']

def write_to_file(filename: str, text: str):
    f = open(filename, "w")
    f.write(text)
    f.close()

def inline_c_array(l: list) -> str:
    """
    Return the inline C or C++ literal array or struct for the elements in the list.

    :param l: the list of the array elements
    :returns: the inline array literal
    """

    return "{" + ",".join(map(str, l)) + "}"

def multiline_c_array(l: list, indentation: str, depth: int) -> str:
    """
    Return the multiline C or C++ literal array or struct for the elements in the list.

    :param l: the list of the array elements
    :param indentation: the characters to use for an indentation level
    :param depth: the depth of the indentation
    :returns: the multiline array literal
    """

    outer_indentation = indentation * depth
    inner_indentation = indentation * (depth + 1)
    splitter = ",\n" + inner_indentation

    return "{\n" + inner_indentation + splitter.join(map(str, l)) + "\n" + outer_indentation + "}"

def bg_size(size: int):
    """
    Return a size rounded up to the next 256 multiple. This helps converting the
    size of a map into the size of its background images.

    :param size: the size of the map
    :returns: the size of the background that can fit the requested size
    """

    return size if size % 256 == 0 else (size // 256 + 1) * 256

def mangle(name: str) -> str:
    """
    Return the lowercase mangled C or C++ name for the given name.

    Names are mangled in the following way:
    - leading characters that aren't ASCII letters are trimmed
    - trailing characters that aren't ASCII letters or digits are trimmed
    - sequences of characters that aren't ASCII letters or digits are replaced
      by a single underscore character
    - letters are lowercased

    :param name: the name to mangle
    :returns: the lowercase mangled name
    """

    match = re.match('^[0-9_]*([a-z0-9_]+?)_*$', re.sub('[^a-z0-9]+', '_', name.lower()))
    return "" if match is None else match.group(1)

class TMXConverter:
    def __init__(self, target, tmx_filename):
        assert target in _targets

        self._target = target
        self._tmx = TMX(tmx_filename)
        self._basename = os.path.splitext(os.path.basename(tmx_filename))[0]
        self._name = mangle(self._basename)
        descriptor = open(os.path.splitext(tmx_filename)[0] + ".json")
        self._descriptor = json.load(descriptor)
        # Add empty lists so we don't ave to check their existence every time.
        if "graphics" not in self._descriptor:
            self._descriptor["graphics"] = []
        if "objects" not in self._descriptor:
            self._descriptor["objects"] = []
        if "tiles" not in self._descriptor:
            self._descriptor["tiles"] = []

        # The list of MapObjects for the list of object layers
        self._objects = list(map(lambda layer_path: self._tmx.objects(layer_path), self._descriptor["objects"] if "objects" in self._descriptor else []))
        self._assign_id_and_layer_to_objects()

    def _assign_id_and_layer_to_objects(self):
        object_classes = self._object_classes()
        id = 0

        # Layers are already sorted, let's first sort by layers
        for layer_index, layer_map_objects in enumerate(self._objects):
            objects = layer_map_objects.objects()

            # Then sort by classes
            for object_class in object_classes:
                if object_class not in objects:
                    continue

                # Then sort in whatever order the objects come in
                for object in objects[object_class]:
                    object.map_layer = layer_index
                    object.map_id = id
                    id += 1

    def _object_classes(self):
        # Return the sorted set of map object class names in the whole map, including the "" class
        # If there are no objects layers an empty list is returned, there is not even the "" class.

        return sorted(set([map_object_class for layer_map_objects in self._objects for map_object_class in layer_map_objects.objects().keys()]))

    def _object_classes_enum(self, namespace):
        # Return the list of enumeration definitions for the map object class names in the whole map, excluding the "" class

        return list(map(lambda i_and_object_class: namespace + mangle(i_and_object_class[1]).upper() + "=" + str(i_and_object_class[0]), enumerate(self._object_classes())))[1:]

    def _all_objects(self):
        # Return the list of map objects in the whole map

        return sorted([map_object for layer_map_objects in self._objects for _, map_objects in layer_map_objects.objects().items() for map_object in map_objects], key=lambda o: o.map_id)

    def _object_ids_enum(self, namespace):
        # Return the list of enumeration definitions for the map object ids in the whole map, excluding the None ids

        return [namespace + mangle(map_object.id).upper() + "=" + str(map_object.map_id) for map_object in self._all_objects() if map_object.id is not None]

    def _tile_ids_enum(self, namespace):
        # Return the list of enumeration definitions for the map tile ids in the whole map

        tile_ids = []
        for first, last, tsx in self._tmx.tilesets():
            enum_base = mangle(os.path.splitext(os.path.basename(tsx.filename()))[0]).upper()
            tile_ids.append(namespace + enum_base + "=" + str(first))
            tile_ids.append(namespace + enum_base + "_LAST=" + str(last))
        return tile_ids

    def _object_spans(self):
        # Return a list for each layer of lists of (index,length) pairs for each
        # object of a given class in the layer, so objects can be flattened but
        # they can still be found per layer and class.

        index_lengths = []
        index = 0
        object_classes = self._object_classes()
        for layer in self._objects:
            layer_index_lengths = []
            for object_class in object_classes:
                length = len(layer.objects()[object_class]) if object_class in layer.objects() else 0
                layer_index_lengths.append((index, length))
                index = index + length
            index_lengths.append(layer_index_lengths)
        return index_lengths

    def dependencies(self):
        return self._tmx.dependencies()

    def basename(self):
        # Return the basename of the map

        return self._basename

    def name(self):
        # Return the basename of the map

        return self._name

    def regular_bg_image(self):
        # Convert the TMX into its regular background image.

        if "graphics" not in self._descriptor or len(self._descriptor["graphics"]) == 0:
            return None

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

        return bntemplate.graphics.format(bg_height=bg_height)

    def butano_header(self):
        # Convert the TMX into its C++ header.

        n_graphics_layers = len(self._descriptor["graphics"]) if "graphics" in self._descriptor else 0
        n_objects_layers = len(self._descriptor["objects"]) if "objects" in self._descriptor else 0
        n_tiles_layers = len(self._descriptor["tiles"]) if "tiles" in self._descriptor else 0

        indentation = "    "
        if self._target == "butano":
            graphics = "bn::regular_bg_items::" + self._name if n_graphics_layers > 0 else "std::monostate()"
            graphics_include = "#include <bn_regular_bg_items_" + self._name + ".h>" if n_graphics_layers > 0 else ""
            indentation_depth = 1
            namespace = ""
            template = bntemplate.template
        elif self._target == "c":
            graphics = ""
            graphics_include = ""
            indentation_depth = 0
            namespace = "BNTMX_MAPS_" + self._name.upper() + "_"
            template = ctemplate.template

        guard = "BNTMX_MAPS_" + self._name.upper() + "_H"
        width_in_pixels, height_in_pixels = self._tmx.dimensions_in_pixels()
        width_in_tiles, height_in_tiles = self._tmx.dimensions_in_tiles()
        tile_width, tile_height = self._tmx.tile_dimensions()
        objects = self._objects

        object_classes = self._object_classes_enum(namespace)
        if len(object_classes) == 0:
            object_classes_definition = template['object_classes_definition_empty']
        else:
            object_classes_literal = multiline_c_array(object_classes, indentation, indentation_depth)
            object_classes_definition = template['object_classes_definition_template'].format(map_name=self._name, object_classes=object_classes_literal)

        object_ids = self._object_ids_enum(namespace)
        if len(object_ids) == 0:
            object_ids_definition = template['object_ids_definition_empty']
        else:
            object_ids_literal = multiline_c_array(object_ids, indentation, indentation_depth)
            object_ids_definition = template['object_ids_definition_template'].format(map_name=self._name, object_ids=object_ids_literal)

        tile_ids = self._tile_ids_enum(namespace)
        if len(tile_ids) == 0:
            tile_ids_definition = template['tile_ids_definition_empty']
        else:
            tile_ids_literal = multiline_c_array(tile_ids, indentation, indentation_depth)
            tile_ids_definition = template['tile_ids_definition_template'].format(map_name=self._name, tile_ids=tile_ids_literal)

        return template['header_template'].format(
            graphics=graphics,
            graphics_include=graphics_include,
            guard=guard,
            height_in_pixels=height_in_pixels,
            height_in_tiles=height_in_tiles,
            map_name=self._name,
            n_graphics_layers=n_graphics_layers,
            n_objects_layers=n_objects_layers,
            n_objects=len(objects),
            n_tiles_layers=n_tiles_layers,
            object_classes_definition=object_classes_definition,
            object_ids_definition=object_ids_definition,
            tile_height=tile_height,
            tile_ids_definition=tile_ids_definition,
            tile_width=tile_width,
            width_in_pixels=width_in_pixels,
            width_in_tiles=width_in_tiles)

    def butano_source(self):
        # Convert the TMX into its C++ source.

        indentation = "    "
        if self._target == "butano":
            indentation_depth = 1
            namespace = "bntmx::maps::" + self._name + "::"
            template = bntemplate.template
        elif self._target == "c":
            indentation_depth = 0
            namespace = "BNTMX_MAPS_" + self._name.upper() + "_"
            template = ctemplate.template

        header_filename = "bntmx_maps_" + self._name + ".h"

        width_in_tiles, height_in_tiles = self._tmx.dimensions_in_tiles()
        n_graphics_layers = len(self._descriptor["graphics"]) if "graphics" in self._descriptor else 0
        n_objects_layers = len(self._descriptor["objects"]) if "objects" in self._descriptor else 0
        n_tiles_layers = len(self._descriptor["tiles"]) if "tiles" in self._descriptor else 0
        size = width_in_tiles * height_in_tiles

        n_objects_classes = len(self._object_classes())
        objects_spans = multiline_c_array(map(lambda layer: multiline_c_array(map(inline_c_array, layer), indentation, indentation_depth + 1), self._object_spans()), indentation, indentation_depth)
        objects = self._all_objects()
        n_objects = len(objects)
        object_to_cpp_literal = lambda o: template['map_object_template'].format(x=o.x, y=o.y, id=o.map_id if o.id is None else namespace + str(o.id))
        objects_literal = multiline_c_array(list(map(object_to_cpp_literal, objects)), indentation, indentation_depth)

        # Get the C or C++ array literal for the given list of tiles, matching lines and columns of the map for readability.
        tiles_to_array_literal = lambda tiles: multiline_c_array([",".join(tiles[i:i + width_in_tiles]) for i in range(0, len(tiles), width_in_tiles)], indentation, indentation_depth + 1)
        # Get the C or C++ array literal of tiles for the given tiles layer path.
        tiles_layer_path_to_array_literal = lambda layer_path: tiles_to_array_literal(self._tmx.tiles(layer_path))
        # Get the C or C++ array literal of tiles layers for the given tiles layer paths.
        tiles_literal = multiline_c_array(list(map(tiles_layer_path_to_array_literal, self._descriptor["tiles"] if "tiles" in self._descriptor else [])), indentation, indentation_depth)

        if n_objects == 0 or n_objects_classes == 0 or n_objects_layers == 0:
            object_getter = template['object_dummy']
            objects_definition = template['objects_definition_empty']
            objects_getter_classless = template['objects_dummy']
            objects_getter_with_class = template['objects_dummy']
        else:
            object_getter = template['object_getter']
            objects_definition = template['objects_definition_template'].format(
                n_objects_classes=n_objects_classes,
                n_objects_layers=n_objects_layers,
                objects=objects_literal,
                objects_spans=objects_spans)
            objects_getter_classless = template['objects_getter_classless']
            objects_getter_with_class = template['objects_getter_with_class']

        if size == 0 or n_tiles_layers == 0:
            tiles_definition = ''
            tiles_getter = template['tiles_dummy']
        else:
            tiles_definition = template['tiles_definition_template'].format(
                n_tiles_layers=n_tiles_layers,
                size=size,
                tiles=tiles_literal)
            tiles_getter = template['tiles_getter_template'].format(size=size)

        return template['source_template'].format(
            header_filename=os.path.basename(header_filename),
            map_name=self._name,
            n_objects_classes=n_objects_classes,
            n_objects_layers=n_objects_layers,
            n_objects=n_objects,
            n_tiles_layers=n_tiles_layers,
            object_getter=object_getter,
            objects_getter_classless=objects_getter_classless,
            objects_getter_with_class=objects_getter_with_class,
            objects_definition=objects_definition,
            size=size,
            tiles_definition=tiles_definition,
            tiles_getter=tiles_getter,
            tiles=tiles_literal)

def process(target, maps_dirs, build_dir):
    assert target in _targets

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

    # Export the global header
    include_filename = os.path.join(build_dir, "include", "bntmx.h")
    if target == "butano":
        include = bntemplate.include
    elif target == "c":
        include = ctemplate.include
    write_to_file(include_filename, include)

    for maps_dir in maps_dirs:
        for map_file in os.listdir(maps_dir):
            if map_file.endswith('.tmx') and os.path.isfile(os.path.join(maps_dir, map_file)):
                tmx_filename = os.path.join(maps_dir, map_file)
                converter = TMXConverter(target, tmx_filename)
                map_basename = converter.basename()
                map_name = converter.name()

                tmx_json_filename = os.path.join(maps_dir, map_basename + ".json")
                bmp_filename = os.path.join(build_dir, "graphics", map_name + ".bmp")
                bmp_json_filename = os.path.join(build_dir, "graphics", map_name + ".json")
                header_filename = os.path.join(build_dir, "include", "bntmx_maps_" + map_name + ".h")
                if target == "butano":
                    source_filename = os.path.join(build_dir, "src", "bntmx_maps_" + map_name + ".cpp")
                elif target == "c":
                    source_filename = os.path.join(build_dir, "src", "bntmx_maps_" + map_name + ".c")

                # Don't rebuild unchanged files
                input_mtime = max(map(lambda filename : os.path.getmtime(filename) if os.path.isfile(filename) else 0, [tmx_filename, tmx_json_filename] + converter.dependencies()))
                output_mtime = min(map(lambda filename : os.path.getmtime(filename) if os.path.isfile(filename) else 0, [bmp_filename, bmp_json_filename, header_filename, source_filename]))
                if input_mtime < output_mtime:
                    continue

                # Export the image
                gfx_im = converter.regular_bg_image()
                if gfx_im is not None:
                    gfx_im.save(bmp_filename, "BMP")
                    # Export the graphics descriptor
                    if target == "butano":
                        write_to_file(bmp_json_filename, converter.regular_bg_descriptor())

                # Export the C++ header
                write_to_file(header_filename, converter.butano_header())

                # Export the C++ source
                write_to_file(source_filename, converter.butano_source())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Compile Tiled maps into code and data usable by the game engine.')
    parser.add_argument('--target', choices=_targets, required=True, help='build target')
    parser.add_argument('--build', required=True, help='build directory path')
    parser.add_argument('mapsdirs', metavar='mapsdir', nargs='+',
                        help='maps directories paths')
    args = parser.parse_args()
    process(args.target, args.mapsdirs, args.build)
