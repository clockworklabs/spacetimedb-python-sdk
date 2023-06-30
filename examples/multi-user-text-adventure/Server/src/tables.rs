use spacetimedb::{spacetimedb, Identity, SpacetimeType, Timestamp};

#[spacetimedb(table)]
#[derive(Clone)]
pub struct Location {
    /* Location Table: Tracks the current location of a spawnable entity. */
    #[primarykey]
    #[autoinc]
    pub spawnable_entity_id: u64,

    // The room that the spawnable entity is currently in. If logged out this will be None.
    pub room_id: Option<String>,
    // The last room that the spawnable entity was in. When logging in this will be used to determine the room to spawn in.
    pub last_room_id: Option<String>,
}

#[spacetimedb(table)]
pub struct Mobile {
    /* Mobile Table: Component on all mobiles in the game. */
    #[primarykey]
    pub spawnable_entity_id: u64,

    // The name of the mobile.
    pub name: String,
}

#[spacetimedb(table)]
pub struct Player {
    /* Player Table: Component on all players in the game. */
    #[primarykey]
    pub spawnable_entity_id: u64,

    // Identity of user who owns this player.
    #[unique]
    pub identity: Identity,
}

#[derive(Clone)]
#[spacetimedb(table)]
pub struct Room {
    /* Room Table: Component on all rooms in the game. */
    #[primarykey]
    pub room_id: String,

    // The name of the room.
    pub name: String,
    // The description of the room.
    pub description: String,
    // The exits from this room.
    pub exits: Vec<Exit>,
}

#[derive(SpacetimeType, Clone)]
pub struct Exit {
    /* Exit Type: Defines an exit used in Room table. */
    // The direction of the exit.
    pub direction: String,
    // The room that the exit leads to.
    pub destination_room_id: String,
}

#[spacetimedb(table)]
pub struct RoomChat {
    /* Room Chat Table: Tracks all chat messages in a room. */
    #[primarykey]
    #[autoinc]
    pub chat_entity_id: u64,

    // The room that the chat message was sent in.
    pub room_id: String,
    // The player that sent the chat message.
    pub source_spawnable_entity_id: u64,
    // The text of the chat message.
    pub chat_text: String,
    // The timestamp of the chat message.
    pub timestamp: Timestamp,
}
