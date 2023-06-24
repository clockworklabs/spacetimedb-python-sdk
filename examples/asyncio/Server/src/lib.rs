use spacetimedb::{spacetimedb, Identity, ReducerContext};

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
