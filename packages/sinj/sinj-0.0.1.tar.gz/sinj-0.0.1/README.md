
# 💉 sinj

`sinj` (**S**imple **Inj**ect) is yet another IoC framework for python. If you try to avoid global variables and singletons you might end up with a complex graph of dependencies in your application. With `sinj` everything is just flat. If you are coming from Java or C# you might be more familiar with IoC frameworks where dependencies are resolved by interface. In python we do not have interfaces and strict types so here we resolve dependencies by constructor argument names.

# Basic examples

The most simple example:

```python
import sinj

class A:
    def a(self):
        return "a"

class B:
    def __init__(self, a):
        self._a = a
    
    def b(self):
        return self._a() + " b"

ioc_container = sinj.Container()
ioc_container.register(A, "a")
ioc_container.register(B, "b")

b = ioc_container.resolve("b")
print(b.b()) # -> "a b"
```

The same example with annotated classes:

```python
import sinj

class A:
    inject = "a" # a will be injected into __init__ method
    def a(self):
        return "a"

class B:
    inject = "b" # b will be injected into __init__ method
    def __init__(self, a):
        self._a = a
    
    def b(self):
        return self._a() + " b"

ioc_container = sinj.Container()
ioc_container.register(A) # no need to specify instance name here
ioc_container.register(B) # but you can overwrite it

b = ioc_container.resolve("b")
print(b.b()) # -> "a b"
```

More examples will be available in `./examples`


# Errors

```python
import sinj
sinj.DependencyNotFoundError # thrown on resolve when dependency is not found for given label (and it is not optional).
sinj.CircularDependencyError # thrown on resolve when circular dependency is detected.
sinj.DependencyConflictError # thrown on register when the container already contains class by that label.
sinj.DependencyNotMappedError # thrown on register when the class is not annotated and the label is not provided in register method.
```

# Install

From pypi.org

```bash
# FIXME
```

From gitlab.com

```bash
# FIXME
```
