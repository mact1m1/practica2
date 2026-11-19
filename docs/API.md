# Справочник API

Описания из docstring исходного кода. Настройки и команды см. в README.

## __init__.py

Cargo dependency graph analyzer, practical work 2, variant 19.

## __main__.py

Run the command-line interface as a Python module.

## cli.py

CLI operations for the five practical-work stages.

`parser` — Build the interface; analysis settings come only from TOML.

`main` — Print configuration, returning a nonzero code for invalid input.

`execute` — Dispatch the configuration and direct-dependency stage commands.

`repository_for` — Select the real sparse index or an offline test repository.

`print_reverse` — Search the complete test graph or the real root's analyzed closure.

## config.py

Read and validate the six user settings from a TOML file.

`AppError` — An actionable configuration, repository or graph error.

`Config` — Validated analysis settings; relative paths use the TOML directory.

`read_config` — Load a complete flat TOML configuration, rejecting unknown keys.

`validate_types` — Reject implicit conversions, especially string boolean values.

`validate_values` — Check package names, exact versions and visible filter characters.

`resolve_repository` — Resolve a test path or validate an HTTP(S) sparse registry URL.

`parse_url` — Report malformed host/port syntax as a configuration error.

## graph.py

Recursive depth-first graph construction and inverse dependencies.

`build_graph` — Construct a versioned graph using recursive DFS from one/many roots.

`recursive_dfs` — Use the same recursive DFS for forward and reverse adjacency.

`reverse_dependencies` — Find all transitive dependents within an explicitly supplied graph.

`select_target` — Accept a unique name or a name@version, rejecting ambiguity.

## registry.py

Read Cargo sparse index JSON Lines over HTTP with the standard library.

`Node` — A graph vertex distinguishes versions of the same crate.

`Node.__str__` — Return a stable human-readable vertex identifier.

`Dependency` — A declared production/build dependency from an index record.

`index_path` — Derive the official Cargo index shard for a lowercase crate name.

`fetch_records` — Fetch one bounded index file; never invoke Cargo or another tool.

`Registry` — Sparse-index access with an in-memory cache per application run.

`Registry.__init__` — Use a configurable HTTP(S) sparse index base URL.

`Registry.records` — Load and validate index entries for one crate.

`Registry.exact` — Find the requested root release, even if it was yanked.

`Registry.resolve` — Choose the highest non-yanked release matching an edge.

`Registry.dependencies` — Read all normal/build edges, including optional/platform edges.

`validate_record` — Reject corrupted index metadata before constructing graph nodes.

`read_dependency` — Decode a dependency, respecting a renamed crate's package field.

## render.py

Deterministic Graphviz DOT and cycle-safe ASCII visualization.

`dot_graph` — Return valid Graphviz source with quoted versioned identifiers.

`ascii_tree` — Render a spanning tree, marking cycles and shared subgraphs.

## testrepo.py

Offline repository with uppercase Latin package names and JSON edges.

`TestRepository` — A complete finite repository; all packages use the configured version.

`TestRepository.__init__` — Read and validate an adjacency list, including referenced nodes.

`TestRepository.exact` — Resolve a test vertex or report an unknown package/version.

`TestRepository.resolve` — Resolve a test edge, whose version is fixed by the TOML file.

`TestRepository.dependencies` — Return deterministic direct edges from the test adjacency list.

`TestRepository.all_nodes` — Enumerate the complete test repository for reverse queries.

`validate_graph` — Require a nonempty mapping of uppercase names to defined nodes.

## versions.py

SemVer ordering and Cargo version requirements without dependencies.

`Version` — Semantic version; build metadata does not change precedence.

`Version.parse` — Parse an exact SemVer and reject leading zeroes.

`Version.__lt__` — Compare core numbers, then numeric/text prerelease components.

`pre_key` — Place numeric prerelease identifiers before textual identifiers.

`split_wildcard` — Separate the numeric prefix from an optional wildcard suffix.

`requirement_part` — Return an operator, padded version and specified core length.

`upper_bound` — Increment one component and zero subsequent components.

`accepts` — Evaluate one Cargo comparator, including partial comparisons.

`comparison` — Evaluate equality and ordered bounds, including partial versions.

`matches` — Match comma intersections; prereleases require an explicit core.
