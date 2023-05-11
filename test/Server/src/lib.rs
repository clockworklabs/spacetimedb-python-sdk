pub mod helpers;
pub mod tables;

use helpers::next_spawnable_entity_id;
use spacetimedb::{rt::log, spacetimedb, ReducerContext};
use tables::{Exit, ExitDirection, Globals, Location, Mobile, Player, Room, RoomChat};

#[spacetimedb(init)]
pub fn initialize() {
    Globals::insert(Globals {
        id: 0,
        spawnable_entity_id_counter: 0,
    });

    Room::insert(Room {
        room_id: "start".into(),

        name: "Clockwork Labs Lobby".into(),
        description: "This is a room.".into(),
        exits: vec![Exit {
            direction: ExitDirection::NE,
            examine: "An exit".into(),
            destination_room_id: "start".into(),
        }],
        spawnable_entities: Vec::new(),
    });
}

#[spacetimedb(reducer)]
pub fn create_player(ctx: ReducerContext, name: String, description: String) -> Result<(), String> {
    if Player::filter_by_identity(&ctx.sender).is_some() {
        return Err("Player already exists".into());
    }

    let spawnable_entity_id = next_spawnable_entity_id();

    Location::insert(Location {
        spawnable_entity_id: spawnable_entity_id,
        room_id: Some("start".into()),
    });
    Mobile::insert(Mobile {
        spawnable_entity_id: spawnable_entity_id,
        name,
        description,
    });
    Player::insert(Player {
        spawnable_entity_id: spawnable_entity_id,
        identity: ctx.sender,
    });

    Ok(())
}

#[spacetimedb(reducer)]
pub fn say(
    _ctx: ReducerContext,
    source_spawnable_entity_id: u64,
    chat_text: String,
) -> Result<(), String> {
    if let Some(location) = Location::filter_by_spawnable_entity_id(&source_spawnable_entity_id) {
        if location.room_id.is_some() {
            RoomChat::insert(RoomChat {
                room_id: location.room_id.unwrap(),
                source_spawnable_entity_id,
                chat_text,
            });
        } else {
            return Err("No location found.".into());
        }
    } else {
        return Err("No mobile found.".into());
    }

    Ok(())
}
