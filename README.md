# CTFdTools
## Description
### Challenge Info
- `name`
- `category`
- `description` (Optional)
- `author` (Optional)
- `connection_info` (Optional)
- `flag` (Optional)
- `tags` (Optional)
- `distfiles` (Optional)
- `hints` (Optional)

### CTFd Info
- `type` : 可以是 `static` 或 `dynamic`
- `value` : 如果 `type` 是 `static` 的話，`value` 是這個 challenge 的分數，如果 `type` 是 `dynamic` 的話，`value` 會是
    ```yaml
    value:
      function: linear
      initial: 500
      minimum: 100
    ```
- `state` : 可以是 `hidden` 或 `visible`

### Metadata
- `canonical_name` : 只能由 `a-z` `0-9` 和 `-` 組成


---
## Example

```yaml
name: Simple
category: Simple
description: |
  This is a simple description
author: Curious
connection_info: nc 127.0.0.1 10000
flag: FLAG{Simple_Flag}
tags: 
  - Simple
distfiles:
  - ./chal
  - ./dist
hints:
  - |
    This is a simple hint

type: static
value: 500
state: visible

canonical_name: simple
```
