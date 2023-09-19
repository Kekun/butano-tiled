/*
 * Copyright (c) 2023 Adrien Plazas <kekun.plazas@laposte.net>
 * zlib License, see LICENSE file.
 */

#ifndef MW3_MAP_ITEM_H
#define MW3_MAP_ITEM_H

#include <bn_fixed_point.h>

namespace mw3
{
    struct MapItem
    {
        bn::fixed_point position;
        int id;
    };
}

#endif
