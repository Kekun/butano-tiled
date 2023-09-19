/*
 * Copyright (c) 2023 Adrien Plazas <kekun.plazas@laposte.net>
 * zlib License, see LICENSE file.
 */

#ifndef MW3_TELEPORT_H
#define MW3_TELEPORT_H

#include <bn_fixed_point.h>
#include "mw3_map_id.h"

namespace mw3
{
    enum TeleportType {
        STATIC_TRANSITION,
        HORIZONTAL_TRANSITION,
        VERTICAL_TRANSITION,
    };

    class Teleport
    {
        private:
            TeleportType _type;
            MapId _map_id;
            int _spawn_index;
            // The delta is the x position of the source spawn for vertical
            // transitions, the y position of the source spawn for horizontal
            // transitions, and is irrelevant for static transitions.
            // It is used to compute the difference of position between the
            // source and destination of teleportations, so e.g. jump height is
            // preserved.
            bn::fixed _position_delta;

        public:
            constexpr Teleport(TeleportType type, MapId map_id, int spawn_index, bn::fixed position_delta) :
                _type(type),
                _map_id(map_id),
                _spawn_index(spawn_index),
                _position_delta(position_delta)
            {
            }

            constexpr Teleport(MapId map_id, int spawn_index) :
                _type(STATIC_TRANSITION),
                _map_id(map_id),
                _spawn_index(spawn_index),
                _position_delta(0)
            {
            }

            static constexpr Teleport horizontal(MapId destination_map_id, int destination_spawn_index, bn::fixed_point source_spawn_position)
            {
                return Teleport(HORIZONTAL_TRANSITION, destination_map_id, destination_spawn_index, source_spawn_position.y());
            }

            static constexpr Teleport vertical(MapId destination_map_id, int destination_spawn_index, bn::fixed_point source_spawn_position)
            {
                return Teleport(VERTICAL_TRANSITION, destination_map_id, destination_spawn_index, source_spawn_position.x());
            }

            constexpr TeleportType type()
            {
                return _type;
            }

            constexpr MapId map_id()
            {
                return _map_id;
            }

            constexpr int spawn_index()
            {
                return _spawn_index;
            }

            constexpr bn::fixed position_delta()
            {
                return _position_delta;
            }
    };
}

#endif
