/*
 * Copyright (c) 2023 Adrien Plazas <kekun.plazas@laposte.net>
 * zlib License, see LICENSE file.
 */

#include <stdio.h>

typedef enum {
    wonderland_object_class_door,
    wonderland_object_class_spawn,
} WonderlandObjectClass;

#include "bntmx_map_items_empty.h"
#include "bntmx_map_items_overworld.h"
#include "bntmx_map_items_wonderland.h"

#define N_ELEMENTS(array) (sizeof (array) / sizeof ((array)[0]))

void wonderland_scene()
{
    for (int i = 0; i < N_ELEMENTS(bntmx_map_items_wonderland_map_objects_class_names_array); i++) {
        printf("wonderland.tmx class id %d is named %s\n", bntmx_map_items_wonderland_map_objects_class_names_array[i].id, bntmx_map_items_wonderland_map_objects_class_names_array[i].value);
    }

    for (int i = 0; i < N_ELEMENTS(bntmx_map_items_wonderland_map_objects_class_enum_array); i++) {
        printf("wonderland.tmx class id %d matches WonderlandObjectClass value %d\n", bntmx_map_items_wonderland_map_objects_class_enum_array[i].id, bntmx_map_items_wonderland_map_objects_class_enum_array[i].value);
    }

    const bntmx_span span = bntmx_map_objects_item_objects(&bntmx_map_items_wonderland_map_objects, 0, 0);
    for (const bntmx_map_object* map_object = span.begin; map_object != span.end; map_object++) {
        printf("wonderland.tmx layer 0 object id %d is at position %d-%d\n", map_object->id, map_object->position.x, map_object->position.y);
    }
}

int main()
{
    wonderland_scene();

    return 0;
}
