/*
 * Copyright (c) 2023 Adrien Plazas <kekun.plazas@laposte.net>
 * zlib License, see LICENSE file.
 */

#include <bn_camera_ptr.h>
#include <bn_core.h>
#include <bn_display.h>
#include "bn_regular_bg_items_wonderland_background.h"
#include "bn_regular_bg_ptr.h"
#include "bntmx_maps_wonderland.h"

int main()
{
    bn::core::init();

    bn::camera_ptr camera = bn::camera_ptr::create(0, 0);
    bntmx::map* map = new bntmx::maps::wonderland();

    bn::regular_bg_ptr background = bn::regular_bg_items::wonderland_background.create_bg(0, 0);
    bn::regular_bg_ptr layer = std::get<bn::regular_bg_item>(map->graphics()).create_bg(0, 0, 0);

    background.set_camera(camera);
    layer.set_camera(camera);

    camera.set_x(-(map->width_in_pixels() - bn::display::width()) / 2);
    camera.set_y(-(map->height_in_pixels() - bn::display::height()) / 2);

    while(true)
    {
        bn::core::update();
    }

    delete map;
}
