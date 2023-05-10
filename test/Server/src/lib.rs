use spacetimedb::{rt::log, spacetimedb, SpacetimeType};

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
pub struct Mobile {
    name: String,
    description: String,
}

#[spacetimedb(table)]
pub struct Room {
    name: String,
    description: String,
    exits: Vec<Exit>,
    mob: Option<Mobile>,
}

#[derive(SpacetimeType)]
pub struct Exit {
    direction: ExitDirection,
    examine: String,
}

#[spacetimedb(reducer)]
pub fn add(name: String) {
    Mobile::insert(Mobile {
        name,
        description: "A mobile.".into(),
    });
    Room::insert(Room {
        name: "A room".into(),
        description: "This is a room.".into(),
        exits: vec![Exit {
            direction: ExitDirection::N,
            examine: "An exit".into(),
        }],
        mob: None,
    });
}

#[spacetimedb(reducer)]
pub fn say_hello() {
    for mobile in Mobile::iter() {
        log::info!("Hello, {}!", mobile.name);
    }
    log::info!("Hello, World!");
}
