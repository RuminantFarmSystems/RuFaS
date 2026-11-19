---
description: Query the graphify dependency graph — BFS traversal, shortest path, or node explanation
argument-hint: "query|path|explain [args]"
allowed-tools: Bash(graphify:*)
---

$ARGUMENTS

## When to use graphify instead of grep/read

Prefer `graphify query/path/explain` over a series of grep + read calls when:

- **Structural question**: "how does X connect to Y?" — graphify traverses the
  pre-built graph in milliseconds vs. multiple reads of the large modules.
- **Impact analysis on a god node**: `OutputManager`, `GeneralConstants`,
  `RufasTime`, `MeasurementUnits`, `InputManager` — these have hundreds of edges;
  grep misses inferred/semantic edges.
- **Cross-subsystem dependency chain**: tracing how the simulation engine reaches
  a manure connection, or how the animal subsystem touches the EEE layer.
- **Shortest path between two symbols**: find the route without guessing
  intermediate modules.

For single-file reads or known symbol locations, use Read/Grep directly —
graphify adds overhead for trivial lookups.

## Commands

### graphify query — BFS traversal from a starting node

```bash
graphify query "SimulationEngine"
graphify query "InputManager" --depth 2
graphify query "OutputManager"
```

Returns all nodes reachable from the starting symbol, with edge types and
confidence scores. `--depth N` limits traversal depth (default: 3).

### graphify path — shortest path between two nodes

```bash
graphify path "TaskManager" "OutputManager"
graphify path "SimulationEngine" "HerdManager"
graphify path "InputManager" "GeneralConstants"
```

Returns the shortest dependency chain between two symbols, showing each hop and
edge type.

### graphify explain — plain-language summary of a node and its neighbors

```bash
graphify explain "SimulationEngine"
graphify explain "OutputManager"
graphify explain "RufasTime"
```

Returns what the node does, its direct callers, and its direct dependencies —
without opening the (often very large) source files.

## God nodes (most connected — handle with care)

Top nodes by edge count (from `graphify-out/GRAPH_REPORT.md`):

| Node                     | Edges | Role                                          |
| ------------------------ | ----- | --------------------------------------------- |
| `OutputManager`          | ~1031 | log/data pools, verbosity, dumps              |
| `GeneralConstants`       | ~892  | shared model constants                        |
| `RufasTime`              | ~805  | simulation calendar/time                      |
| `MeasurementUnits`       | ~704  | unit handling (`units.py`)                    |
| `Utility`                | ~583  | broad helpers (`util.py`)                     |
| `InputManager`           | ~507  | input JSON tree → model objects               |
| `AnimalType`             | ~471  | animal subsystem core type                    |
| `SoilData`               | ~400  | soil model data                               |

Any change to a god node has wide blast radius — run `graphify query "<node>"`
before modifying.

## RuFaS-specific examples

```bash
# How does the engine reach the manure subsystem?
graphify path "SimulationEngine" "ManureManager"

# What depends on GeneralConstants?
graphify query "GeneralConstants" --depth 1

# Understand the OutputManager abstraction without reading 127 KB
graphify explain "OutputManager"
```

## Graph freshness

- AST graph is rebuilt with `GRAPHIFY_NO_TIPS=1 graphify update .` (free, no API).
- CI auto-updates `graphify-out/GRAPH_REPORT.md` on push to `dev-msf`
  (`.github/workflows/update-graphify.yml`).
- Fresh clone: run `graphify update .` to populate `graphify-out/graph.json`
  (gitignored) before using these commands.
- Optional semantic pass (richer edges, uses API tokens): `/graphify` skill.
