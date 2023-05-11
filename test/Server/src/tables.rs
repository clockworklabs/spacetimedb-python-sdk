use spacetimedb::{spacetimedb, Identity, SpacetimeType};

#[spacetimedb(table)]
#[derive(Debug, Clone)]
pub struct Globals {
    #[unique]
    pub id: u32,

    pub spawnable_entity_id_counter: u64,
}

#[derive(SpacetimeType)]
pub enum ExitDirection {
    N,
    NW,
    W,
    SW,
    S,
    SE,
    E,
    NE,
    U,
    D,
}

#[spacetimedb(table)]
pub struct Location {
    #[unique]
    #[autoinc]
    pub spawnable_entity_id: u64,

    pub room_id: Option<String>,
}

#[spacetimedb(table)]
pub struct Mobile {
    #[unique]
    pub spawnable_entity_id: u64,

    pub name: String,
    pub description: String,
}

#[spacetimedb(table)]
pub struct Player {
    #[unique]
    pub spawnable_entity_id: u64,
    #[unique]
    pub identity: Identity,
}

#[spacetimedb(table)]
pub struct Room {
    #[unique]
    pub room_id: String,

    pub name: String,
    pub description: String,
    pub exits: Vec<Exit>,
    pub spawnable_entities: Vec<u64>,
}

#[spacetimedb(table)]
pub struct RoomChat {
    #[unique]
    pub room_id: String,

    pub source_spawnable_entity_id: u64,
    pub chat_text: String,
}

#[derive(SpacetimeType)]
pub struct Exit {
    pub direction: ExitDirection,
    pub examine: String,
    pub destination_room_id: String,
}
