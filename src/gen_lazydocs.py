import traceback
from lazydocs import generate_docs

try:
    # The parameters of this function correspond to the CLI options
    generate_docs(
        [
            "spacetimedb_sdk.spacetimedb_async_client",
            "spacetimedb_sdk.spacetimedb_client",
        ],
        output_path="../lazydocs",
        remove_package_prefix=True,
    )
except Exception as e:
    print(f"Exception occurred: {e}")
    traceback.print_exc()
