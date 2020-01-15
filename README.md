# PEPGrave
PEPGrave: Resurrecting Dead PEPS

> Re-write of my old project [PEPAllow](https://github.com/isidentical-archive/pepallow) with a complete new approach

```py
from pepgrave import magic

with magic.Magic(313):
    assert IV == 4
    print(XX)

with magic.Magic(204):
    print([:5], "yaay!", "no more", range(5))
    assert [:5] == [0, 1, 2, 3, 4]
    some_iterator = reversed([:3])

with magic.Magic(276):
    for i in 3:
        if i > 1:
            print(i)

with magic.Magic(245, 212):
    interface Foo:
        pass
    print(Foo.__abstractmethods__)


    for i indexing e in some_iterator:
        print(i, e)

try:
    assert XX == 4
except:
    print("yea some normal non-magical code")
```
