## django technical assignment

### author: Davit Koshkeli


### How to run 

Clone the repository
```shell
git clone github.com/koshkaj/djangoproject
cd djangoproject
```

running the project
```shell
make dev
```

running the tests
```shell
make test
---------------------------------------------------------------------
Found 3 test(s).
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
...
----------------------------------------------------------------------
Ran 3 tests in 0.011s

OK

```

## Notes:

- I did not implement tests for every endpoint because it is time consuming, I only wrote it 
for one endpoint to demonstrate that I know how to write tests and how do they work
- I do not have user auth or anything implemented, I just did what was described in the task
- I also have not implemented additional features like if you want to remove the field when a row is already added,
obviously SQL throws an error in that case, usually you would have a workaround on those fields when implementing dynamic
table creations, but statically, you would just use `default value` or `null=True` after altering or removing the field


