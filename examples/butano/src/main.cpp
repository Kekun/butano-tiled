/*
 * Copyright (c) 2023 Adrien Plazas <kekun.plazas@laposte.net>
 * zlib License, see LICENSE file.
 */

#include <bn_camera_ptr.h>
#include <bn_core.h>
#include <bn_display.h>
#include <bn_keypad.h>
#include <bn_log.h>
#include <bn_regular_bg_ptr.h>

enum class WonderlandObjectClass {
    door,
    spawn,
};

#include "bn_regular_bg_items_wonderland_background.h"
#include "bntmx_map_items_empty.h"
#include "bntmx_map_items_wonderland.h"

void wonderland_scene()
{
    for (auto object_class: bntmx::map_items::wonderland_map_objects_class_names_span) {
        BN_LOG("wonderland.tmx class id ", std::get<0>(object_class), " is named ", std::get<1>(object_class));
    }

    for (auto object_class: bntmx::map_items::wonderland_map_objects_class_enum_span) {
        BN_LOG("wonderland.tmx class id ", std::get<0>(object_class), " matches WonderlandObjectClass value ", static_cast<int>(std::get<1>(object_class)));
    }

    for (auto map_object: bntmx::map_items::wonderland_map_objects.objects(0)) {
        BN_LOG("wonderland.tmx layer 0 object id ", map_object.id, " is at position ", map_object.position.x(), "-", map_object.position.y());
    }

    bn::camera_ptr camera = bn::camera_ptr::create(0, 0);

    bn::regular_bg_ptr background = bn::regular_bg_items::wonderland_background.create_bg(0, 0);
    bn::regular_bg_ptr foreground = bntmx::map_items::wonderland_regular_bg.create_bg(0, 0, 0);
    const bntmx::orthogonal_map_item& layout = bntmx::map_items::wonderland_orthogonal_map;

    background.set_camera(camera);
    foreground.set_camera(camera);

    camera.set_x(-(layout.width() - bn::display::width()) / 2);
    camera.set_y(-(layout.height() - bn::display::height()) / 2);

    while(!bn::keypad::start_pressed())
    {
        bn::core::update();
    }
}

int main()
{
    bn::core::init();

    while(true)
    {
        wonderland_scene();
        bn::core::update();
    }
}
