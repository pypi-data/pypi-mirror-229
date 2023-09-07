import inspect

from .DependencyNotFoundError import DependencyNotFoundError
from .CircularDependencyError import CircularDependencyError
from .DependencyConflictError import DependencyConflictError
from .DependencyNotMappedError import DependencyNotMappedError


class Container:
    def __init__(self):
        self._inject_register = dict()  # instance_name -> class
        self._inject_list_register = dict()  # list_name -> set<instance_name>
        self._resolved = dict()  # (instance_name | list_name) -> instance

    def register(self, cls, inject=None, inject_list=None):
        if inject is None:
            if hasattr(cls, "inject"):
                inject = cls.inject

        if inject is None:
            cls_name = "cls"
            if hasattr(cls, "__name__"):
                cls_name = cls.__name__
            raise DependencyNotMappedError(f"inject is None for {cls_name}")

        if inject_list is None:
            if hasattr(cls, "inject_list"):
                inject_list = cls.inject_list

        if isinstance(inject_list, str):
            inject_list = [inject_list]

        if inject_list is None:
            inject_list = []

        if inject in self._inject_register:
            raise DependencyConflictError(f"inject conflict for {inject}")

        if inject in self._inject_list_register:
            raise DependencyConflictError(f"inject conflict for {inject}")

        for i in inject_list:
            if i in self._inject_register:
                raise DependencyConflictError(f"inject conflict for {i}")

        for i in inject_list:
            if i not in self._inject_list_register:
                self._inject_list_register[i] = set()

            self._inject_list_register[i].add(inject)

        self._inject_register[inject] = cls

    def resolve(self, instance_name, throw_if_missing=True):
        unresolved = set()
        return self._resolve_recursive(instance_name, throw_if_missing, unresolved)

    def _resolve_recursive(self, instance_name, throw_if_missing, unresolved):
        if instance_name in self._resolved:
            return self._resolved[instance_name]

        if instance_name in unresolved:
            raise CircularDependencyError(
                f"circular dependency detected for {instance_name}"
            )

        unresolved.add(instance_name)

        if instance_name in self._inject_register:
            instance = self._resolve_instance(instance_name, unresolved)
            self._resolved[instance_name] = instance
            unresolved.remove(instance_name)
            return instance

        if instance_name in self._inject_list_register:
            instance = self._resolve_list(instance_name, unresolved)
            self._resolved[instance_name] = instance
            unresolved.remove(instance_name)
            return instance

        if throw_if_missing:
            raise DependencyNotFoundError(
                f"could not resolve dependency for {instance_name}"
            )

        return None

    def _resolve_instance(self, instance_name, unresolved):
        cls = self._inject_register[instance_name]
        instance = self._instanciate(cls, unresolved)
        return instance

    def _resolve_list(self, instance_name, unresolved):
        result = []
        for i in self._inject_list_register[instance_name]:
            instance = self._resolve_recursive(i, True, unresolved)
            result.append(instance)
        return result

    def _instanciate(self, cls, unresolved):
        sig = inspect.signature(cls)
        args = []
        kwargs = dict()
        for param in sig.parameters.values():
            if param.kind == param.VAR_POSITIONAL:
                continue
            if param.kind == param.VAR_KEYWORD:
                continue

            arg = self._resolve_recursive(param.name, False, unresolved)
            if param.kind == param.POSITIONAL_ONLY:
                if arg is None:
                    cls_name = "cls"
                    if hasattr(cls, "__name__"):
                        cls_name = cls.__name__
                    raise DependencyNotFoundError(
                        f"could not resolve POSITIONAL_ONLY dependency for {cls_name} {param.name}"
                    )
                args.append(arg)

            if (
                param.kind == param.KEYWORD_ONLY
                and param.default is param.empty
                and arg is None
            ):
                cls_name = "cls"
                if hasattr(cls, "__name__"):
                    cls_name = cls.__name__
                raise DependencyNotFoundError(
                    f"could not resolve non default KEYWORD_ONLY dependency for {cls_name} {param.name}"
                )

            if (
                param.kind == param.POSITIONAL_OR_KEYWORD
                and param.default is param.empty
                and arg is None
            ):
                cls_name = "cls"
                if hasattr(cls, "__name__"):
                    cls_name = cls.__name__
                raise DependencyNotFoundError(
                    f"could not resolve non default POSITIONAL_OR_KEYWORD dependency for {cls_name} {param.name}"
                )

            if arg is not None:
                kwargs[param.name] = arg

        instance = cls(*args, **kwargs)
        return instance
