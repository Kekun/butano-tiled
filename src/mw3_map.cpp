/*
 * Copyright (c) 2023 Adrien Plazas <kekun.plazas@laposte.net>
 * zlib License, see LICENSE file.
 */

#include "mw3_map.h"

#include "mw3_maps_wonderland.h"

namespace mw3
{
    Map* create_map(MapId map_id)
    {
        switch(map_id)
        {
            case WONDERLAND:
                return new mw3::maps::wonderland();
            default:
                BN_ASSERT(false, "Invalid map id: ", map_id);
                return nullptr;
        }
    }
}
