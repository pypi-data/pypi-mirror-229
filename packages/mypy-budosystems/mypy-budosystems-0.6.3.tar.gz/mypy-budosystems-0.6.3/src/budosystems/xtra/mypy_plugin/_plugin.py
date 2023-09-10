#
#  Copyright (c) 2021-2023.  Budo Systems
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
#

# # type: ignore  # Have mypy ignore the whole file for now.
# pylint: skip-file

"""MyPy Plugin to let it know of the variations it should expect from the model."""
from __future__ import annotations

# noinspection SpellCheckingInspection
# pylint: disable=unused-import
# TODO: Clean-up imports once the plug-in works.

from typing import (
    Optional,
    Callable,
    Union,
    Any,
)

import sys
from traceback import (
    extract_tb,
    extract_stack,
)
from os import (
    environ
)

import logging
import coloredlogs      # type: ignore
from autologging import traced, TRACE, logged, install_traced_noop  # type: ignore

from mypy.plugin import (
    Plugin,
    ClassDefContext,
    CheckerPluginInterface,
    SemanticAnalyzerPluginInterface, DynamicClassDefContext, AttributeContext, MethodContext, MethodSigContext,
    FunctionContext, FunctionSigContext, AnalyzeTypeContext,
)
from mypy.options import Options
from mypy.plugins.common import (
    add_attribute_to_class,
)
from mypy.plugins.attrs import (
    attr_class_makers,
    attr_attrib_makers,
    attr_class_maker_callback,
    attr_dataclass_makers,
    attr_tag_callback,
    attr_class_maker_callback,
    MAGIC_ATTR_NAME,
    MAGIC_ATTR_CLS_NAME_TEMPLATE,
    MethodAdder, ATTRS_INIT_NAME,
    _add_attrs_magic_attribute,
    _analyze_class,
    _add_match_args,
    _add_init,
    _add_order,
    _make_frozen,
)
from mypy.nodes import (
    Node,
    TypeInfo,
    FuncBase,
    SymbolNode,
    TupleExpr, ClassDef,
    SymbolTableNode, DictExpr,
)
from mypy.evalexpr import (
    evaluate_expression
)
from mypy.types import (
    Instance,
    TupleType, Type, FunctionLike,
)
from mypy.lookup import lookup_fully_qualified
# from mypy.semanal import set_callable_name


from budosystems.models.meta import BudoMeta, default_attr_config


# Debug logging
log = logging.getLogger(__name__)
fmt_args = {"fmt": '[{levelname:^10}] {funcName}:[{lineno:d}] {message}', "style": '{'}
# log.setLevel(TRACE)
# log.setLevel(logging.INFO)
log.setLevel(logging.DEBUG)
console = logging.StreamHandler(sys.stdout)
console.setFormatter(coloredlogs.ColoredFormatter(**fmt_args))
console.setLevel(logging.WARNING)
log.addHandler(console)
debug_file = logging.FileHandler("budosystems_mypy_plugin_debug.log", "w+", "utf-8")
debug_file.setFormatter(logging.Formatter(**fmt_args))  # type: ignore
debug_file.setLevel(logging.DEBUG)
log.addHandler(debug_file)


ds = 6
debug_title = '*'*ds + ' '*ds + "Budo Systems Mypy Plugin" + ' '*ds + '*'*ds

log.debug('*'*len(debug_title))
log.info(debug_title)
log.debug('*'*len(debug_title))


def _node_repr(self: Node) -> str:
    qname = type(self).__qualname__
    extra = ""
    if hasattr(self, "fullname") and self.fullname:
        extra = f" for {self.fullname}"
    elif hasattr(self, "items") and self.items:
        extra = f" with items={self.items}"
    elif hasattr(self, "value") and self.value:
        extra = f" with value={self.value}"

    return f"⟪{qname}{extra}⟫"


Node.__repr__ = _node_repr     # type: ignore #[method-assign,assigment]
SymbolTableNode.__repr__ = SymbolTableNode.__str__    # type: ignore #[method-assign,assignment]


# @traced
def fully_qualified_class_name(cls: Union[object, type]) -> str:
    """Returns the fully qualified class name of the provided object or class."""
    if not isinstance(cls, type):
        cls = type(cls)
    value = f"{cls.__module__}.{cls.__qualname__}"
    return value


BUDO_META_FQCN = fully_qualified_class_name(BudoMeta)
log.debug(f"{BUDO_META_FQCN=}")

attr_class_makers.add(BUDO_META_FQCN+".__new__")


# @traced
class BudoModelPlugin(Plugin):
    """Implementation of MyPy Plugin specialized for Budo Systems models."""

    def __init__(self, options: Options):
        super().__init__(options)
        self._bmti: Optional[Node] = None
        log.log(TRACE, f"{self=}")

    def get_metaclass_hook(self, fullname: str
                           ) -> Optional[Callable[[ClassDefContext], None]]:
        # if fullname == BUDO_META_FQCN:
        if fullname.startswith("budosystems."):
            log.debug("Sending handler")
            return budo_meta_handler
        return None

    def get_base_class_hook(self, fullname: str
                            ) -> Optional[Callable[[ClassDefContext], None]]:
        sym = self.lookup_fully_qualified(fullname)
        if sym and self.BUDO_META_TYPE_INFO and isinstance(sym.node, TypeInfo):
            mcs: Optional[Instance] = sym.node.calculate_metaclass_type()
            log.debug(f"{sym.node=}")
            log.debug(f"{mcs=}")

            if mcs and mcs.type == self.BUDO_META_TYPE_INFO:
                # Metaclass is BudoMeta
                log.debug(f"{sym=}")
                log.debug(f"{sym.node=}")
                log.debug("Sending handler")
                return budo_class_handler

            if any(base == self.BUDO_META_TYPE_INFO for base in sym.node.mro):
                # BudoMeta is an ancestor.
                log.debug(f"{sym.node.mro=}")
                return budo_meta_handler
        return None

    @property
    def BUDO_META_TYPE_INFO(self) -> Optional[Node]:
        """If available, returns the :class:`TypeInfo` for :class:`BudoMeta`."""
        if not self._bmti:
            stn = self.lookup_fully_qualified(BUDO_META_FQCN)
            if stn:
                self._bmti = stn.node
            log.debug(f"{self._bmti=}")
        return self._bmti

    # # NOTE: Overriding for tracing purposes.
    # def get_type_analyze_hook(self, fullname: str) -> Callable[[AnalyzeTypeContext], Type] | None:
    #     return None
    #
    # def get_function_signature_hook(self, fullname: str) -> Callable[[FunctionSigContext], FunctionLike] | None:
    #     return None
    #
    # def get_function_hook(self, fullname: str) -> Callable[[FunctionContext], Type] | None:
    #     return None
    #
    # def get_method_signature_hook(self, fullname: str) -> Callable[[MethodSigContext], FunctionLike] | None:
    #     return None
    #
    # def get_method_hook(self, fullname: str) -> Callable[[MethodContext], Type] | None:
    #     return None
    #
    # def get_attribute_hook(self, fullname: str) -> Callable[[AttributeContext], Type] | None:
    #     return None
    #
    # def get_class_attribute_hook(self, fullname: str) -> Callable[[AttributeContext], Type] | None:
    #     return None
    #
    # def get_class_decorator_hook(self, fullname: str) -> Callable[[ClassDefContext], None] | None:
    #     return None
    #
    # def get_class_decorator_hook_2(self, fullname: str) -> Callable[[ClassDefContext], bool] | None:
    #     return None
    #
    # def get_customize_class_mro_hook(self, fullname: str) -> Callable[[ClassDefContext], None] | None:
    #     return None
    #
    # def get_dynamic_class_hook(self, fullname: str) -> Callable[[DynamicClassDefContext], None] | None:
    #     return None


# Callbacks
def budo_meta_handler(ctx: ClassDefContext) -> None:
    """Callback function to process classes that have :class:`BuduMeta` as a metaclass."""
    log.debug(f"About the class:")
    log.debug(f"{ctx.cls.info=!s}")
    log.debug(f"{ctx.cls.decorators=!s}")
    # log.debug(f"{ctx.cls.defs=!s}")
    # log.debug(f"{ctx.reason=}")
    log.debug(f"{ctx.cls.info.names=}")

    if MAGIC_ATTR_NAME not in ctx.cls.info.names:
        log.debug(f"{ctx.api=}")
        builtins_tuple_instance = ctx.api.named_type("builtins.tuple")
        log.debug(f"{builtins_tuple_instance=!s}")
        tuple_type = TupleType([], builtins_tuple_instance)
        log.debug(f"{tuple_type=!s}")

        attr_s_func = ctx.api.lookup_fully_qualified("attr.s")
        log.debug(f"{attr_s_func.node=}")

        # ctx.cls.decorators.append(attr_s_func)

        # attr_class_maker_callback(ctx, True)
        # _add_attrs_magic_attribute(ctx, [])
        # add_attribute_to_class(ctx.api, ctx.cls, MAGIC_ATTR_NAME, tuple_type)


# @traced
def _attrs_kwargs(cls: ClassDef) -> dict[str, Any]:
    attrs_kwargs: dict[str, Any] = default_attr_config.copy()
    log.debug(f"{cls.keywords=}")
    if cls.keywords and 'attrs' in cls.keywords:
        cls_attrs = cls.keywords['attrs']
        log.debug(f"{cls.fullname=}")
        if isinstance(cls_attrs, DictExpr):
            log.debug(f"{cls_attrs.items=}")
            eval_cls_attrs = evaluate_expression(cls_attrs)
            log.debug(f"{eval_cls_attrs=}")
            assert isinstance(eval_cls_attrs, dict)
            attrs_kwargs.update(eval_cls_attrs)
    return attrs_kwargs


# @traced
def budo_class_handler(ctx: ClassDefContext) -> None:
    """Callback function to process classes that have :class:`BuduMeta` as a metaclass."""
    log.debug(f"About the class:")
    log.debug(f"{ctx.cls.info=!s}")
    log.debug(f"{ctx.cls.keywords=}")
    log.debug(f"{ctx.cls.decorators=!s}")
    log.debug(f"{ctx.cls.metaclass=!s}")
    info: TypeInfo = ctx.cls.info
    log.debug(f"{info.metaclass_type=}")
    # budo_meta_handler(ti.metaclass_type)

    attrs_kwargs = _attrs_kwargs(ctx.cls)
    log.debug(f"{attrs_kwargs=}")

    defaults = ctx.api.lookup_fully_qualified("budosystems.models.meta.default_attr_config")
    log.debug(f"{defaults=}")
    #
    # init = ctx.cls.keywords["info"] or default_attr_config["init"]
    # frozen = _get_frozen(ctx, frozen_default)
    # order = _determine_eq_order(ctx)
    # slots = _get_decorator_bool_argument(ctx, "slots", False)
    #
    # auto_attribs = _get_decorator_optional_bool_argument(ctx, "auto_attribs", auto_attribs_default)
    # kw_only = _get_decorator_bool_argument(ctx, "kw_only", False)
    # match_args = _get_decorator_bool_argument(ctx, "match_args", True)
    #
    init = attrs_kwargs.get("init", True)
    frozen = attrs_kwargs.get("frozen", False)
    order = attrs_kwargs.get("order", False)
    slots = attrs_kwargs.get("slots", False)
    auto_attribs = attrs_kwargs.get("auto_attribs", True)
    kw_only = attrs_kwargs.get("kw_only", False)
    match_args = attrs_kwargs.get("match_args", True)

    for super_info in ctx.cls.info.mro[1:-1]:
        if "attrs_tag" in super_info.metadata and "attrs" not in super_info.metadata:
            # Super class is not ready yet. Request another pass.
            return # False

    attributes = _analyze_class(ctx, auto_attribs, kw_only)
    #
    # # Check if attribute types are ready.
    for attr in attributes:
        node = info.get(attr.name)
        if node is None:
            # This name is likely blocked by some semantic analysis error that
            # should have been reported already.
            info.metadata["attrs"] = {"attributes": [], "frozen": frozen}
            return # True

    _add_attrs_magic_attribute(ctx, [(attr.name, info[attr.name].type) for attr in attributes])
    if slots:
        info.slots = {attr.name for attr in attributes}
    if match_args and ctx.api.options.python_version[:2] >= (3, 10):
        # `.__match_args__` is only added for python3.10+, but the argument
        # exists for earlier versions as well.
        _add_match_args(ctx, attributes)
    #
    # Save the attributes so that subclasses can reuse them.
    info.metadata["attrs"] = {
        "attributes": [attr.serialize() for attr in attributes],
        "frozen": frozen,
    }

    #
    adder = MethodAdder(ctx)
    # If  __init__ is not being generated, attrs still generates it as __attrs_init__ instead.
    _add_init(ctx, attributes, adder, "__init__" if init else ATTRS_INIT_NAME)
    if order:
        _add_order(ctx, adder)
    if frozen:
        _make_frozen(ctx, attributes)

    return # True

# Helpers


# Make this plugin accessible to the config file
def plugin(version: str) -> type[Plugin]:
    """Budo Systems model plugin for MyPy.

    :return: The :class:`BudoModelPlugin` class
    """
    log.info(f"Plugin {__name__} initialized for mypy {version}")
    return BudoModelPlugin
