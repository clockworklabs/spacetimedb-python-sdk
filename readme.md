# SpacetimeDB Python SDK

A comprehensive software development kit (SDK) designed to facilitate the creation of client applications that interact with SpaceTimeDB modules.

## Key Features

### Connection Management

The SDK simplifies the process of establishing and managing connections to the SpaceTimeDB module. Developers can establish secure WebSocket connections, enabling real-time communication with the module.

### Local Client Cache

By subscribing to a set of queries, the SDK will keep a local cache of rows that match the subscribed queries. SpacetimeDB generates python files that allow you to iterate throught these tables and filter on specific columns.

### Transaction and Row Update Events

Register for transaction and row update events.

Full documentation can be found on the [SpacetimeDB](spacetimedb.com) website.

Note: SpacetimeDB is not yet released and is only currently available to the partner program.