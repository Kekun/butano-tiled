"""
Copyright (c) 2023 Adrien Plazas <kekun.plazas@laposte.net>
zlib License, see LICENSE file.
"""

include = '''\
/*
 * Copyright (c) 2023 Adrien Plazas <kekun.plazas@laposte.net>
 * zlib License, see LICENSE file.
 */

#ifndef BNTMX_H
#define BNTMX_H

#include <stddef.h>
#include <stdint.h>

typedef struct
{
    int x;
    int y;
    uint16_t id;
} bntmx_map_object;

typedef uint16_t bntmx_map_tile;

typedef struct
{
    const void* data;
    size_t length;
} bntmx_span;

#endif
'''

map_object = '(bntmx_map_object) {{{x}, {y}, {id}}}'

objects_definition_template = '''\
/* Objects are sorted by layers, then within layers they are sorted by classes
 * (with classless objects first), then within classes they are sorted in the
 * order they are found.
 * Because object IDs are assigned in the same order, they are also sorted by
 * ID.
 */
static const bntmx_map_object _objects[] = {objects};

/* This purposefully doesn't use bntmx_span so we can use smaller types, saving
 * ROM space.
 */
static const struct {{uint16_t index; uint16_t length;}} _objects_spans[{n_objects_layers}][{n_objects_classes}] = {objects_spans};
'''

objects_definition_empty = '''\
/* There is no objects in this map. */
'''

object_getter = '_objects[id]'

object_dummy = '(bntmx_map_object) {0, 0, 0}'

objects_getter = '(bntmx_span) {&_objects[_objects_spans[objects_layer_index][objects_class].index], _objects_spans[objects_layer_index][objects_class].length}'

objects_dummy = '(bntmx_span) {NULL, 0}'

tiles_definition = '''\
static const bntmx_map_tile _tiles[{n_tiles_layers}][{size}] = {tiles};
'''

tiles_getter = '(bntmx_span) {{_tiles[tiles_layer_index], {size}}}'

tiles_dummy = '(bntmx_span) {NULL, 0}'

object_classes_definition_empty = '''\
/* There are no object classes in this map. */
'''

object_classes_definition_template = '''\
typedef enum {object_classes} bntmx_maps_{map_name}_object_class;
'''

object_ids_definition_empty = '''\
/* There are no object IDs in this map. */
'''

object_ids_definition_template = '''\
typedef enum {object_ids} bntmx_maps_{map_name}_object_id;
'''

tile_ids_definition_empty = '''\
/* There are no tile IDs in this map. */
'''

tile_ids_definition_template = '''\
typedef enum {tile_ids} bntmx_maps_{map_name}_tile_id;
'''

header = '''\
#ifndef {guard}
#define {guard}

#include "bntmx.h"

{object_classes_definition}
{object_ids_definition}
{tile_ids_definition}
#define bntmx_maps_{map_name}_height_in_pixels() ({height_in_pixels})
#define bntmx_maps_{map_name}_width_in_tiles() ({width_in_tiles})
#define bntmx_maps_{map_name}_height_in_tiles() ({height_in_tiles})
#define bntmx_maps_{map_name}_tile_width() ({tile_width})
#define bntmx_maps_{map_name}_tile_height() ({tile_height})
#define bntmx_maps_{map_name}_n_graphics_layers() ({n_graphics_layers})
#define bntmx_maps_{map_name}_n_objects_layers() ({n_objects_layers})
#define bntmx_maps_{map_name}_n_tiles_layers() ({n_tiles_layers})

const bntmx_map_object bntmx_maps_{map_name}_object(int id);
const bntmx_span bntmx_maps_{map_name}_objects(int objects_layer_index, int objects_class);
const bntmx_span bntmx_maps_{map_name}_tiles(int tiles_layer_index);

#endif
'''

source = '''\
#include "{header_filename}"

#include <assert.h>

{objects_definition}

{tiles_definition}

const bntmx_map_object bntmx_maps_{map_name}_object(int id)
{{
    assert(id < {n_objects});
    return {object_getter};
}}

const bntmx_span bntmx_maps_{map_name}_objects(int objects_layer_index, int objects_class)
{{
    assert(objects_layer_index < {n_objects_layers});
    assert(objects_class < {n_objects_classes});
    return {objects_getter_with_class};
}}

const bntmx_span bntmx_maps_{map_name}_tiles(int tiles_layer_index)
{{
    assert(tiles_layer_index < {n_tiles_layers});
    return {tiles_getter};
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
    'objects_getter_classless': objects_getter,
    'objects_getter_with_class': objects_getter,
    'source_template': source,
    'tile_ids_definition_empty': tile_ids_definition_empty,
    'tile_ids_definition_template': tile_ids_definition_template,
    'tiles_definition_template': tiles_definition,
    'tiles_dummy': tiles_dummy,
    'tiles_getter_template': tiles_getter
}
