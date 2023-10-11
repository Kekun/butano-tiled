"""
Copyright (c) 2023 Adrien Plazas <kekun.plazas@laposte.net>
zlib License, see LICENSE file.
"""

include = '''\
/*
 * Copyright (c) 2023 Adrien Plazas <kekun.plazas@laposte.net>
 * zlib License, see LICENSE file.
 */

#ifndef BNTMX_MAP_H
#define BNTMX_MAP_H

#include <bn_affine_bg_item.h>
#include <bn_fixed_point.h>
#include <bn_size.h>
#include <bn_span.h>
#include <bn_regular_bg_item.h>
#include <variant>

namespace bntmx
{

struct map_object
{
    bn::fixed_point position;
    uint16_t id;
};

typedef uint16_t map_tile;

class map
{

public:
    virtual constexpr ~map() {}

    /**
     * @brief Returns the dimensions of the map in pixels.
     */
    virtual constexpr bn::size dimensions_in_pixels() const = 0;

    /**
     * @brief Returns the dimensions of the map in tiles.
     */
    virtual constexpr bn::size dimensions_in_tiles() const = 0;

    /**
     * @brief Returns the dimensions of each tile of the map.
     */
    virtual constexpr bn::size tile_dimensions() const = 0;

    /**
     * @brief Returns the width of the map in pixels.
     */
    virtual constexpr int width_in_pixels() const = 0;

    /**
     * @brief Returns the height of the map in pixels.
     */
    virtual constexpr int height_in_pixels() const = 0;

    /**
     * @brief Returns the width of the map in tiles.
     */
    virtual constexpr int width_in_tiles() const = 0;

    /**
     * @brief Returns the height of the map in tiles.
     */
    virtual constexpr int height_in_tiles() const = 0;

    /**
     * @brief Returns the width of each tile of the map.
     */
    virtual constexpr int tile_width() const = 0;

    /**
     * @brief Returns the height of each tile of the map.
     */
    virtual constexpr int tile_height() const = 0;

    /**
     * @brief Returns the number of graphics layers of the map.
     */
    virtual constexpr int n_graphics_layers() const = 0;

    /**
     * @brief Returns the number of objects layers of the map.
     */
    virtual constexpr int n_objects_layers() const = 0;

    /**
     * @brief Returns the number of tiles layers of the map.
     */
    virtual constexpr int n_tiles_layers() const = 0;

    /**
     * @brief Returns the graphics layers of the map.
     */
    virtual constexpr  std::variant<std::monostate, bn::regular_bg_item, bn::affine_bg_item> graphics() const = 0;

    /**
     * @brief Returns the object with the given ID.
     * @param object_id ID of the objects.
     */
    virtual const bntmx::map_object object(int object_id) const = 0;

    /**
     * @brief Returns the classless objects of the given layer of the map.
     * @param objects_layer_index Index of the objects layer.
     */
    virtual const bn::span<const bntmx::map_object> objects(int objects_layer_index) const = 0;

    /**
     * @brief Returns the objects of the given class and layer of the map.
     * @param objects_layer_index Index of the objects layer.
     * @param objects_class Class of the objects.
     */
    virtual const bn::span<const bntmx::map_object> objects(int objects_layer_index, int objects_class) const = 0;

    /**
     * @brief Returns the tiles of the given layer of the map.
     * @param tiles_layer_index Index of the tiles layer.
     */
    virtual const bn::span<const bntmx::map_tile> tiles(int tiles_layer_index) const = 0;
};

}

#endif
'''

graphics = '''\
{{
    "type": "regular_bg",
    "bpp_mode": "bpp_4_auto",
    "height": {bg_height}
}}
'''

map_object = 'bntmx::map_object(bn::fixed_point({x}, {y}), {id})'

objects_definition_template = '''\
    // Objects are sorted by layers, then within layers they are sorted by
    // classes (with classless objects first), then within classes they are
    // sorted in the order they are found.
    // Because object IDs are assigned in the same order, they are also sorted
    // by ID.
    static constexpr bntmx::map_object _objects[] = {objects};

    // This purposefully doesn't use bn::span so we can use smaller types,
    // saving ROM space.
    static constexpr struct {{uint16_t index; uint16_t length;}} _objects_spans[{n_objects_layers}][{n_objects_classes}] = {objects_spans};
'''

objects_definition_empty = '''\
    // There is no objects in this map.
'''

object_getter = '_objects[id]'

object_dummy = 'bntmx::map_object(bn::fixed_point(0, 0), 0)'

objects_getter_classless = 'bn::span(&_objects[_objects_spans[objects_layer_index][0].index], _objects_spans[objects_layer_index][0].length)'

objects_getter_with_class = 'bn::span(&_objects[_objects_spans[objects_layer_index][objects_class].index], _objects_spans[objects_layer_index][objects_class].length)'

objects_dummy = 'bn::span<const bntmx::map_object>()'

tiles_definition = '''\
    static const bntmx::map_tile _tiles[{n_tiles_layers}][{size}] = {tiles};
'''

tiles_getter = 'bn::span(_tiles[tiles_layer_index], {size})'

tiles_dummy = 'bn::span<const bntmx::map_tile>()'

object_classes_definition_empty = '''\
    // There is no object classes in this map.
'''

object_classes_definition_template = '''\
    enum object_class {object_classes};
'''

object_ids_definition_empty = '''\
    // There are no object IDs in this map.
'''

object_ids_definition_template = '''\
    enum object_id {object_ids};
'''

tile_ids_definition_empty = '''\
    // There are no tile IDs in this map.
'''

tile_ids_definition_template = '''\
    enum tile_id {tile_ids};
'''

header = '''\
#ifndef {guard}
#define {guard}

#include "bntmx.h"

{graphics_include}

namespace bntmx::maps
{{

class {map_name} : public bntmx::map
{{

public:
{object_classes_definition}
{object_ids_definition}
{tile_ids_definition}
    constexpr {map_name}() {{}}
    constexpr ~{map_name}() {{}}

    constexpr bn::size dimensions_in_pixels() const {{ return bn::size({width_in_pixels}, {height_in_pixels}); }}
    constexpr bn::size dimensions_in_tiles() const {{ return bn::size({width_in_tiles}, {height_in_tiles}); }}
    constexpr bn::size tile_dimensions() const {{ return bn::size({tile_width}, {tile_height}); }}
    constexpr int width_in_pixels() const {{ return {width_in_pixels}; }}
    constexpr int height_in_pixels() const {{ return {height_in_pixels}; }}
    constexpr int width_in_tiles() const {{ return {width_in_tiles}; }}
    constexpr int height_in_tiles() const {{ return {height_in_tiles}; }}
    constexpr int tile_width() const {{ return {tile_width}; }}
    constexpr int tile_height() const {{ return {tile_height}; }}
    constexpr int n_graphics_layers() const {{ return {n_graphics_layers}; }}
    constexpr int n_objects_layers() const {{ return {n_objects_layers}; }}
    constexpr int n_tiles_layers() const {{ return {n_tiles_layers}; }}
    constexpr std::variant<std::monostate, bn::regular_bg_item, bn::affine_bg_item> graphics() const {{ return {graphics}; }}

    const bntmx::map_object object(int id) const;
    const bn::span<const bntmx::map_object> objects(int objects_layer_index) const;
    const bn::span<const bntmx::map_object> objects(int objects_layer_index, int objects_class) const;
    const bn::span<const bntmx::map_tile> tiles(int tiles_layer_index) const;

}};

}}

#endif
'''

source = '''\
#include "{header_filename}"

namespace bntmx::maps
{{
{objects_definition}

{tiles_definition}

    const bntmx::map_object {map_name}::object(int id) const
    {{
        BN_ASSERT(id < {n_objects}, "Invalid object ID: ", id);
        return {object_getter};
    }}

    const bn::span<const bntmx::map_object> {map_name}::objects(int objects_layer_index) const
    {{
        BN_ASSERT(objects_layer_index < {n_objects_layers}, "Invalid objects layer index: ", objects_layer_index);
        return {objects_getter_classless};
    }}

    const bn::span<const bntmx::map_object> {map_name}::objects(int objects_layer_index, int objects_class) const
    {{
        BN_ASSERT(objects_layer_index < {n_objects_layers}, "Invalid objects layer index: ", objects_layer_index);
        BN_ASSERT(objects_class < {n_objects_classes}, "Invalid objects class: ", objects_class);
        return {objects_getter_with_class};
    }}

    const bn::span<const bntmx::map_tile> {map_name}::tiles(int tiles_layer_index) const
    {{
        BN_ASSERT(tiles_layer_index < {n_tiles_layers}, "Invalid tiles layer index: ", tiles_layer_index);
        return {tiles_getter};
    }}
}}
'''

template = {
    'header_template': header,
    'map_object_template': map_object,
    'object_classes_definition_empty': object_classes_definition_empty,
    'object_classes_definition_template': object_classes_definition_template,
    'object_ids_definition_empty': object_ids_definition_empty,
    'object_ids_definition_template': object_ids_definition_template,
    'object_dummy': object_dummy,
    'object_getter': object_getter,
    'objects_definition_empty': objects_definition_empty,
    'objects_definition_template': objects_definition_template,
    'objects_dummy': objects_dummy,
    'objects_getter_classless': objects_getter_classless,
    'objects_getter_with_class': objects_getter_with_class,
    'source_template': source,
    'tile_ids_definition_empty': tile_ids_definition_empty,
    'tile_ids_definition_template': tile_ids_definition_template,
    'tiles_definition_template': tiles_definition,
    'tiles_dummy': tiles_dummy,
    'tiles_getter_template': tiles_getter
}
