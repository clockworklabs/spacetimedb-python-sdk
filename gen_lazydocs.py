from lazydocs import generate_docs

# The parameters of this function correspond to the CLI options
generate_docs(
    [
        "src.spacetimedb_sdk.spacetimedb_async_client",
        "src.spacetimedb_sdk.spacetimedb_client",
    ],
    output_path="./lazydocs",
)
