import functools
import inspect
from typing import Callable, Type, Iterable, Optional

from ._models import FunctionInformation
from ._utils import parse_function_information


class _BaseOperationAdditionalFunctionDecorator:  # noqa
    """
    Base decorator class, that contain all common logic for
    store and work with decorated functions of services classes
    """

    def __init__(self):
        self._operations_additional_funcs_store: dict[Type, dict[str, list[FunctionInformation]]] = {}

    def __getattr__(self, operation_name):
        """
        Use getattr to dynamic registration of any operation additions
        """

        class _BaseOperationAdditionalFunctionDecoratorWrapper:
            def __init__(init_self, method=None, *, priority: int = -1, rollback: Optional[Callable] = None):
                nonlocal self
                init_self.additional_function_decorator = self  # pre or post decorator object
                init_self.operation_decorator_wrapper = None
                init_self.operation_name = operation_name
                init_self.method = None
                init_self.priority = priority
                init_self.rollback = rollback

                if inspect.isfunction(method):
                    init_self.method = method
                    if method is not None:
                        functools.update_wrapper(init_self, method)
                else:
                    init_self.operation_decorator_wrapper = method

            def __set_name__(self, owner, name):
                def register(operation_decorator: _BaseOperationAdditionalFunctionDecoratorWrapper):
                    method = operation_decorator.method
                    if operation_decorator.operation_decorator_wrapper is not None:
                        method = register(operation_decorator.operation_decorator_wrapper)
                    operation_decorator.additional_function_decorator._register_operation_func(
                        operation_name=operation_decorator.operation_name,
                        original_function_owner=owner,
                        original_function=method,
                        priority=operation_decorator.priority,
                        rollback=operation_decorator.rollback,
                    )
                    return method

                self.method = register(self)
                setattr(owner, name, self.method)

            def __call__(self, method_or_wrapper):
                return _BaseOperationAdditionalFunctionDecoratorWrapper(
                    method_or_wrapper, priority=self.priority, rollback=self.rollback
                )

        return _BaseOperationAdditionalFunctionDecoratorWrapper

    def _get_class_funcs(self, class_obj) -> dict[str, list[FunctionInformation]]:
        """
        Used in local cases and can be used only for add/edit class funcs,
        but can't handle MRO recursive funcs handling
        """
        if (res := self._operations_additional_funcs_store.get(class_obj, None)) is None:
            res = self._operations_additional_funcs_store[class_obj] = {}
        return res

    def _register_operation_func(
        self,
        operation_name: str,
        original_function_owner: Type,
        original_function: Callable,
        priority: int,
        rollback: Optional[Callable] = None,
    ):
        operation_name = operation_name.lower()
        funcs_store = self._get_class_funcs(original_function_owner)
        if operation_name not in funcs_store:
            funcs_store[operation_name] = []
        funcs_list = funcs_store[operation_name]

        func_info = parse_function_information(original_function)
        func_info.priority = priority
        func_info.rollback = rollback
        funcs_list.append(func_info)

    def get_additional_operation_funcs(self, operation_owner_class, operation_name: str) -> list[FunctionInformation]:
        classes: Iterable[Type] = reversed(inspect.getmro(operation_owner_class))
        result: list[FunctionInformation] = []
        for obj in classes:
            result.extend(self._get_class_funcs(obj).get(operation_name, []))
        return result


# Decorators collection for automatic running pre-operation functions
pre = _BaseOperationAdditionalFunctionDecorator()

# Decorators collection for automatic running post-operation functions
post = _BaseOperationAdditionalFunctionDecorator()


def operation(
    _method=None,
    *,
    exception_handlers_mapping: Optional[dict[Type, Callable]] = None,
    as_transaction: bool = False,
    rollback: Optional[Callable] = None,
):
    def decorator_operations(func):
        from .operations import _OperationsFactory

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return _OperationsFactory(
                method=func,
                exception_handlers_mapping=exception_handlers_mapping,
                as_transaction=as_transaction,
                rollback=rollback,
            )(*args, **kwargs)

        return wrapper

    if _method is None:
        return decorator_operations
    else:
        return decorator_operations(_method)
