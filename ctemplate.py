"""
Copyright (c) 2023 Adrien Plazas <kekun.plazas@laposte.net>
zlib License, see LICENSE file.
"""

include = '''
/*
 * Copyright (c) 2023 Adrien Plazas <kekun.plazas@laposte.net>
 * zlib License, see LICENSE file.
 */

#ifndef BNTMX_MAP_H
#define BNTMX_MAP_H

typedef struct
{
    int x;
    int y;
    uint16_t id;
} bntmx_map_object;

typedef uint16_t bntmx_map_tile;

typedef struct
{
    void* data;
    size_t length;
} bntmx_span;

#endif
'''

header = '''\
#ifndef {guard}
#define {guard}

#include "bntmx.h"

typedef enum {object_classes} bntmx_maps_{map_name}_object_class;

typedef enum {object_ids} bntmx_maps_{map_name}_object_id;

typedef enum {tile_ids} bntmx_maps_{map_name}_tile_id;

#define bntmx_maps_{map_name}_width_in_pixels() ({width_in_pixels})
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

map_object = '(bntmx_map_object) {{{x}, {y}, {id}}}'

source = '''\
#include "{header_filename}"

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

static const bntmx_map_tile _tiles[{n_tiles_layers}][{size}] = {tiles};

const bntmx_map_object bntmx_maps_{map_name}_object(int id) const
{{
    assert(id < {n_objects}, "Invalid object ID: ", id);
    return _objects[id];
}}

const bntmx_span bntmx_maps_{map_name}_objects(int objects_layer_index, int objects_class) const
{{
    assert(objects_layer_index < {n_objects_layers});
    assert(objects_class < {n_objects_classes});
    return bntmx_span(&_objects[_objects_spans[objects_layer_index][objects_class].index], _objects_spans[objects_layer_index][objects_class].length);
}}

const bntmx_span bntmx_maps_{map_name}_tiles(int tiles_layer_index) const
{{
    assert(tiles_layer_index < {n_tiles_layers});
    return bntmx_span(_tiles[tiles_layer_index], {size});
}}
'''
