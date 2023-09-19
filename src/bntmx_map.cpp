/*
 * Copyright (c) 2023 Adrien Plazas <kekun.plazas@laposte.net>
 * zlib License, see LICENSE file.
 */

#include "bntmx_map.h"

#include "bntmx_maps_wonderland.h"

namespace bntmx
{
    Map* create_map(MapId map_id)
    {
        switch(map_id)
        {
            case WONDERLAND:
                return new bntmx::maps::wonderland();
            default:
                BN_ASSERT(false, "Invalid map id: ", map_id);
                return nullptr;
        }
    }
}
