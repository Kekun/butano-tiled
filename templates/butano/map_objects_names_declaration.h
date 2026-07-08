constexpr inline bn::array<const bn::pair<uint16_t, bn::string_view>, {map_objects_item._objects_count}> {map_objects_item._name}_map_objects_names_array = {object_ids};

constexpr inline bn::span<const bn::pair<uint16_t, bn::string_view>> {map_objects_item._name}_map_objects_names_span({map_objects_item._name}_map_objects_names_array);