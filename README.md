# CTFdTools

## YML Description
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
- `type` : 必須是 `standard` 或 `dynamic`
- `value` : 如果 `type` 是 `standard` 的話，`value` 是這個 challenge 的分數，如果 `type` 是 `dynamic` 的話，`value` 會是
    ```yaml
    value:
      function: linear
      initial: 500
      minimum: 100
    ```
- `state` : 必須是 `hidden` 或 `visible`

### Metadata
- `canonical_name` : 只能由 `a-z` `0-9` 和 `-` 組成，如果沒有 `distfiles` 的話是 Optional，有 `distfiles` 的話會是 required


---
## Example For YML

```yml
name: Simple Name
category: Simple Category
description: |
  This is a simple description
author: Curious
connection_info: nc {server} 10000
flag: FLAG{Simple_Flag}
tags: 
  - Simple Tag 0
  - Simple Tag 1
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


---
## Example For CTFdTools

```py
from CTFdTools.ctfd import CTFd
from CTFdTools.challenge import Challenge


# 指從 `.env` 裡面載入環境變數，`.env` 裡面需要有 `BASE_URL`、`TOKEN` 和 `SERVER`
#   - `BASE_URL` : CTFd 首頁的網址
#   - `TOKEN`    : CTFd token
#   - `SERVER`   : Challenge deploy server 的 IP
ctfd = CTFd('.env')

challenges: list[Challenge] = []
for root, _, files in os.walk('.'):
    if 'task.yml' in files:
        # 把每個 `task.yml` 都載入進來
        challenges.append(Challenge(root, ctfd))

for challenge in challenges:
    # 把 challenge post 到 CTFd
    challenge.post()
```
