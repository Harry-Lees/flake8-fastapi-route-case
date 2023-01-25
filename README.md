# Flake8 FastAPI Route Case

A Flake8 FastAPI plugin to ensure all FastAPI routes follow the same case.

## Rationale

In a project, you may have many FastAPI endpoints, this plugin will ensure
all FastAPI routes follow the same case so you don't end up with mismatched
case.

```python
@router.get("/users/user_info")
def get_user_info():
    ...

# should be /users/user_info to follow naming convention
@router.post("/users/userInfo")
def post_user_info():
    ...
```
