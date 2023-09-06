<h1 style="text-align: center">Ory</h1>
<p style="text-align: center">
    <strong>Huge Singleton Python implementation</strong>
</p>
<hr>

<h1 style="text-align: center;">Overview</h1>

<p style="text-align: justify">
Ory is a library that facilitates the implementation of classes as singletons. However, it offers more than that. The
library also encompasses a series of useful functions that further simplify the singleton design pattern in Python. With
Ory, it becomes feasible to store any type of data within a singleton class and subsequently utilize it globally
throughout the entire project. We also support the asynchronous programming paradigm with asyncio.
</p>

<hr>

<h1 style="text-align: center;">Installation</h1>
<p style="text-align: justify">
If you have pip installed, you can simply run the following command to install Ory:
</p>

```bash
pip install nyria-ory
```

<p style="text-align: justify">
Otherwise, you can clone the repository and install the package manually:
</p>

```bash
git clone https://gitlab.nyria.net/nyria/libaries/ory.git
```

<hr>

<h1 style="text-align: center;">How does it work?</h1>
<p style="text-align: justify">
In Ory, to be more precise, we have a three-tier layer system. 
The first layer comprises the Registry Handler, which enables 
the global storage of everything. In the second layer, there are the Pools.
These Pools are stored within the Registry and can be accessed from there. 
They encompass the first layer, which consists of the Pods. A Pod serves as a 
wrapper for the value stored within.
</p>

<hr>

<h1 style="text-align: center;">Singleton Example</h1>

```py
from ory.ext.singleton import Singleton

class Car(Singleton):
    door = 4
    color = "red"
```

<p style="text-align: justify">
The above example shows how to create a singleton class. Every class that inherits from the Singleton class will be
automatically a singleton.
</p>

<hr>

<h1 style="text-align: center;">Registry Example</h1>

<p style="text-align: justify">
The following example shows how to store something in the registry. The registry is the first layer of the three-tier layer system. It
enables the global storage of everything. In the example, we create a pool called "workshop" and a pod called "car". The
pod stores a Car object. The pool is registered within the registry. The pod is registered within the pool. The
permission of the pool and the pod is set to READ_ONLY. This means that the pool and the pod can only be read, but not
modified. 
</p>

```py
from ory.components.pod import Pod
from ory.components.pool import Pool
from ory.components.registry_handler import RegistryHandler

from ory.states.permission import Permission


class Car:
    pass


pool = Pool(
    name="workshop",
    permission=Permission.READ_ONLY
)

pod = Pod(
    name="car",
    permission=Permission.READ_ONLY,
    storage=Car()
)

pool.register_pod(pod, override=False)
RegistryHandler.create_new_pool(pool, override=False)
```

<p style="text-align: justify">
To get the stored value, we can use the simple following code:
</p>

```py
from ory.components.registry_handler import RegistryHandler

car = RegistryHandler.get_pool_by_name("workshop").get_pod_by_name("car").get_storage()
```

<hr>