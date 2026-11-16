# Демонстрации этапов

Фактический вывод, 16 ноября 2026 года. Локальные пути заменены
на `<project>` и `<temporary>` для переносимости отчёта.

## `sh run.sh examples/test.toml config`

Код возврата: 0.

stdout:

```text
package=A
repository=<project>/examples/graph.json
test_mode=True
version=1.0.0
ascii_tree=True
exclude=
```

## `sh run.sh examples/test.toml direct`

Код возврата: 0.

stdout:

```text
Direct dependencies of A@1.0.0:
B 1.0.0 [normal, optional=False, target=None]
C 1.0.0 [normal, optional=False, target=None]
```

## `sh run.sh examples/test.toml graph`

Код возврата: 0.

stdout:

```text
digraph dependencies {
  rankdir=LR;
  "A@1.0.0";
  "B@1.0.0";
  "C@1.0.0";
  "D@1.0.0";
  "A@1.0.0" -> "B@1.0.0";
  "A@1.0.0" -> "C@1.0.0";
  "B@1.0.0" -> "D@1.0.0";
  "C@1.0.0" -> "D@1.0.0";
}
```

stderr:

```text
A@1.0.0
|-- B@1.0.0
|   `-- D@1.0.0
`-- C@1.0.0
    `-- D@1.0.0 [shared]
```

## `sh run.sh examples/cycle.toml graph`

Код возврата: 0.

stdout:

```text
digraph dependencies {
  rankdir=LR;
  "A@1.0.0";
  "B@1.0.0";
  "C@1.0.0";
  "D@1.0.0";
  "A@1.0.0" -> "B@1.0.0";
  "B@1.0.0" -> "C@1.0.0";
  "C@1.0.0" -> "A@1.0.0";
  "C@1.0.0" -> "D@1.0.0";
  "D@1.0.0" -> "D@1.0.0";
}
```

stderr:

```text
A@1.0.0
`-- B@1.0.0
    `-- C@1.0.0
        |-- A@1.0.0 [cycle]
        `-- D@1.0.0
            `-- D@1.0.0 [cycle]
```

## `sh run.sh examples/filtered.toml graph`

Код возврата: 0.

stdout:

```text
digraph dependencies {
  rankdir=LR;
  "A@1.0.0";
  "B@1.0.0";
  "D@1.0.0";
  "A@1.0.0" -> "B@1.0.0";
  "B@1.0.0" -> "D@1.0.0";
}
```

stderr:

```text
A@1.0.0
`-- B@1.0.0
    `-- D@1.0.0
```

## `sh run.sh examples/test.toml reverse --target D`

Код возврата: 0.

stdout:

```text
Reverse dependencies of D@1.0.0 (scope: complete test repository):
A@1.0.0
B@1.0.0
C@1.0.0
E@1.0.0
```

## `sh run.sh examples/test.toml reverse --target Z`

Код возврата: 0.

stdout:

```text
Reverse dependencies of Z@1.0.0 (scope: complete test repository):
```

## `sh run.sh examples/cycle.toml reverse --target A`

Код возврата: 0.

stdout:

```text
Reverse dependencies of A@1.0.0 (scope: complete test repository):
B@1.0.0
C@1.0.0
```

## `sh run.sh examples/filtered.toml reverse --target D`

Код возврата: 0.

stdout:

```text
Reverse dependencies of D@1.0.0 (scope: complete test repository):
A@1.0.0
B@1.0.0
```

## `Неверный параметр package`

Код возврата: 1.

stderr:

```text
Error: package: invalid name for the selected mode
```

## `Неверный параметр repository`

Код возврата: 1.

stderr:

```text
Error: repository: test file not found: <temporary>/missing
```

## `Неверный параметр test_mode`

Код возврата: 1.

stderr:

```text
Error: test_mode: expected bool
```

## `Неверный параметр version`

Код возврата: 1.

stderr:

```text
Error: Invalid SemVer: latest
```

## `Неверный параметр ascii_tree`

Код возврата: 1.

stderr:

```text
Error: ascii_tree: expected bool
```

## `Неверный параметр exclude`

Код возврата: 1.

stderr:

```text
Error: exclude: expected str
```
