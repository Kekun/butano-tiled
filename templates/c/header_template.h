#ifndef BNTMX_MAP_ITEMS_{map._name_upper}_H
#define BNTMX_MAP_ITEMS_{map._name_upper}_H

{includes}

{data_declarations}

{item_declarations}

{objects_classes_definition}
{object_ids_definition}
{tile_ids_definition}
#define bntmx_map_items_{map._name}_height_in_pixels() ({map._height_in_pixels})
#define bntmx_map_items_{map._name}_width_in_tiles() ({map._width_in_tiles})
#define bntmx_map_items_{map._name}_height_in_tiles() ({map._height_in_tiles})
#define bntmx_map_items_{map._name}_tile_width() ({map._tile_width})
#define bntmx_map_items_{map._name}_tile_height() ({map._tile_height})
#define bntmx_map_items_{map._name}_regular_bg_layers_count() ({map._regular_bg_layers_count})
#define bntmx_map_items_{map._name}_objects_layers_count() ({map._objects_layers_count})
#define bntmx_map_items_{map._name}_tiles_layers_count() ({map._tiles_layers_count})

const bntmx_map_object bntmx_map_items_{map._name}_object(int id);
const bntmx_span bntmx_map_items_{map._name}_objects(int objects_layer_index, int objects_class);
const bntmx_span bntmx_map_items_{map._name}_tiles(int tiles_layer_index);

#endif
