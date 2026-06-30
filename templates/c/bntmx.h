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
