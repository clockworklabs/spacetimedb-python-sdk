use crate::tables::Globals;

pub fn get_globals() -> Globals {
    Globals::filter_by_id(&0).unwrap()
}

pub fn update_globals(globals: Globals) {
    Globals::update_by_id(&0, globals);
}

pub fn next_spawnable_entity_id() -> u64 {
    let mut globals = get_globals().clone();
    globals.spawnable_entity_id_counter += 1;
    let result = globals.spawnable_entity_id_counter;
    update_globals(globals);

    result
}
