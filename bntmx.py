"""
Copyright (c) 2023 Adrien Plazas <kekun.plazas@laposte.net>
zlib License, see LICENSE file.
"""

from enum import Enum
from PIL import Image
from tmx import TMX
import argparse
import json
import os
import re

class Target(Enum):
    butano = 'butano'
    c = 'c'

    def __str__(self):
        return self.value

def read_template(target, template):
    bntmx_dir = os.path.dirname(os.path.realpath(__file__))
    template_filename = os.path.join(bntmx_dir, 'templates', str(target), template)
    template_file = open(template_filename, 'r')
    return template_file.read()

_templates = {
    Target.butano: {
        'graphics': read_template(Target.butano, 'graphics.h'),
        'header_template': read_template(Target.butano, 'header_template.h'),
        'indentation': '    ',
        'map_object_template': read_template(Target.butano, 'map_object_template.h'),
        'object_dummy': read_template(Target.butano, 'object_dummy.h'),
        'object_getter': read_template(Target.butano, 'object_getter.h'),
        'object_ids_definition_empty': read_template(Target.butano, 'object_ids_definition_empty.h'),
        'object_ids_definition_template': read_template(Target.butano, 'object_ids_definition_template.h'),
        'objects_classes_definition_empty': read_template(Target.butano, 'objects_classes_definition_empty.h'),
        'objects_classes_definition_template': read_template(Target.butano, 'objects_classes_definition_template.h'),
        'objects_definition_empty': read_template(Target.butano, 'objects_definition_empty.h'),
        'objects_definition_template': read_template(Target.butano, 'objects_definition_template.h'),
        'objects_dummy': read_template(Target.butano, 'objects_dummy.h'),
        'objects_getter_classless': read_template(Target.butano, 'objects_getter_classless.h'),
        'objects_getter_with_class': read_template(Target.butano, 'objects_getter_with_class.h'),
        'source_template': read_template(Target.butano, 'source_template.cpp'),
        'tile_ids_definition_empty': read_template(Target.butano, 'tile_ids_definition_empty.h'),
        'tile_ids_definition_template': read_template(Target.butano, 'tile_ids_definition_template.h'),
        'tiles_definition_template': read_template(Target.butano, 'tiles_definition_template.h'),
        'tiles_dummy': read_template(Target.butano, 'tiles_dummy.h'),
        'tiles_getter_template': read_template(Target.butano, 'tiles_getter_template.h'),
    },
    Target.c: {
        'header_template': read_template(Target.c, 'header_template.h'),
        'indentation': '    ',
        'map_object_template': read_template(Target.c, 'map_object.h'),
        'object_dummy': read_template(Target.c, 'object_dummy.h'),
        'object_getter': read_template(Target.c, 'object_getter.h'),
        'object_ids_definition_empty': read_template(Target.c, 'object_ids_definition_empty.h'),
        'object_ids_definition_template': read_template(Target.c, 'object_ids_definition_template.h'),
        'objects_classes_definition_empty': read_template(Target.c, 'objects_classes_definition_empty.h'),
        'objects_classes_definition_template': read_template(Target.c, 'objects_classes_definition_template.h'),
        'objects_definition_empty': read_template(Target.c, 'objects_definition_empty.h'),
        'objects_definition_template': read_template(Target.c, 'objects_definition_template.h'),
        'objects_dummy': read_template(Target.c, 'objects_dummy.h'),
        'objects_getter_classless': read_template(Target.c, 'objects_getter.h'),
        'objects_getter_with_class': read_template(Target.c, 'objects_getter.h'),
        'source_template': read_template(Target.c, 'source_template.c'),
        'tile_ids_definition_empty': read_template(Target.c, 'tile_ids_definition_empty.h'),
        'tile_ids_definition_template': read_template(Target.c, 'tile_ids_definition_template.h'),
        'tiles_definition_template': read_template(Target.c, 'tiles_definition_template.h'),
        'tiles_dummy': read_template(Target.c, 'tiles_dummy.h'),
        'tiles_getter_template': read_template(Target.c, 'tiles_getter_template.h'),
    },
}

def write_to_file(filename: str, text: str):
    f = open(filename, "w")
    f.write(text)
    f.close()

def lines(l: list, tail: str) -> str:
    """
    Return a string with a line for each element.

    :param l: the list of the elements
    :returns: a string with a line for each element
    """

    if not l:
        return ''

    return (tail + '\n').join(map(str, l)) + tail

def indent(s: str, indentation: str, depth: int) -> str:
    """
    Return the indented multiline string

    Empty lines are left unindented.

    :param s: the string to indent
    :param indentation: the characters to use for an indentation level
    :param depth: the depth of the indentation
    :returns: the indented multiline string
    """

    line_indentation = indentation * depth

    return '\n'.join(map(lambda line: line_indentation + line if line != '' else '', s.splitlines()))

def inline_c_array(l: list) -> str:
    """
    Return the inline C or C++ literal array or struct for the elements in the list.

    :param l: the list of the array elements
    :returns: the inline array literal
    """

    return '{ ' + ', '.join(map(str, l)) + ' }'

def multiline_c_array(l: list, indentation: str, depth: int) -> str:
    """
    Return the multiline C or C++ literal array or struct for the elements in the list.

    :param l: the list of the array elements
    :param indentation: the characters to use for an indentation level
    :param depth: the depth of the indentation
    :returns: the multiline array literal
    """

    return '{\n' + indent(lines(l, ','), indentation, depth + 1) + '\n' + (indentation * depth) + '}'

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

class MapItem:
    def __init__(self, target: Target, tmx_filename):
        self._target = target
        self._tmx = TMX(tmx_filename)
        self._basename = os.path.splitext(os.path.basename(tmx_filename))[0]
        self._name = mangle(self._basename)
        self._name_upper = self._name.upper()
        descriptor = open(os.path.splitext(tmx_filename)[0] + ".json")
        descriptor = json.load(descriptor)

        self._graphics_layers = descriptor["graphics"] if "graphics" in descriptor else list()
        self._objects_layers = descriptor["objects"] if "objects" in descriptor else list()
        self._tiles_layers = descriptor["tiles"] if "tiles" in descriptor else list()

        # The list of MapObjects for the list of object layers
        self._objects_layers_objects = list(map(lambda layer_path: self._tmx.objects(layer_path), self._objects_layers))
        # This needs to be called once self._objects_layers_objects is set
        self._assign_id_and_layer_to_objects()
        # The list of MapObjects for the whole map
        #
        # This needs to be called after self._assign_id_and_layer_to_objects()
        # as otherwise it wouldn't match self._objects_layers_objects anynmore
        self._objects = sorted([map_object for layer_map_objects in self._objects_layers_objects for _, map_objects in layer_map_objects.objects().items() for map_object in map_objects], key=lambda o: o.map_id)

        self._width_in_pixels, self._height_in_pixels = self._tmx.dimensions_in_pixels()
        self._width_in_tiles, self._height_in_tiles = self._tmx.dimensions_in_tiles()
        self._tile_width, self._tile_height = self._tmx.tile_dimensions()

        self._graphics_layers_count = len(self._graphics_layers)
        self._objects_layers_count = len(self._objects_layers)
        self._tiles_layers_count = len(self._tiles_layers)

        self._objects_classes_count = len(self._objects_classes())
        self._objects_count = len(self._objects)
        self._tiles_layers_tiles_count = self._width_in_tiles * self._height_in_tiles

    def _assign_id_and_layer_to_objects(self):
        objects_classes = self._objects_classes()
        id = 0

        # Layers are already sorted, let's first sort by layers
        for layer_index, layer_map_objects in enumerate(self._objects_layers_objects):
            objects = layer_map_objects.objects()

            # Then sort by classes
            for object_class in objects_classes:
                if object_class not in objects:
                    continue

                # Then sort in whatever order the objects come in
                for object in objects[object_class]:
                    object.map_layer = layer_index
                    object.map_id = id
                    id += 1

    def _objects_classes(self):
        # Return the sorted set of map object class names in the whole map, including the "" class
        # If there are no objects layers an empty list is returned, there is not even the "" class.

        return sorted(set([map_object_class for layer_map_objects in self._objects_layers_objects for map_object_class in layer_map_objects.objects().keys()]))

    def _objects_classes_enum(self, namespace):
        # Return the list of enumeration definitions for the map object class names in the whole map, excluding the "" class

        return list(map(lambda i_and_object_class: namespace + mangle(i_and_object_class[1]).upper() + "=" + str(i_and_object_class[0]), enumerate(self._objects_classes())))[1:]

    def _object_ids_enum(self, namespace):
        # Return the list of enumeration definitions for the map object ids in the whole map, excluding the None ids

        return [namespace + mangle(map_object.id).upper() + "=" + str(map_object.map_id) for map_object in self._objects if map_object.id is not None]

    def _tile_ids_enum(self, namespace):
        # Return the list of enumeration definitions for the map tile ids in the whole map

        tile_ids = []
        for first, last, tsx in self._tmx.tilesets():
            enum_base = mangle(os.path.splitext(os.path.basename(tsx.filename()))[0]).upper()
            tile_ids.append(namespace + enum_base + "=" + str(first))
            tile_ids.append(namespace + enum_base + "_LAST=" + str(last))
        return tile_ids

    def _objects_spans(self):
        # Return a list for each layer of lists of (index,length) pairs for each
        # object of a given class in the layer, so objects can be flattened but
        # they can still be found per layer and class.

        index_lengths = []
        index = 0
        objects_classes = self._objects_classes()
        for layer in self._objects_layers_objects:
            layer_index_lengths = []
            for object_class in objects_classes:
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

        if self._graphics_layers_count == 0:
            return None

        # The size of the map, in pixels
        src_width, src_height = self._tmx.dimensions_in_pixels()
        # The size of each individual background
        bg_width, bg_height = bg_size(src_width), bg_size(src_height)

        # Compose the layers into a single background image
        gfx_im = Image.new("RGBA", (bg_width, bg_height * self._graphics_layers_count), self._tmx.background_color())
        for i, layer_path in enumerate(self._graphics_layers):
            self._tmx.compose(gfx_im, layer_path, 0, bg_height * i)

        # Make the image paletted
        gfx_im = gfx_im.quantize(256)

        return gfx_im

    def regular_bg_descriptor(self):
        # Convert the TMX into its regular background descriptor.

        _, src_height = self._tmx.dimensions_in_pixels()
        bg_height = bg_size(src_height)

        return _templates[Target.butano]['graphics'].format(bg_height=bg_height)

    def butano_header(self):
        # Convert the TMX into its C++ header.

        template = _templates[self._target]
        if self._target == Target.butano:
            graphics = "bn::regular_bg_items::" + self._name if self._graphics_layers_count > 0 else "std::monostate()"
            graphics_include = "#include <bn_regular_bg_items_" + self._name + ".h>" if self._graphics_layers_count > 0 else ""
            indentation_depth = 1
            namespace = ""
        elif self._target == Target.c:
            graphics = ""
            graphics_include = ""
            indentation_depth = 0
            namespace = "BNTMX_MAPS_" + self._name.upper() + "_"

        objects_classes = self._objects_classes_enum(namespace)
        if len(objects_classes) == 0:
            objects_classes_definition = template['objects_classes_definition_empty']
        else:
            objects_classes_literal = multiline_c_array(objects_classes, template['indentation'], indentation_depth)
            objects_classes_definition = template['objects_classes_definition_template'].format(map=self, objects_classes=objects_classes_literal)

        object_ids = self._object_ids_enum(namespace)
        if len(object_ids) == 0:
            object_ids_definition = template['object_ids_definition_empty']
        else:
            object_ids_literal = multiline_c_array(object_ids, template['indentation'], indentation_depth)
            object_ids_definition = template['object_ids_definition_template'].format(map=self, object_ids=object_ids_literal)

        tile_ids = self._tile_ids_enum(namespace)
        if len(tile_ids) == 0:
            tile_ids_definition = template['tile_ids_definition_empty']
        else:
            tile_ids_literal = multiline_c_array(tile_ids, template['indentation'], indentation_depth)
            tile_ids_definition = template['tile_ids_definition_template'].format(map=self, tile_ids=tile_ids_literal)

        return template['header_template'].format(
            graphics=graphics,
            graphics_include=graphics_include,
            map=self,
            objects_classes_definition=objects_classes_definition,
            object_ids_definition=object_ids_definition,
            tile_ids_definition=tile_ids_definition)

    def butano_source(self):
        # Convert the TMX into its C++ source.

        template = _templates[self._target]
        if self._target == Target.butano:
            indentation_depth = 1
            namespace = "bntmx::maps::" + self._name + "::"
        elif self._target == Target.c:
            indentation_depth = 0
            namespace = "BNTMX_MAPS_" + self._name.upper() + "_"

        objects_spans = multiline_c_array(map(lambda layer: multiline_c_array(map(inline_c_array, layer), template['indentation'], indentation_depth + 1), self._objects_spans()), template['indentation'], indentation_depth)
        object_to_cpp_literal = lambda o: template['map_object_template'].format(x=o.x, y=o.y, id=o.map_id if o.id is None else namespace + str(o.id))
        objects_literal = multiline_c_array(list(map(object_to_cpp_literal, self._objects)), template['indentation'], indentation_depth)

        # Get the C or C++ array literal for the given list of tiles, matching lines and columns of the map for readability.
        tiles_to_array_literal = lambda tiles: multiline_c_array([', '.join(tiles[i:i + self._width_in_tiles]) for i in range(0, len(tiles), self._width_in_tiles)], template['indentation'], indentation_depth + 1)
        # Get the C or C++ array literal of tiles for the given tiles layer path.
        tiles_layer_path_to_array_literal = lambda layer_path: tiles_to_array_literal(self._tmx.tiles(layer_path))
        # Get the C or C++ array literal of tiles layers for the given tiles layer paths.
        tiles_literal = multiline_c_array(list(map(tiles_layer_path_to_array_literal, self._tiles_layers)), template['indentation'], indentation_depth)

        if self._objects_count == 0 or self._objects_classes_count == 0 or self._objects_layers_count == 0:
            object_getter = template['object_dummy']
            objects_definition = template['objects_definition_empty']
            objects_getter_classless = template['objects_dummy']
            objects_getter_with_class = template['objects_dummy']
        else:
            object_getter = template['object_getter']
            objects_definition = template['objects_definition_template'].format(
                map=self,
                objects=objects_literal,
                objects_spans=objects_spans)
            objects_getter_classless = template['objects_getter_classless']
            objects_getter_with_class = template['objects_getter_with_class']

        if self._tiles_layers_tiles_count == 0 or self._tiles_layers_count == 0:
            tiles_definition = ''
            tiles_getter = template['tiles_dummy']
        else:
            tiles_definition = template['tiles_definition_template'].format(
                map=self,
                tiles=tiles_literal)
            tiles_getter = template['tiles_getter_template'].format(map=self)

        return template['source_template'].format(
            map=self,
            object_getter=object_getter,
            objects_definition=objects_definition,
            objects_getter_classless=objects_getter_classless,
            objects_getter_with_class=objects_getter_with_class,
            tiles=tiles_literal,
            tiles_definition=tiles_definition,
            tiles_getter=tiles_getter)

def process(target: Target, maps_dirs, build_dir):
    bntmx_dir = os.path.dirname(os.path.realpath(__file__))
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
    include = read_template(target, "bntmx.h")
    write_to_file(include_filename, include)

    for maps_dir in maps_dirs:
        for map_file in os.listdir(maps_dir):
            if map_file.endswith('.tmx') and os.path.isfile(os.path.join(maps_dir, map_file)):
                tmx_filename = os.path.join(maps_dir, map_file)
                item = MapItem(target, tmx_filename)
                map_basename = item.basename()
                map_name = item.name()

                tmx_json_filename = os.path.join(maps_dir, map_basename + ".json")
                bmp_filename = os.path.join(build_dir, "graphics", map_name + ".bmp")
                bmp_json_filename = os.path.join(build_dir, "graphics", map_name + ".json")
                header_filename = os.path.join(build_dir, "include", "bntmx_maps_" + map_name + ".h")
                if target == Target.butano:
                    source_filename = os.path.join(build_dir, "src", "bntmx_maps_" + map_name + ".cpp")
                elif target == Target.c:
                    source_filename = os.path.join(build_dir, "src", "bntmx_maps_" + map_name + ".c")

                # Don't rebuild unchanged files
                input_mtime = max(map(lambda filename : os.path.getmtime(filename) if os.path.isfile(filename) else 0, [tmx_filename, tmx_json_filename] + item.dependencies()))
                output_mtime = min(map(lambda filename : os.path.getmtime(filename) if os.path.isfile(filename) else 0, [bmp_filename, bmp_json_filename, header_filename, source_filename]))
                if input_mtime < output_mtime:
                    continue

                # Export the image
                gfx_im = item.regular_bg_image()
                if gfx_im is not None:
                    gfx_im.save(bmp_filename, "BMP")
                    # Export the graphics descriptor
                    if target == Target.butano:
                        write_to_file(bmp_json_filename, item.regular_bg_descriptor())

                # Export the C++ header
                write_to_file(header_filename, item.butano_header())

                # Export the C++ source
                write_to_file(source_filename, item.butano_source())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Compile Tiled maps into code and data usable by the game engine.')
    parser.add_argument('--target', type=Target, choices=list(Target), required=True, help='build target')
    parser.add_argument('--build', required=True, help='build directory path')
    parser.add_argument('mapsdirs', metavar='mapsdir', nargs='+',
                        help='maps directories paths')
    args = parser.parse_args()
    process(args.target, args.mapsdirs, args.build)
