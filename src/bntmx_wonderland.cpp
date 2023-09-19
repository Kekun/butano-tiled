/*
 * Copyright (c) 2023 Adrien Plazas <kekun.plazas@laposte.net>
 * zlib License, see LICENSE file.
 */

#include "bntmx_maps_wonderland.h"

#include <bn_display.h>
#include <bn_fixed.h>

namespace bntmx::maps
{
    void wonderland::init([[maybe_unused]] Scene& scene)
    {
    }

    void wonderland::enter([[maybe_unused]] Scene& scene)
    {
    }

    void wonderland::leave([[maybe_unused]] Scene& scene)
    {
    }

    void wonderland::deinit([[maybe_unused]] Scene& scene)
    {
    }

    void wonderland::interact_with_item([[maybe_unused]] Scene& scene, [[maybe_unused]] int item_id)
    {
        switch (item_id)
        {
            case OLD_LADY:
                break;
            case BOOT_SELLER:
                break;
            default:
                break;
        }
    }

    void wonderland::update_background(bn::fixed camera_x,
                                           [[maybe_unused]] bn::fixed camera_y)
    {
        for(int index = 0, limit = bn::display::height(); index < limit; ++index)
        {
            _background_horizontal_deltas[index] = camera_x * bn::fixed(0.2);
        }
        _background_horizontal_deltas_hbe.reload_deltas_ref();
    }

    void wonderland::update_foreground([[maybe_unused]] bn::fixed camera_x,
                                           [[maybe_unused]] bn::fixed camera_y)
    {
    }

    bn::optional<Teleport> wonderland::out_of_bounds(bn::fixed_point position)
    {
        if (position.x() < 0)
        {
            // FIXME To Shion's House
        }
        else if (position.x() >= width() * BNTMX_TILE_SIZE)
        {
            // FIXME To Purapril Castle Entrance
        }

        return bn::optional<Teleport>();
    }
}
