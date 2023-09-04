<style>code { color: #ee6666 } </style>
# Changelog

## 2.0.0 (2023/09/03)
------------------
- Major update
- Completely overhauled file reading to use dictionaries instead of strings
- Added `getFileDict()`
- Added 3 new utility functions: `searchEvents()`, `removeEvents()` and `replaceField()`
- `getAngles()`, `setAngles()` and all event functions are now deprecated
- Updated documentation
- README and CHANGELOG now uses markdown

## 0.1.1 (2023/07/17)
------------------
- Minor bugfixes
- Fixed encoding incompatibility
- Fixed output string for `moveDecorations()`

## 0.1.0 (2023/06/15)
------------------
- Minor update
- Added dynamic pivot offset, parallax offset, masking and blending fields to `addDecoration()` and `moveDecorations()`
- Added angleOffset to `setSpeed()`

## 0.0.3 (2023/06/14)
------------------
- Minor bugfix: fixed filename `__init__.py`

## 0.0.2 (2023/06/13)
------------------
- Minor bugfix: `'re'` is no longer a dependency

## 0.0.1 (2023/05/28)
------------------
- First Release