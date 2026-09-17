# Repository instructions

## Authority

- Follow repository configuration and the user's separate Python code-style and project-layout guides.
- Repository-specific behavior and public compatibility take precedence over general preferences.
- Do not invent a convention when the repository or guide already answers the question.

## Workflow

- Inspect the relevant code, tests, configuration, and current Git diff before editing.
- Keep each change scoped to the requested concern. Leave unrelated cleanup for another change.
- Preserve public behavior unless the request explicitly changes it.
- Use the Makefile targets. Run `make ci` after repository changes and report every skipped or failed check.
- Do not commit, push, merge, publish, or delete remote data without explicit approval.
- Add abstractions and quality gates only for current requirements or committed near-term work.

## Architecture

- Keep the first-party import graph acyclic. `make lint` runs Import Linter's `acyclic_siblings` contract.
- Do not hide a cycle with a local import.
- Prefer capability-oriented modules over generic horizontal layers or catchall modules.
- Keep deterministic policy in a functional core and external effects in an imperative shell.

### Extending import contracts

Extend Import Linter only when the code provides a concrete boundary:

- Add a `forbidden` contract when policy modules and concrete effect adapters or transport entry points exist. Scope the source to policy, not the entire capability.
- Add an `independence` contract when two capabilities must remain independent.
- Add a `protected` contract when callers must enter a subsystem through a deliberate public facade.
- Use `ignore_imports` only for existing violations that are scheduled for removal.
- Do not add a `layers` contract or enable exhaustive checking by default.

## Testing

- Test through the highest-fidelity stable boundary that remains deterministic and diagnostically useful.
- Use the real deterministic core. Replace only effectful or nondeterministic boundaries.
- Assert visible outcomes. Assert calls only when the interaction is part of the contract.
- Add a focused regression test before fixing a lower-level defect exposed by a broader test.
- When a second implementation satisfies the same protocol, add one shared contract-test suite for both implementations.
- Separate integration tests when databases, APIs, subprocesses, cloud services, or specialized environments make their execution contract different from unit tests.

### Mutation testing

Add Mutmut only after stable, decision-heavy policy exists and the deterministic unit suite is fast enough to run repeatedly.

- Start with explicit `only_mutate` entries for policy, parsing, normalization, state-transition, retry, or algorithm modules.
- Do not mutate adapters, framework wiring, generated code, migrations, or integration tests by default.
- Configure `source_paths` for the root package and `pytest_add_cli_args_test_selection` for the relevant tests.
- Add `pytest_add_cli_args` only to exclude an established integration marker.
- Add `also_copy` only for files the tests prove are required in Mutmut's isolated tree.
- Add a separate `make mutate` target that runs `mutmut run` and `mutmut results`.
- Keep mutation testing outside normal CI until its runtime and surviving-mutant policy are known.

### Property-based testing

Add Hypothesis when deterministic code has a broad input space and explicit invariants, such as parsers, serializers, normalization, date ranges, state transitions, retry calculations, or reversible transformations. Prefer ordinary parametrized tests when a small example table states the behavior more clearly.

### Installed-artifact verification

For a distributable package or CLI, build the wheel, install it in an isolated environment, change outside the checkout, import a concrete module, and verify that its origin is the installed environment rather than the repository root.

### Async and resource testing

When code creates tasks or owns resources, test cleanup after failure, cancellation propagation, timeout ownership, task supervision, and partial initialization as applicable.

### Performance testing

Add benchmarks only for a measured bottleneck or an explicit performance contract. Do not add benchmark scaffolding speculatively.
