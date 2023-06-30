pub mod tables;

use std::time::Duration;

use spacetimedb::{schedule, spacetimedb, ReducerContext};
use tables::{Exit, Location, Mobile, Player, Room, RoomChat};

#[spacetimedb(init)]
pub fn initialize() {
    /* init is called when a module is initially published and when --clear-database is used

      This is a good place to initialize the database with default values.
    */

    // Create the default rooms.
    Room::insert(Room {
        room_id: "start".into(),

        name: "Nexus".into(),
        description: "    You find yourself in the Nexus, a vast and awe-inspiring chamber that serves as the central hub connecting all the worlds that have been created. The room is adorned with towering marble pillars, their intricate carvings depicting the unique essence of each realm they represent. Sunlight streams through stained glass windows, casting vibrant hues across the polished stone floor, illuminating the boundless possibilities that lie beyond.\n\n        As you stand in the center, you can sense the energy pulsating through the air, a palpable hum that resonates with the whispers of countless adventures waiting to be embarked upon. A network of shimmering portals surrounds you, each one a gateway to a different realm. The soft, ethereal glow emanating from these gateways beckons you to step closer, inviting you to explore the realms that lie just beyond their threshold. With every breath, the Nexus buzzes with the promise of uncharted territories, calling upon your courage to traverse the unknown and make your mark upon the tapestry of this boundless multiverse.".into(),
        exits: vec![Exit {
            direction: "n".into(),
            destination_room_id: "office1".into(),
        }],
    }).unwrap();

    Room::insert(Room {
        room_id: "office1".into(),

        name: "3Blave's Code Cave".into(),
        description: "    You find yourself in a mysterious and unconventional office space that belongs to an eccentric programmer. Within its walls, a vibrant blend of chaos and creativity unfolds. \n    Overflowing with bizarre decorations, quirky gadgets, and walls adorned with enigmatic algorithms, the Code Cave serves as the sanctuary where the Mad Coder's genius flourishes amidst the madness, producing innovative and unconventional software solutions that defy traditional norms.".into(),
        exits: vec![Exit {
            direction: "s".into(),
            destination_room_id: "start".into(),
        }],
    }).unwrap();
}

#[spacetimedb(connect)]
pub fn connect(ctx: ReducerContext) {
    /* connect is called when a client connects to the server.

      This is a good place to initialize the client's state.
    */

    // find a player that matches this user's identity
    if let Some(player) = Player::filter_by_identity(&ctx.sender) {
        // we schedule the sign_in reducer so all clients get an event when someone connects.
        schedule!(
            Duration::from_millis(100),
            sign_in(_, player.spawnable_entity_id)
        );
    }
}

#[spacetimedb(disconnect)]
pub fn disconnect(ctx: ReducerContext) {
    /* disconnect is called when a client disconnects from the server.

      This is a good place to clean up the client's state.
    */

    // find a player that matches this user's identity
    if let Some(player) = Player::filter_by_identity(&ctx.sender) {
        // we schedule the sign_out reducer so all clients get an event when someone disconnects.
        schedule!(
            Duration::from_millis(100),
            sign_out(_, player.spawnable_entity_id)
        );
    }
}

#[spacetimedb(reducer)]
pub fn sign_in(_ctx: ReducerContext, player_spawnable_entity_id: u64) -> Result<(), String> {
    /* sign in reducer: update the player's location to their last known location */

    // get this player's location component so we can update it
    let mut location = Location::filter_by_spawnable_entity_id(&player_spawnable_entity_id)
        .unwrap()
        .clone();

    // set the player's location to the last room they were in
    location.room_id = location.last_room_id.clone();
    // clear the last room they were in
    location.last_room_id = None;
    Location::update_by_spawnable_entity_id(&player_spawnable_entity_id, location);

    Ok(())
}

#[spacetimedb(reducer)]
pub fn sign_out(_ctx: ReducerContext, player_spawnable_entity_id: u64) -> Result<(), String> {
    /* sign in reducer: update the player's location room to None */

    // get this player's location component so we can update it
    let mut location = Location::filter_by_spawnable_entity_id(&player_spawnable_entity_id)
        .unwrap()
        .clone();
    location.last_room_id = location.room_id.clone();
    location.room_id = None;
    Location::update_by_spawnable_entity_id(&player_spawnable_entity_id, location);

    Ok(())
}

#[spacetimedb(reducer)]
pub fn create_player(ctx: ReducerContext, name: String) -> Result<(), String> {
    /* create player reducer: create a player spawnable entity for the user */

    // check if a player already exists for this user
    if Player::filter_by_identity(&ctx.sender).is_some() {
        return Err("Player already exists".into());
    }

    // create a new player spawnable entity, this generates the entity id by using the autoinc feature
    let result = Location::insert(Location {
        spawnable_entity_id: 0,
        room_id: Some("start".into()),
        last_room_id: None,
    })
    .unwrap();

    // get the spawnable entity id that was generated
    let spawnable_entity_id = result.spawnable_entity_id;

    // create the player and mobile components, the owner identity is the identity of the sender in the reducer context
    Mobile::insert(Mobile {
        spawnable_entity_id: spawnable_entity_id,
        name,
    })
    .unwrap();
    Player::insert(Player {
        spawnable_entity_id: spawnable_entity_id,
        identity: ctx.sender,
    })
    .unwrap();

    Ok(())
}

#[spacetimedb(reducer)]
pub fn say(
    ctx: ReducerContext,
    source_spawnable_entity_id: u64,
    chat_text: String,
) -> Result<(), String> {
    /* say reducer: create a room chat entry for the message */

    // get the location of the player
    if let Some(location) = Location::filter_by_spawnable_entity_id(&source_spawnable_entity_id) {
        // if the player is in a room, create a room chat entry
        if location.room_id.is_some() {
            RoomChat::insert(RoomChat {
                chat_entity_id: 0,

                room_id: location.room_id.unwrap(),
                source_spawnable_entity_id,
                chat_text,

                timestamp: ctx.timestamp,
            })
            .unwrap();
        } else {
            return Err("No location found.".into());
        }
    } else {
        return Err("No mobile found.".into());
    }

    Ok(())
}

#[spacetimedb(reducer)]
pub fn go(
    _ctx: ReducerContext,
    source_spawnable_entity_id: u64,
    exit_direction: String,
) -> Result<(), String> {
    /* go reducer: move the player to a new room */

    // get the location of the player
    if let Some(location) = Location::filter_by_spawnable_entity_id(&source_spawnable_entity_id) {
        // create a mutable reference to the location so we can update it
        let mut new_location = location.clone();
        // if the player room location is not None
        if let Some(room_id) = location.room_id.clone() {
            // get the room entry
            let room = Room::filter_by_room_id(&room_id).unwrap();
            // find the exit that matches the exit direction
            let exit = room.exits.iter().find(|e| e.direction == exit_direction);
            // if the exit exists, update the player's location
            if let Some(exit) = exit {
                // set the player's last room id to the current room id
                new_location.last_room_id = location.room_id.clone();
                // set the player's room id to the destination room id
                new_location.room_id = Some(exit.destination_room_id.clone());
                // update the player's location
                Location::update_by_spawnable_entity_id(&source_spawnable_entity_id, new_location);
            } else {
                return Err("Invalid exit.".into());
            }
        } else {
            return Err("No location found.".into());
        }
    } else {
        return Err("No mobile found.".into());
    }

    Ok(())
}
