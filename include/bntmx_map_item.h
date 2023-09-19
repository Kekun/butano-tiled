/*
 * Copyright (c) 2023 Adrien Plazas <kekun.plazas@laposte.net>
 * zlib License, see LICENSE file.
 */

#ifndef BNTMX_MAP_ITEM_H
#define BNTMX_MAP_ITEM_H

#include <bn_fixed_point.h>

namespace bntmx
{
    struct MapItem
    {
        bn::fixed_point position;
        int id;
    };
}

#endif
