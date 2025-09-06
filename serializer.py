# serializer.py
from __future__ import annotations
import json
import dataclasses
import datetime
import decimal
import base64
import uuid
import inspect
from enum import Enum
from typing import Any, Callable, Iterable, Mapping, Optional, Dict, Set

# --- Helpers / default converters ---
DEFAULT_TYPE_CONVERTERS: Dict[type, Callable[[Any], Any]] = {
    datetime.datetime: lambda dt: dt.isoformat(),
    datetime.date: lambda d: d.isoformat(),
    datetime.time: lambda t: t.isoformat(),
    decimal.Decimal: lambda d: str(d),
    uuid.UUID: lambda u: str(u),
    bytes: lambda b: base64.b64encode(b).decode("ascii"),
    bytearray: lambda b: base64.b64encode(bytes(b)).decode("ascii"),
    Enum: lambda e: e.value if hasattr(e, "value") else e.name,
}

def _is_primitive(obj: Any) -> bool:
    return obj is None or isinstance(obj, (str, int, float, bool))

# --- Core primitive conversion ---
def to_primitive(
    obj: Any,
    *,
    type_converters: Optional[Dict[type, Callable[[Any], Any]]] = None,
    state_extractor: Optional[Callable[[Any], Any]] = None,
    _visited: Optional[Set[int]] = None,
) -> Any:
    """
    Convert `obj` into JSON-serializable primitives (dict/list/str/int/float/bool/None).
    - type_converters: mapping from type -> converter(obj) for types like datetime, Decimal, UUID...
    - state_extractor: callable(obj) -> state; used for frameworks like LangGraph where objects
                       may carry a `.state` or custom structure.
    """
    if _visited is None:
        _visited = set()

    # avoid infinite recursion for cycles
    oid = id(obj)
    if oid in _visited:
        return f"<cycle {type(obj).__name__}>"
    _visited.add(oid)

    # small shortcut for primitives
    if _is_primitive(obj):
        _visited.remove(oid)
        return obj

    # allow custom type converters (merge defaults)
    converters = dict(DEFAULT_TYPE_CONVERTERS)
    if type_converters:
        converters.update(type_converters)

    # exact-type converters (or isinstance for Enum)
    for t, conv in converters.items():
        try:
            if t is Enum:
                if isinstance(obj, Enum):
                    val = conv(obj)
                    _visited.remove(oid)
                    return val
            elif isinstance(obj, t):
                val = conv(obj)
                _visited.remove(oid)
                return val
        except Exception:
            # if converter fails, ignore and continue fallback
            pass

    # Mapping-like (dict, TypedDict, etc.)
    if isinstance(obj, Mapping):
        out = {}
        for k, v in obj.items():
            # JSON keys must be strings
            if not isinstance(k, str):
                k = str(k)
            out[k] = to_primitive(v, type_converters=type_converters, state_extractor=state_extractor, _visited=_visited)
        _visited.remove(oid)
        return out

    # Iterable (but not bytes/str)
    if isinstance(obj, Iterable) and not isinstance(obj, (str, bytes, bytearray, dict)):
        try:
            out = [to_primitive(v, type_converters=type_converters, state_extractor=state_extractor, _visited=_visited) for v in obj]
            _visited.remove(oid)
            return out
        except TypeError:
            pass  # not a real iterable; continue

    # Pydantic v2
    if hasattr(obj, "model_dump") and callable(getattr(obj, "model_dump")):
        try:
            dumped = obj.model_dump()
            out = to_primitive(dumped, type_converters=type_converters, state_extractor=state_extractor, _visited=_visited)
            _visited.remove(oid)
            return out
        except Exception:
            pass

    # Pydantic v1
    if hasattr(obj, "dict") and callable(getattr(obj, "dict")) and not inspect.isclass(obj):
        try:
            dumped = obj.dict()
            out = to_primitive(dumped, type_converters=type_converters, state_extractor=state_extractor, _visited=_visited)
            _visited.remove(oid)
            return out
        except Exception:
            pass

    # dataclass
    if dataclasses.is_dataclass(obj):
        try:
            dumped = dataclasses.asdict(obj)
            out = to_primitive(dumped, type_converters=type_converters, state_extractor=state_extractor, _visited=_visited)
            _visited.remove(oid)
            return out
        except Exception:
            pass

    # common custom serializers
    for attr in ("to_dict", "to_json", "serialize", "as_dict"):
        if hasattr(obj, attr) and callable(getattr(obj, attr)):
            try:
                result = getattr(obj, attr)()
                # if to_json returns a str, try to parse it
                if isinstance(result, str):
                    try:
                        parsed = json.loads(result)
                        out = to_primitive(parsed, type_converters=type_converters, state_extractor=state_extractor, _visited=_visited)
                        _visited.remove(oid)
                        return out
                    except Exception:
                        # not JSON -> return the string
                        _visited.remove(oid)
                        return result
                out = to_primitive(result, type_converters=type_converters, state_extractor=state_extractor, _visited=_visited)
                _visited.remove(oid)
                return out
            except Exception:
                pass

    # LangGraph-style: allow user to provide a state_extractor or look for .state
    if state_extractor is not None:
        try:
            extracted = state_extractor(obj)
            out = to_primitive(extracted, type_converters=type_converters, state_extractor=state_extractor, _visited=_visited)
            _visited.remove(oid)
            return out
        except Exception:
            pass

    if hasattr(obj, "state"):
        try:
            st = getattr(obj, "state")
            out = to_primitive(st, type_converters=type_converters, state_extractor=state_extractor, _visited=_visited)
            _visited.remove(oid)
            return out
        except Exception:
            pass

    # final fallback: try obj.__dict__ if present
    if hasattr(obj, "__dict__"):
        try:
            d = {k: v for k, v in vars(obj).items() if not k.startswith("_")}
            out = to_primitive(d, type_converters=type_converters, state_extractor=state_extractor, _visited=_visited)
            _visited.remove(oid)
            return out
        except Exception:
            pass

    # last resort: string representation
    _visited.remove(oid)
    return str(obj)

# --- JSON serializer wrapper ---
def model_to_json(
    obj: Any,
    *,
    indent: Optional[int] = 2,
    ensure_ascii: bool = False,
    type_converters: Optional[Dict[type, Callable[[Any], Any]]] = None,
    state_extractor: Optional[Callable[[Any], Any]] = None,
) -> str:
    """
    Convert any object into a JSON string. If `obj` is an iterable of models (list/tuple/etc.)
    it will serialize the iterable as a JSON array.
    """
    primitive = to_primitive(obj, type_converters=type_converters, state_extractor=state_extractor)
    return json.dumps(primitive, indent=indent, ensure_ascii=ensure_ascii)

# --- NDJSON / streaming generator ---
def stream_ndjson(
    iterable: Iterable[Any],
    *,
    type_converters: Optional[Dict[type, Callable[[Any], Any]]] = None,
    state_extractor: Optional[Callable[[Any], Any]] = None,
) -> Iterable[str]:
    """
    Turn an iterable of objects into an iterator of NDJSON lines (strings).
    """
    for item in iterable:
        yield json.dumps(
            to_primitive(item, type_converters=type_converters, state_extractor=state_extractor),
            ensure_ascii=False
        )

# --- write to file convenience ---
def dump_to_file(
    obj: Any,
    path: str,
    *,
    indent: Optional[int] = 2,
    ndjson: bool = False,
    type_converters: Optional[Dict[type, Callable[[Any], Any]]] = None,
    state_extractor: Optional[Callable[[Any], Any]] = None,
) -> None:
    if ndjson and isinstance(obj, Iterable) and not isinstance(obj, (str, bytes, bytearray, dict)):
        with open(path, "w", encoding="utf-8") as f:
            for line in stream_ndjson(obj, type_converters=type_converters, state_extractor=state_extractor):
                f.write(line + "\n")
    else:
        s = model_to_json(obj, indent=indent, ensure_ascii=False, type_converters=type_converters, state_extractor=state_extractor)
        with open(path, "w", encoding="utf-8") as f:
            f.write(s)
