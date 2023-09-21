/*
 * Copyright (c) 2023 Adrien Plazas <kekun.plazas@laposte.net>
 * zlib License, see LICENSE file.
 */

#include <bn_core.h>
#include "bntmx_maps_wonderland.h"
#include "bn_regular_bg_items_wonderland_background.h"

int main()
{
    bn::core::init();

    bn::regular_bg_ptr background = bn::regular_bg_items::wonderland_background.create_bg(8, 48);
    bntmx::Map* map = new bntmx::maps::wonderland();
    bn::regular_bg_ptr layer = map->create_layer(0);

    while(true)
    {
        bn::core::update();
    }

    delete map;
}
