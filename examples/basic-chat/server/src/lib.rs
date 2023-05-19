use spacetimedb::{spacetimedb, Identity, ReducerContext};

#[spacetimedb(table)]
pub struct User {
    #[unique]
    pub owner_id: Identity,
}

#[spacetimedb(table)]
pub struct UserChat {
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
    let owner_id = ctx.sender;
    UserChat::insert(UserChat { owner_id, chat });
}
