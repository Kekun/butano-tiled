/*
 * Copyright (c) 2026 Adrien Plazas <kekun.plazas@laposte.net>
 * zlib License, see LICENSE file.
 */

#ifndef BNTMX_H
#define BNTMX_H

#include <stdint.h>

typedef int bntmx_fixed;

typedef struct
{
    bntmx_fixed x;
    bntmx_fixed y;
} bntmx_fixed_point;

typedef struct
{
    int x;
    int y;
} bntmx_point;

typedef struct
{
    int width;
    int height;
} bntmx_size;

typedef struct
{
    const void* begin;
    const void* end;
} bntmx_span;

typedef const char* bntmx_string_view;

typedef struct
{
    uint16_t index;
    uint16_t length;
} bntmx_slice;

typedef uint16_t bntmx_map_tile;

typedef struct
{
    bntmx_fixed_point position;
    uint16_t id;
} bntmx_map_object;

typedef uint16_t bntmx_map_object_class;

typedef struct
{
    const bntmx_map_tile* tiles_ptr;
    bntmx_size dimensions;
    int layers_count;
} bntmx_map_tiles_item;

typedef struct
{
    bntmx_map_tiles_item tiles_item;
    bntmx_size tile_dimensions;
} bntmx_orthogonal_map_item;

typedef struct
{
    const bntmx_map_object* objects;
    int layers_count;
    int objects_count;
    const bntmx_slice* object_slices;
    int classes_count;
} bntmx_map_objects_item;

bntmx_size bntmx_map_tiles_item_dimensions(const bntmx_map_tiles_item* this);
int bntmx_map_tiles_item_width(const bntmx_map_tiles_item* this);
int bntmx_map_tiles_item_height(const bntmx_map_tiles_item* this);
int bntmx_map_tiles_item_layers_count(const bntmx_map_tiles_item* this);
const bntmx_map_tile* bntmx_map_tiles_item_tiles(const bntmx_map_tiles_item* this, int layer_index);
int bntmx_map_tiles_item_tile_index(const bntmx_map_tiles_item* this, int tile_x, int tile_y);
bntmx_map_tile bntmx_map_tiles_item_tile(const bntmx_map_tiles_item* this, int layer_index, int tile_x, int tile_y);

bntmx_size bntmx_orthogonal_map_item_dimensions(const bntmx_orthogonal_map_item* this);
int bntmx_orthogonal_map_item_width(const bntmx_orthogonal_map_item* this);
int bntmx_orthogonal_map_item_height(const bntmx_orthogonal_map_item* this);
bntmx_size bntmx_orthogonal_map_item_tile_dimensions(const bntmx_orthogonal_map_item* this);
int bntmx_orthogonal_map_item_tile_width(const bntmx_orthogonal_map_item* this);
int bntmx_orthogonal_map_item_tile_height(const bntmx_orthogonal_map_item* this);
const bntmx_map_tiles_item* bntmx_orthogonal_map_item_tiles_item(const bntmx_orthogonal_map_item* this);
bntmx_point bntmx_orthogonal_map_item_tile_position(const bntmx_orthogonal_map_item* this, int x, int y);
bntmx_map_tile bntmx_orthogonal_map_item_tile(const bntmx_orthogonal_map_item* this, int layer_index, int x, int y);

int bntmx_map_objects_item_layers_count(const bntmx_map_objects_item* this);
bntmx_map_object bntmx_map_objects_item_object(const bntmx_map_objects_item* this, int object_id);
bntmx_span bntmx_map_objects_item_objects(const bntmx_map_objects_item* this, int objects_layer_index, bntmx_map_object_class objects_class);

#endif
