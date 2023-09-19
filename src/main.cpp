/*
 * Copyright (c) 2023 Adrien Plazas <kekun.plazas@laposte.net>
 * zlib License, see LICENSE file.
 */

#include <bn_core.h>
#include "bntmx_maps_wonderland.h"

int main()
{
    bn::core::init();

    bntmx::Map* map = new bntmx::maps::wonderland();
    bn::regular_bg_ptr layer = map->create_layer(0);
    map->background().set_priority(3);
    layer.set_priority(2);
    map->foreground().set_priority(1);

    while(true)
    {
        bn::core::update();
    }

    delete map;
}
