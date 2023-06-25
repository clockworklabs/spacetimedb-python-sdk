use spacetimedb::{spacetimedb, Identity, ReducerContext};

#[spacetimedb(table)]
pub struct GlobalTable {
    #[primarykey]
    pub version: u64,

    pub message_of_the_day: String,
}

#[spacetimedb(table)]
pub struct User {
    #[primarykey]
    pub owner_id: Identity,
}

#[spacetimedb(table)]
pub struct UserChat {
    #[autoinc]
    #[primarykey]
    pub chat_entity_id: u64,

    pub owner_id: Identity,
    pub chat: String,
}

#[spacetimedb(init)]
pub fn init() {
    GlobalTable::insert(GlobalTable {
        version: 0,
        message_of_the_day: "Welcome to my chat server!".to_string(),
    })
    .unwrap();
}

#[spacetimedb(reducer)]
pub fn create_user(ctx: ReducerContext) {
    User::insert(User {
        owner_id: ctx.sender,
    })
    .unwrap();
}

#[spacetimedb(reducer)]
pub fn user_chat(ctx: ReducerContext, chat: String) {
    log::info!("user_chat {}", chat);
    let owner_id = ctx.sender;
    UserChat::insert(UserChat {
        chat_entity_id: 0,
        owner_id,
        chat,
    })
    .unwrap();
}

#[spacetimedb(reducer)]
pub fn update_motd(_ctx: ReducerContext, motd: String) {
    let mut global = GlobalTable::filter_by_version(&0).unwrap();
    global.message_of_the_day = motd;
    GlobalTable::update_by_version(&0, global);
}
