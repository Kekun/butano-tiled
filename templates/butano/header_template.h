#ifndef BNTMX_MAP_ITEMS_{map._name_upper}_H
#define BNTMX_MAP_ITEMS_{map._name_upper}_H

{includes}

{data_declarations}

namespace bntmx::map_items {{
{item_declarations}

class {map._name} : public bntmx::map_item
{{

public:
    constexpr {map._name}() {{}}
    constexpr ~{map._name}() {{}}

    constexpr bn::size dimensions_in_pixels() const {{ return bn::size({map._width_in_pixels}, {map._height_in_pixels}); }}
    constexpr int width_in_pixels() const {{ return {map._width_in_pixels}; }}
    constexpr int height_in_pixels() const {{ return {map._height_in_pixels}; }}
    constexpr int regular_bg_layers_count() const {{ return {map._regular_bg_layers_count}; }}
    constexpr bn::optional<bn::regular_bg_item> regular_bg() const {{ return {regular_bg}; }}

}};

}}

#endif
