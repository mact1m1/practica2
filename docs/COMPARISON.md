# Сравнение с cargo tree

Фактическая проверка выполнена 16 ноября 2026 года.
Cargo: `cargo 1.89.0 (c24e10642 2025-06-23)`.
Анализатор самостоятельно читает `https://index.crates.io`.
Cargo не вызывается из `src/` и нужен только для сравнения.

## Методика

Для каждого пакета создан временный Rust-проект с единственной
зависимостью, закреплённой на точной версии (`=версия`). Копии манифестов,
полный DOT, ASCII и штатный вывод сохранены в [examples](examples/).
В штатном выводе заменён только локальный путь временного проекта.

```sh
sh run.sh examples/itoa.toml graph > itoa.dot 2> itoa.tree.txt
cargo tree --manifest-path /tmp/compare/Cargo.toml \
  --edges normal,build --target all --charset ascii --color never
```

Для повторения создайте отдельную папку, скопируйте туда
`examples/itoa.Cargo.toml` из этой директории как `Cargo.toml`
и создайте пустой `lib.rs`. Повторите для остальных двух манифестов.
Cargo использует стандартные features зависимостей. `--target all`
включает все платформы. Корень `compare-*` является тестовой обёрткой
и в число вершин сравниваемого пакета не включён.

## Результаты

| Точный корень | Анализатор: вершины / рёбра | Cargo: вершины / рёбра |
| --- | --- | --- |
| itoa 1.0.15 | 6 / 9 | 1 / 0 |
| crc32fast 1.4.2 | 3 / 2 | 2 / 1 |
| miniz_oxide 0.8.9 | 12 / 17 | 2 / 1 |

### itoa

[DOT](examples/itoa.dot), [ASCII](examples/itoa.tree.txt),
[cargo tree](examples/itoa.cargo-tree.txt).
В штатном дереве пакет не имеет активных зависимостей.
Анализатор дополнительно показывает объявленную optional-зависимость
`no-panic` и её связи с `proc-macro2`, `quote`, `syn`, `unicode-ident`.

### crc32fast

[DOT](examples/crc32fast.dot), [ASCII](examples/crc32fast.tree.txt),
[cargo tree](examples/crc32fast.cargo-tree.txt).
Оба инструмента находят `cfg-if 1.0.5`. Анализатор также показывает
optional-зависимость `rustc-std-workspace-core` у `cfg-if`.
Эта зависимость нужна специальному режиму сборки стандартной библиотеки,
а при обычной сборке Cargo не активируется.

### miniz_oxide

[DOT](examples/miniz_oxide.dot), [ASCII](examples/miniz_oxide.tree.txt),
[cargo tree](examples/miniz_oxide.cargo-tree.txt).
Оба инструмента находят `adler2 2.0.1`. Анализатор дополнительно
показывает optional-пакеты `simd-adler32`, `serde`, компоненты
`rustc-std-workspace-*` и их транзитивные зависимости.

## Причины и границы расхождений

Программа показывает граф **объявленных normal/build зависимостей**,
включая optional и все платформы. Она не активирует Cargo features.
`cargo tree` показывает зависимости, активированные для конкретной
сборки. Поэтому дополнительные ветви в приведённых примерах ожидаемы.
Оба инструмента исключают dev-рёбра при указанных параметрах сравнения.

Анализатор независимо выбирает максимальную неотозванную версию для
каждого требования. Cargo дополнительно унифицирует совместимые версии,
учитывает features, Cargo.lock, ограничения Rust и другие условия.
Доступные версии в индексе меняются: повторный запуск позже может дать
другие транзитивные версии. Сохранённые текстовые результаты фиксируют
фактическое сравнение, а не гарантируют неизменность реестра.

Источники описания форматов и поведения:

- [Формат Cargo registry index](https://doc.rust-lang.org/cargo/reference/registry-index.html).
- [Семантика требований версий](https://doc.rust-lang.org/cargo/reference/specifying-dependencies.html).
- [Параметры cargo tree](https://doc.rust-lang.org/cargo/commands/cargo-tree.html).
