from __future__ import annotations
import oexp.jbridge as jbridge
import sys
import weakref
from multiprocessing import current_process
from threading import current_thread
import abc
from typing import List, Optional, Dict, TypeVar, Generic
from enum import Enum, auto
import json
import struct

_SAFE_PROCESS = current_process().pid
_SAFE_THREAD = current_thread().ident


def _ensure_synchronized():
    global _SAFE_PROCESS, _SAFE_THREAD
    if current_process().pid != _SAFE_PROCESS or current_thread().ident != _SAFE_THREAD:
        raise Exception(
            f"Python-Kotlin communication is currently not safe to use across multiple threads or processes. If you need this feature, please let me know."
        )


JAR_URL = f"https://matt-central.s3.us-east-2.amazonaws.com//0/versioned/front/1693937469/oexp-front-0-all.jar"


class OexpExitSocketHeaders(Enum):
    EXIT = b"\x00"


EXIT = b"\x00"
SET_EXIT_PORT = b"\x01"
CALL_GLOBAL_FUN = b"\x02"
CREATE_OBJECT = b"\x03"
INIT_OBJECT = b"\x04"
CHECK_EQUALITY = b"\x05"
STR = b"\x06"
CALL_FUN = b"\x07"
GET_JSON = b"\x08"
GET_VAL = b"\x09"
SET_VAR = b"\x0A"
GC = b"\x0B"


def _sendall(b):
    jbridge._java_conn.sendall(b)


def _send_short(arg):
    _sendall(arg.to_bytes(2, "big"))


def _send_int(arg):
    _sendall(arg.to_bytes(4, "big"))


def _send_long(arg):
    _sendall(arg.to_bytes(8, "big"))


def _send_double(arg):
    _sendall(struct.pack("d", arg))


def _send_string(arg):
    the_int = len(arg)
    _send_int(the_int)
    _sendall(arg.encode())


def _recv(n):
    r = bytes()
    while n > 0:
        new = jbridge._java_conn.recv(n)
        r += new
        n -= len(new)
    return r


def _recv_is_present():
    isPresent = _recv_byte()
    if isPresent == b"\x00":
        return False
    else:
        if isPresent != b"\x01":
            raise Exception(f"isPresent should be b'\x01' but is {isPresent}")
        return True


def _recv_byte(nullable=False):
    if nullable and not _recv_is_present():
        return None
    return _recv(1)


def _recv_short(nullable=False):
    if nullable and not _recv_is_present():
        return None
    return int.from_bytes(_recv(2), "big", signed=True)


def _recv_int(nullable=False):
    if nullable and not _recv_is_present():
        return None
    return int.from_bytes(_recv(4), "big", signed=True)


def _recv_long(nullable=False):
    if nullable and not _recv_is_present():
        return None
    return int.from_bytes(_recv(8), "big", signed=True)


def _recv_double(nullable=False):
    if nullable and not _recv_is_present():
        return None
    return struct.unpack("d", _recv(8))


def _recv_string(nullable=False):
    if nullable and not _recv_is_present():
        return None
    length = _recv_int()
    return _recv(length).decode("utf-8")


def _recv_exception_check():
    no_exception = _recv_byte()
    if no_exception == b"\x00":
        return None
    else:
        if no_exception != b"\x01":
            raise Exception(f"no_exception should be b'\x01' but is {no_exception}")
        report = _recv_string()
        import oexp.jbridge

        oexp.jbridge.kill_java()
        raise Exception(Exception(report))


def _recv_confirmation():
    confirmation = _recv_byte()
    if confirmation != b"\x00":
        raise Exception(f"confirmation should be b'\x00' but is {confirmation}")


def _recv_bool(nullable=False):
    if nullable and not _recv_is_present():
        return None
    isTrue = _recv_byte()
    if isTrue == b"\x01":
        return True
    else:
        if isTrue != b"\x00":
            raise Exception(f"isTrue should be b'\x00' but is {isTrue}")
        return False


def _recv_object(cls, nullable=False):
    if nullable and not _recv_is_present():
        return None
    r_id = _recv_long()
    if isinstance(cls, KBObject):
        if r_id != cls._id._id:
            cls._init()
            raise Exception(f"buggy singleton id")
        return cls
    else:
        return cls(_id=r_id)


def _recv_enum(cls, nullable=False):
    if nullable and not _recv_is_present():
        return None
    ordinal = _recv_short()
    members = cls.__members__.values()
    for mem in members:
        if mem.value == ordinal:
            return mem
    raise Exception(f"could not find enum constant of {cls} with {ordinal=}")


def _recv_list(elementReceiveFun, nullable=False):
    if nullable and not _recv_is_present():
        return None
    r_len = _recv_int()
    r = []
    for i in range(r_len):
        r.append(elementReceiveFun())
    return r


def _recv_map(keyReceiveFun, valueReceiveFun, nullable=False):
    if nullable and not _recv_is_present():
        return None
    r_len = _recv_int()
    r = {}
    for i in range(r_len):
        k = keyReceiveFun()
        r[k] = valueReceiveFun()
    return r


class DEFAULT_VALUE:
    pass


DEFAULT_VALUE = DEFAULT_VALUE()


class NO_DEFAULT:
    pass


NO_DEFAULT = NO_DEFAULT()


class _ObjectID:
    _object_ids = {}

    def __init__(self, _id):
        self._id = _id

    def __str__(self):
        return f"_ObjectID[{self._id}]"

    def __repr__(self):
        return str(self)


def _object_id(_id):
    ref = _ObjectID._object_ids.get(_id)
    if ref is not None:
        return ref()
    else:
        obj = _ObjectID(_id)
        wref = weakref.ref(obj, lambda ref: _gc_callback(_id))
        _ObjectID._object_ids[_id] = wref
        return obj


_PROBABLY_DISCONNECTED = False


def _gc_callback(the_id):
    global _PROBABLY_DISCONNECTED
    if not _PROBABLY_DISCONNECTED:
        try:
            _sendall(GC)
            _send_long(the_id)
            del _ObjectID._object_ids[the_id]
        except OSError:
            _PROBABLY_DISCONNECTED = True


def _exit_server():
    _sendall(EXIT)


def _check_required_parameters(**kwargs):
    for k, v in kwargs.items():
        if v == NO_DEFAULT:
            raise Exception(f"there is no default value for {k}, so it must be defined")


# [[matt.oexp.front.api.ApiKt#login]]
def login(username=NO_DEFAULT, password=NO_DEFAULT) -> OnlineExperiments:
    _ensure_synchronized()
    _check_required_parameters(**dict(username=username, password=password))
    jbridge._init_java()
    _sendall(CALL_GLOBAL_FUN)
    _send_string(f"matt.oexp.front.api.ApiKt")
    _send_string(f"login")
    _send_string(username)
    _send_string(password)
    _recv_exception_check()
    return _recv_object(OnlineExperiments, nullable=False)


# [[matt.oexp.front.api.ApiKt#ping]]
def ping():
    _ensure_synchronized()
    _check_required_parameters(**dict())
    jbridge._init_java()
    _sendall(CALL_GLOBAL_FUN)
    _send_string(f"matt.oexp.front.api.ApiKt")
    _send_string(f"ping")
    _recv_exception_check()
    return _recv_confirmation()


class KBClass(abc.ABC):
    def __str__(self):
        return f"{type(self)} with id {self._id}"


class KBVClass(KBClass, abc.ABC):
    pass


class KBDClass(KBClass, abc.ABC):
    pass


class KBObject(KBClass, abc.ABC):
    pass


def degrees(value=NO_DEFAULT):
    _check_required_parameters(**dict(value=value))
    return Degrees(value)


# [[matt.model.data.sensemod.Degrees]]
class Degrees(KBDClass):
    def __init__(self, *args, _id=None):
        _ensure_synchronized()
        if _id is None:
            jbridge._init_java()
            _sendall(CREATE_OBJECT)
            _send_string("matt.model.data.sensemod.Degrees")
            _send_int(args[0])
            self._id = _object_id(_recv_long())
        else:
            self._id = _object_id(_id)

    # [[matt.model.data.sensemod.Degrees#value]]
    @property
    def value(self) -> int:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(0)
        temp = _recv_int(nullable=False)
        return temp

    # [[matt.model.data.sensemod.Degrees]]
    def to_json(self):
        _ensure_synchronized()
        _sendall(GET_JSON)
        _send_long(self._id._id)
        return _recv_string(nullable=False)

    # [[matt.model.data.sensemod.Degrees]]
    def to_dict(self):
        return json.loads(self.to_json())

    # [[matt.model.data.sensemod.Degrees]]
    def to_data(self):
        from mstuff.mstuff import Obj

        return Obj(self.to_dict())

    # [[matt.model.data.sensemod.Degrees]]
    def __eq__(self, other):
        _ensure_synchronized()
        if isinstance(other, KBClass):
            _sendall(CHECK_EQUALITY)
            _send_long(self._id._id)
            _send_long(other._id._id)
            return _recv_bool()
        else:
            return False


def degrees_double(value=NO_DEFAULT):
    _check_required_parameters(**dict(value=value))
    return DegreesDouble(value)


# [[matt.model.data.sensemod.DegreesDouble]]
class DegreesDouble(KBVClass):
    def __init__(self, *args, _id=None):
        _ensure_synchronized()
        if _id is None:
            jbridge._init_java()
            _sendall(CREATE_OBJECT)
            _send_string("matt.model.data.sensemod.DegreesDouble")
            _send_double(args[0])
            self._id = _object_id(_recv_long())
        else:
            self._id = _object_id(_id)

    # [[matt.model.data.sensemod.DegreesDouble#value]]
    @property
    def value(self) -> float:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(0)
        temp = _recv_double(nullable=False)
        return temp

    # [[matt.model.data.sensemod.DegreesDouble#round]]
    def round(self) -> Degrees:
        _ensure_synchronized()
        _check_required_parameters(**dict())
        _sendall(CALL_FUN)
        _send_long(self._id._id)
        _send_int(0)
        _recv_exception_check()
        return _recv_object(Degrees, nullable=False)

    # [[matt.model.data.sensemod.DegreesDouble]]
    def to_json(self):
        _ensure_synchronized()
        _sendall(GET_JSON)
        _send_long(self._id._id)
        return _recv_string(nullable=False)

    # [[matt.model.data.sensemod.DegreesDouble]]
    def to_dict(self):
        return json.loads(self.to_json())

    # [[matt.model.data.sensemod.DegreesDouble]]
    def to_data(self):
        from mstuff.mstuff import Obj

        return Obj(self.to_dict())

    # [[matt.model.data.sensemod.DegreesDouble]]
    def __eq__(self, other):
        _ensure_synchronized()
        return type(other) == type(self) and other.value == self.value


# [[matt.oexp.front.api.API]]
class API(KBObject):
    _id = None

    @staticmethod
    def _init():
        _ensure_synchronized()
        if API._id is None:
            jbridge._init_java()
            _sendall(INIT_OBJECT)
            _send_string("matt.oexp.front.api.API")
            API._id = _object_id(_recv_long())

    # [[matt.oexp.front.api.API#enableLocalMode]]
    def enable_local_mode(self, port=NO_DEFAULT):
        _ensure_synchronized()
        _check_required_parameters(**dict(port=port))
        API._init()
        _sendall(CALL_FUN)
        _send_long(self._id._id)
        _send_int(0)
        _send_int(port)
        _recv_exception_check()
        return _recv_confirmation()

    # [[matt.oexp.front.api.API#enableStageMode]]
    def enable_stage_mode(self, token=NO_DEFAULT):
        _ensure_synchronized()
        _check_required_parameters(**dict(token=token))
        API._init()
        _sendall(CALL_FUN)
        _send_long(self._id._id)
        _send_int(1)
        _send_string(token)
        _recv_exception_check()
        return _recv_confirmation()

    # [[matt.oexp.front.api.API]]
    def __eq__(self, other):
        _ensure_synchronized()
        return type(other) == type(self)


API = API()
# [[matt.oexp.front.api.BridgeJob]]
class BridgeJob(KBClass):
    def __init__(self, _id=None):
        _ensure_synchronized()
        if _id is None:
            raise Exception(f"id must not be None")
        else:
            self._id = _object_id(_id)

    # [[matt.oexp.front.api.BridgeJob#join]]
    def join(self):
        _ensure_synchronized()
        _check_required_parameters(**dict())
        _sendall(CALL_FUN)
        _send_long(self._id._id)
        _send_int(0)
        _recv_exception_check()
        return _recv_confirmation()

    # [[matt.oexp.front.api.BridgeJob]]
    def __eq__(self, other):
        _ensure_synchronized()
        if isinstance(other, KBClass):
            _sendall(CHECK_EQUALITY)
            _send_long(self._id._id)
            _send_long(other._id._id)
            return _recv_bool()
        else:
            return False


def experiment(user=NO_DEFAULT, uid=NO_DEFAULT):
    _check_required_parameters(**dict(user=user, uid=uid))
    return Experiment(user, uid)


# [[matt.oexp.front.api.Experiment]]
class Experiment(KBDClass):
    def __init__(self, *args, _id=None):
        _ensure_synchronized()
        if _id is None:
            jbridge._init_java()
            _sendall(CREATE_OBJECT)
            _send_string("matt.oexp.front.api.Experiment")
            _send_long(args[0]._id._id)
            _send_long(args[1])
            self._id = _object_id(_recv_long())
        else:
            self._id = _object_id(_id)

    # [[matt.oexp.front.api.Experiment#css]]
    @property
    def css(self) -> Optional[str]:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(0)
        temp = _recv_string(nullable=True)
        return temp

    @css.setter
    def css(self, value) -> Optional[str]:
        _ensure_synchronized()
        _sendall(SET_VAR)
        _send_long(self._id._id)
        _send_int(0)
        if value is None:
            _sendall(b"\x00")
        else:
            _sendall(b"\x01")
        if value is not None:
            _send_string(value)
        _recv_confirmation()

    # [[matt.oexp.front.api.Experiment#manifests]]
    @property
    def manifests(self) -> Optional[List[TrialManifest]]:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(1)
        temp = _recv_list(
            elementReceiveFun=lambda: _recv_object(TrialManifest, nullable=False),
            nullable=True,
        )
        return temp

    @manifests.setter
    def manifests(self, value) -> Optional[List[TrialManifest]]:
        _ensure_synchronized()
        _sendall(SET_VAR)
        _send_long(self._id._id)
        _send_int(1)
        if value is None:
            _sendall(b"\x00")
        else:
            _sendall(b"\x01")
        if value is not None:
            _send_int(len(value))
            for e in value:
                _send_long(e._id._id)
        _recv_confirmation()

    # [[matt.oexp.front.api.Experiment#name]]
    @property
    def name(self) -> str:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(2)
        temp = _recv_string(nullable=False)
        return temp

    @name.setter
    def name(self, value) -> str:
        _ensure_synchronized()
        _sendall(SET_VAR)
        _send_long(self._id._id)
        _send_int(2)
        _send_string(value)
        _recv_confirmation()

    # [[matt.oexp.front.api.Experiment#scss]]
    @property
    def scss(self) -> Optional[str]:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(3)
        temp = _recv_string(nullable=True)
        return temp

    @scss.setter
    def scss(self, value) -> Optional[str]:
        _ensure_synchronized()
        _sendall(SET_VAR)
        _send_long(self._id._id)
        _send_int(3)
        if value is None:
            _sendall(b"\x00")
        else:
            _sendall(b"\x01")
        if value is not None:
            _send_string(value)
        _recv_confirmation()

    # [[matt.oexp.front.api.Experiment#uid]]
    @property
    def uid(self) -> int:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(4)
        temp = _recv_long(nullable=False)
        return temp

    # [[matt.oexp.front.api.Experiment#user]]
    @property
    def user(self) -> OnlineExperiments:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(5)
        temp = _recv_object(OnlineExperiments, nullable=False)
        return temp

    # [[matt.oexp.front.api.Experiment#delete]]
    def delete(self):
        _ensure_synchronized()
        _check_required_parameters(**dict())
        _sendall(CALL_FUN)
        _send_long(self._id._id)
        _send_int(0)
        _recv_exception_check()
        return _recv_confirmation()

    # [[matt.oexp.front.api.Experiment#deleteAllImages]]
    def delete_all_images(self):
        _ensure_synchronized()
        _check_required_parameters(**dict())
        _sendall(CALL_FUN)
        _send_long(self._id._id)
        _send_int(1)
        _recv_exception_check()
        return _recv_confirmation()

    # [[matt.oexp.front.api.Experiment#deleteSubjectData]]
    def delete_subject_data(self):
        _ensure_synchronized()
        _check_required_parameters(**dict())
        _sendall(CALL_FUN)
        _send_long(self._id._id)
        _send_int(2)
        _recv_exception_check()
        return _recv_confirmation()

    # [[matt.oexp.front.api.Experiment#deleteUnusedImages]]
    def delete_unused_images(self):
        _ensure_synchronized()
        _check_required_parameters(**dict())
        _sendall(CALL_FUN)
        _send_long(self._id._id)
        _send_int(3)
        _recv_exception_check()
        return _recv_confirmation()

    # [[matt.oexp.front.api.Experiment#generateImageUrl]]
    def generate_image_url(self, path=NO_DEFAULT) -> str:
        _ensure_synchronized()
        _check_required_parameters(**dict(path=path))
        _sendall(CALL_FUN)
        _send_long(self._id._id)
        _send_int(4)
        _send_string(path)
        _recv_exception_check()
        return _recv_string(nullable=False)

    # [[matt.oexp.front.api.Experiment#hotCss]]
    def hot_css(self, file=NO_DEFAULT):
        _ensure_synchronized()
        _check_required_parameters(**dict(file=file))
        _sendall(CALL_FUN)
        _send_long(self._id._id)
        _send_int(5)
        _send_string(file)
        _recv_exception_check()
        return _recv_confirmation()

    # [[matt.oexp.front.api.Experiment#imageUploadSession]]
    def image_upload_session(self) -> ImageUploadSession:
        _ensure_synchronized()
        _check_required_parameters(**dict())
        _sendall(CALL_FUN)
        _send_long(self._id._id)
        _send_int(6)
        _recv_exception_check()
        return _recv_object(ImageUploadSession, nullable=False)

    # [[matt.oexp.front.api.Experiment#linkProlific]]
    def link_prolific(self, prolific_study_id=NO_DEFAULT):
        _ensure_synchronized()
        _check_required_parameters(**dict(prolific_study_id=prolific_study_id))
        _sendall(CALL_FUN)
        _send_long(self._id._id)
        _send_int(7)
        _send_string(prolific_study_id)
        _recv_exception_check()
        return _recv_confirmation()

    # [[matt.oexp.front.api.Experiment#listImages]]
    def list_images(self) -> List[str]:
        _ensure_synchronized()
        _check_required_parameters(**dict())
        _sendall(CALL_FUN)
        _send_long(self._id._id)
        _send_int(8)
        _recv_exception_check()
        return _recv_list(
            elementReceiveFun=lambda: _recv_string(nullable=False), nullable=False
        )

    # [[matt.oexp.front.api.Experiment#open]]
    def open(
        self,
        disable_auto_fullscreen=DEFAULT_VALUE,
        allow_fullscreen_exit=DEFAULT_VALUE,
        hot_css=DEFAULT_VALUE,
        man_num=DEFAULT_VALUE,
    ):
        _ensure_synchronized()
        _check_required_parameters(**dict())
        _sendall(CALL_FUN)
        _send_long(self._id._id)
        _send_int(9)
        if disable_auto_fullscreen == DEFAULT_VALUE:
            _sendall(b"\x00")
        else:
            _sendall(b"\x01")
            if disable_auto_fullscreen:
                _sendall(b"\x01")
            else:
                _sendall(b"\x00")
        if allow_fullscreen_exit == DEFAULT_VALUE:
            _sendall(b"\x00")
        else:
            _sendall(b"\x01")
            if allow_fullscreen_exit:
                _sendall(b"\x01")
            else:
                _sendall(b"\x00")
        if hot_css == DEFAULT_VALUE:
            _sendall(b"\x00")
        else:
            _sendall(b"\x01")
            if hot_css:
                _sendall(b"\x01")
            else:
                _sendall(b"\x00")
        if man_num == DEFAULT_VALUE:
            _sendall(b"\x00")
        else:
            _sendall(b"\x01")
            if man_num is None:
                _sendall(b"\x00")
            else:
                _sendall(b"\x01")
            if man_num is not None:
                _send_int(man_num)
        _recv_exception_check()
        return _recv_confirmation()

    # [[matt.oexp.front.api.Experiment#openProlific]]
    def open_prolific(self):
        _ensure_synchronized()
        _check_required_parameters(**dict())
        _sendall(CALL_FUN)
        _send_long(self._id._id)
        _send_int(10)
        _recv_exception_check()
        return _recv_confirmation()

    # [[matt.oexp.front.api.Experiment#sessionUrl]]
    def session_url(
        self,
        disable_auto_fullscreen=DEFAULT_VALUE,
        allow_fullscreen_exit=DEFAULT_VALUE,
        hot_css=DEFAULT_VALUE,
        man_num=DEFAULT_VALUE,
    ) -> str:
        _ensure_synchronized()
        _check_required_parameters(**dict())
        _sendall(CALL_FUN)
        _send_long(self._id._id)
        _send_int(11)
        if disable_auto_fullscreen == DEFAULT_VALUE:
            _sendall(b"\x00")
        else:
            _sendall(b"\x01")
            if disable_auto_fullscreen:
                _sendall(b"\x01")
            else:
                _sendall(b"\x00")
        if allow_fullscreen_exit == DEFAULT_VALUE:
            _sendall(b"\x00")
        else:
            _sendall(b"\x01")
            if allow_fullscreen_exit:
                _sendall(b"\x01")
            else:
                _sendall(b"\x00")
        if hot_css == DEFAULT_VALUE:
            _sendall(b"\x00")
        else:
            _sendall(b"\x01")
            if hot_css:
                _sendall(b"\x01")
            else:
                _sendall(b"\x00")
        if man_num == DEFAULT_VALUE:
            _sendall(b"\x00")
        else:
            _sendall(b"\x01")
            if man_num is None:
                _sendall(b"\x00")
            else:
                _sendall(b"\x01")
            if man_num is not None:
                _send_int(man_num)
        _recv_exception_check()
        return _recv_string(nullable=False)

    # [[matt.oexp.front.api.Experiment#subjectData]]
    def subject_data(self) -> SubjectData:
        _ensure_synchronized()
        _check_required_parameters(**dict())
        _sendall(CALL_FUN)
        _send_long(self._id._id)
        _send_int(12)
        _recv_exception_check()
        return _recv_object(SubjectData, nullable=False)

    # [[matt.oexp.front.api.Experiment#uploadImage]]
    def upload_image(self, local_abs_path=NO_DEFAULT, remote_rel_path=NO_DEFAULT):
        _ensure_synchronized()
        _check_required_parameters(
            **dict(local_abs_path=local_abs_path, remote_rel_path=remote_rel_path)
        )
        _sendall(CALL_FUN)
        _send_long(self._id._id)
        _send_int(13)
        _send_string(local_abs_path)
        _send_string(remote_rel_path)
        _recv_exception_check()
        return _recv_confirmation()

    # [[matt.oexp.front.api.Experiment#uploadImageAsync]]
    def upload_image_async(
        self, local_abs_path=NO_DEFAULT, remote_rel_path=NO_DEFAULT
    ) -> BridgeJob:
        _ensure_synchronized()
        _check_required_parameters(
            **dict(local_abs_path=local_abs_path, remote_rel_path=remote_rel_path)
        )
        _sendall(CALL_FUN)
        _send_long(self._id._id)
        _send_int(14)
        _send_string(local_abs_path)
        _send_string(remote_rel_path)
        _recv_exception_check()
        return _recv_object(BridgeJob, nullable=False)

    # [[matt.oexp.front.api.Experiment#uploadImages]]
    def upload_images(self, root_dir=NO_DEFAULT) -> List[str]:
        _ensure_synchronized()
        _check_required_parameters(**dict(root_dir=root_dir))
        _sendall(CALL_FUN)
        _send_long(self._id._id)
        _send_int(15)
        _send_string(root_dir)
        _recv_exception_check()
        return _recv_list(
            elementReceiveFun=lambda: _recv_string(nullable=False), nullable=False
        )

    # [[matt.oexp.front.api.Experiment#viewImage]]
    def view_image(self, path=NO_DEFAULT):
        _ensure_synchronized()
        _check_required_parameters(**dict(path=path))
        _sendall(CALL_FUN)
        _send_long(self._id._id)
        _send_int(16)
        _send_string(path)
        _recv_exception_check()
        return _recv_confirmation()

    # [[matt.oexp.front.api.Experiment]]
    def __eq__(self, other):
        _ensure_synchronized()
        if isinstance(other, KBClass):
            _sendall(CHECK_EQUALITY)
            _send_long(self._id._id)
            _send_long(other._id._id)
            return _recv_bool()
        else:
            return False


def online_experiments(username=NO_DEFAULT, password=NO_DEFAULT):
    _check_required_parameters(**dict(username=username, password=password))
    return OnlineExperiments(username, password)


# [[matt.oexp.front.api.OnlineExperiments]]
class OnlineExperiments(KBDClass):
    def __init__(self, *args, _id=None):
        _ensure_synchronized()
        if _id is None:
            jbridge._init_java()
            _sendall(CREATE_OBJECT)
            _send_string("matt.oexp.front.api.OnlineExperiments")
            _send_string(args[0])
            _send_string(args[1])
            self._id = _object_id(_recv_long())
        else:
            self._id = _object_id(_id)

    # [[matt.oexp.front.api.OnlineExperiments#password]]
    @property
    def password(self) -> str:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(0)
        temp = _recv_string(nullable=False)
        return temp

    # [[matt.oexp.front.api.OnlineExperiments#prolificKey]]
    @property
    def prolific_key(self) -> str:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(1)
        temp = _recv_string(nullable=False)
        return temp

    @prolific_key.setter
    def prolific_key(self, value) -> str:
        _ensure_synchronized()
        _sendall(SET_VAR)
        _send_long(self._id._id)
        _send_int(1)
        _send_string(value)
        _recv_confirmation()

    # [[matt.oexp.front.api.OnlineExperiments#username]]
    @property
    def username(self) -> str:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(2)
        temp = _recv_string(nullable=False)
        return temp

    # [[matt.oexp.front.api.OnlineExperiments#changePassword]]
    def change_password(self, new_password=NO_DEFAULT):
        _ensure_synchronized()
        _check_required_parameters(**dict(new_password=new_password))
        _sendall(CALL_FUN)
        _send_long(self._id._id)
        _send_int(0)
        _send_string(new_password)
        _recv_exception_check()
        return _recv_confirmation()

    # [[matt.oexp.front.api.OnlineExperiments#experiment]]
    def experiment(self, name=NO_DEFAULT) -> Experiment:
        _ensure_synchronized()
        _check_required_parameters(**dict(name=name))
        _sendall(CALL_FUN)
        _send_long(self._id._id)
        _send_int(1)
        _send_string(name)
        _recv_exception_check()
        return _recv_object(Experiment, nullable=False)

    # [[matt.oexp.front.api.OnlineExperiments#experimentWithUid]]
    def experiment_with_uid(self, uid=NO_DEFAULT) -> Experiment:
        _ensure_synchronized()
        _check_required_parameters(**dict(uid=uid))
        _sendall(CALL_FUN)
        _send_long(self._id._id)
        _send_int(2)
        _send_long(uid._id._id)
        _recv_exception_check()
        return _recv_object(Experiment, nullable=False)

    # [[matt.oexp.front.api.OnlineExperiments#listExperimentData]]
    def list_experiment_data(self) -> List[ExperimentConfig]:
        _ensure_synchronized()
        _check_required_parameters(**dict())
        _sendall(CALL_FUN)
        _send_long(self._id._id)
        _send_int(3)
        _recv_exception_check()
        return _recv_list(
            elementReceiveFun=lambda: _recv_object(ExperimentConfig, nullable=False),
            nullable=False,
        )

    # [[matt.oexp.front.api.OnlineExperiments#listExperiments]]
    def list_experiments(self) -> List[Experiment]:
        _ensure_synchronized()
        _check_required_parameters(**dict())
        _sendall(CALL_FUN)
        _send_long(self._id._id)
        _send_int(4)
        _recv_exception_check()
        return _recv_list(
            elementReceiveFun=lambda: _recv_object(Experiment, nullable=False),
            nullable=False,
        )

    # [[matt.oexp.front.api.OnlineExperiments]]
    def __eq__(self, other):
        _ensure_synchronized()
        if isinstance(other, KBClass):
            _sendall(CHECK_EQUALITY)
            _send_long(self._id._id)
            _send_long(other._id._id)
            return _recv_bool()
        else:
            return False


def image_upload_session(experiment=NO_DEFAULT):
    _check_required_parameters(**dict(experiment=experiment))
    return ImageUploadSession(experiment)


# [[matt.oexp.front.api.upload.ImageUploadSession]]
class ImageUploadSession(KBClass):
    def __init__(self, *args, _id=None):
        _ensure_synchronized()
        if _id is None:
            jbridge._init_java()
            _sendall(CREATE_OBJECT)
            _send_string("matt.oexp.front.api.upload.ImageUploadSession")
            _send_long(args[0]._id._id)
            self._id = _object_id(_recv_long())
        else:
            self._id = _object_id(_id)

    # [[matt.oexp.front.api.upload.ImageUploadSession#close]]
    def close(self):
        _ensure_synchronized()
        _check_required_parameters(**dict())
        _sendall(CALL_FUN)
        _send_long(self._id._id)
        _send_int(0)
        _recv_exception_check()
        return _recv_confirmation()

    # [[matt.oexp.front.api.upload.ImageUploadSession#uploadImageAsyncEfficient]]
    def upload_image_async_efficient(
        self, local_abs_path=NO_DEFAULT, remote_rel_path=NO_DEFAULT
    ) -> BridgeJob:
        _ensure_synchronized()
        _check_required_parameters(
            **dict(local_abs_path=local_abs_path, remote_rel_path=remote_rel_path)
        )
        _sendall(CALL_FUN)
        _send_long(self._id._id)
        _send_int(1)
        _send_string(local_abs_path)
        _send_string(remote_rel_path)
        _recv_exception_check()
        return _recv_object(BridgeJob, nullable=False)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    # [[matt.oexp.front.api.upload.ImageUploadSession]]
    def __eq__(self, other):
        _ensure_synchronized()
        if isinstance(other, KBClass):
            _sendall(CHECK_EQUALITY)
            _send_long(self._id._id)
            _send_long(other._id._id)
            return _recv_bool()
        else:
            return False


def experiment_config(
    uid=NO_DEFAULT,
    name=NO_DEFAULT,
    manifests=DEFAULT_VALUE,
    prolific_study_id=DEFAULT_VALUE,
    css=DEFAULT_VALUE,
):
    _check_required_parameters(**dict(uid=uid, name=name))
    return ExperimentConfig(uid, name, manifests, prolific_study_id, css)


# [[matt.oexp.olang.lab.model.ExperimentConfig]]
class ExperimentConfig(KBDClass):
    def __init__(self, *args, _id=None):
        _ensure_synchronized()
        if _id is None:
            jbridge._init_java()
            _sendall(CREATE_OBJECT)
            _send_string("matt.oexp.olang.lab.model.ExperimentConfig")
            _send_long(args[0]._id._id)
            _send_string(args[1])
            if args[2] == DEFAULT_VALUE:
                _sendall(b"\x00")
            else:
                _sendall(b"\x01")
                if args[2] is None:
                    _sendall(b"\x00")
                else:
                    _sendall(b"\x01")
                if args[2] is not None:
                    _send_int(len(args[2]))
                    for e in args[2]:
                        _send_long(e._id._id)
            if args[3] == DEFAULT_VALUE:
                _sendall(b"\x00")
            else:
                _sendall(b"\x01")
                if args[3] is None:
                    _sendall(b"\x00")
                else:
                    _sendall(b"\x01")
                if args[3] is not None:
                    _send_long(args[3]._id._id)
            if args[4] == DEFAULT_VALUE:
                _sendall(b"\x00")
            else:
                _sendall(b"\x01")
                if args[4] is None:
                    _sendall(b"\x00")
                else:
                    _sendall(b"\x01")
                if args[4] is not None:
                    _send_string(args[4])
            self._id = _object_id(_recv_long())
        else:
            self._id = _object_id(_id)

    # [[matt.oexp.olang.lab.model.ExperimentConfig#css]]
    @property
    def css(self) -> Optional[str]:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(0)
        temp = _recv_string(nullable=True)
        return temp

    # [[matt.oexp.olang.lab.model.ExperimentConfig#manifestCount]]
    @property
    def manifest_count(self) -> Optional[int]:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(1)
        temp = _recv_int(nullable=True)
        return temp

    # [[matt.oexp.olang.lab.model.ExperimentConfig#manifests]]
    @property
    def manifests(self) -> Optional[List[TrialManifest]]:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(2)
        temp = _recv_list(
            elementReceiveFun=lambda: _recv_object(TrialManifest, nullable=False),
            nullable=True,
        )
        return temp

    # [[matt.oexp.olang.lab.model.ExperimentConfig#name]]
    @property
    def name(self) -> str:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(3)
        temp = _recv_string(nullable=False)
        return temp

    # [[matt.oexp.olang.lab.model.ExperimentConfig#prolificStudyID]]
    @property
    def prolific_study_id(self) -> Optional[ProlificStudyId]:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(4)
        temp = _recv_object(ProlificStudyId, nullable=True)
        return temp

    # [[matt.oexp.olang.lab.model.ExperimentConfig#uid]]
    @property
    def uid(self) -> ExperimentUid:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(5)
        temp = _recv_object(ExperimentUid, nullable=False)
        return temp

    # [[matt.oexp.olang.lab.model.ExperimentConfig#willProvideAManifest]]
    @property
    def will_provide_a_manifest(self) -> bool:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(6)
        temp = _recv_bool(nullable=False)
        return temp

    # [[matt.oexp.olang.lab.model.ExperimentConfig]]
    def to_json(self):
        _ensure_synchronized()
        _sendall(GET_JSON)
        _send_long(self._id._id)
        return _recv_string(nullable=False)

    # [[matt.oexp.olang.lab.model.ExperimentConfig]]
    def to_dict(self):
        return json.loads(self.to_json())

    # [[matt.oexp.olang.lab.model.ExperimentConfig]]
    def to_data(self):
        from mstuff.mstuff import Obj

        return Obj(self.to_dict())

    # [[matt.oexp.olang.lab.model.ExperimentConfig]]
    def __eq__(self, other):
        _ensure_synchronized()
        if isinstance(other, KBClass):
            _sendall(CHECK_EQUALITY)
            _send_long(self._id._id)
            _send_long(other._id._id)
            return _recv_bool()
        else:
            return False


def experiment_config_patch(
    name=DEFAULT_VALUE,
    manifests=DEFAULT_VALUE,
    prolific_study_id=DEFAULT_VALUE,
    css=DEFAULT_VALUE,
):
    _check_required_parameters(**dict())
    return ExperimentConfigPatch(name, manifests, prolific_study_id, css)


# [[matt.oexp.olang.lab.model.ExperimentConfigPatch]]
class ExperimentConfigPatch(KBDClass):
    def __init__(self, *args, _id=None):
        _ensure_synchronized()
        if _id is None:
            jbridge._init_java()
            _sendall(CREATE_OBJECT)
            _send_string("matt.oexp.olang.lab.model.ExperimentConfigPatch")
            if args[0] == DEFAULT_VALUE:
                _sendall(b"\x00")
            else:
                _sendall(b"\x01")
                if args[0] is None:
                    _sendall(b"\x00")
                else:
                    _sendall(b"\x01")
                if args[0] is not None:
                    _send_string(args[0])
            if args[1] == DEFAULT_VALUE:
                _sendall(b"\x00")
            else:
                _sendall(b"\x01")
                if args[1] is None:
                    _sendall(b"\x00")
                else:
                    _sendall(b"\x01")
                if args[1] is not None:
                    _send_int(len(args[1]))
                    for e in args[1]:
                        _send_long(e._id._id)
            if args[2] == DEFAULT_VALUE:
                _sendall(b"\x00")
            else:
                _sendall(b"\x01")
                if args[2] is None:
                    _sendall(b"\x00")
                else:
                    _sendall(b"\x01")
                if args[2] is not None:
                    _send_long(args[2]._id._id)
            if args[3] == DEFAULT_VALUE:
                _sendall(b"\x00")
            else:
                _sendall(b"\x01")
                if args[3] is None:
                    _sendall(b"\x00")
                else:
                    _sendall(b"\x01")
                if args[3] is not None:
                    _send_string(args[3])
            self._id = _object_id(_recv_long())
        else:
            self._id = _object_id(_id)

    # [[matt.oexp.olang.lab.model.ExperimentConfigPatch#css]]
    @property
    def css(self) -> Optional[str]:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(0)
        temp = _recv_string(nullable=True)
        return temp

    # [[matt.oexp.olang.lab.model.ExperimentConfigPatch#manifests]]
    @property
    def manifests(self) -> Optional[List[TrialManifest]]:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(1)
        temp = _recv_list(
            elementReceiveFun=lambda: _recv_object(TrialManifest, nullable=False),
            nullable=True,
        )
        return temp

    # [[matt.oexp.olang.lab.model.ExperimentConfigPatch#name]]
    @property
    def name(self) -> Optional[str]:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(2)
        temp = _recv_string(nullable=True)
        return temp

    # [[matt.oexp.olang.lab.model.ExperimentConfigPatch#prolificStudyID]]
    @property
    def prolific_study_id(self) -> Optional[ProlificStudyId]:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(3)
        temp = _recv_object(ProlificStudyId, nullable=True)
        return temp

    # [[matt.oexp.olang.lab.model.ExperimentConfigPatch#patch]]
    def patch(self, experiment_config=NO_DEFAULT) -> ExperimentConfig:
        _ensure_synchronized()
        _check_required_parameters(**dict(experiment_config=experiment_config))
        _sendall(CALL_FUN)
        _send_long(self._id._id)
        _send_int(0)
        _send_long(experiment_config._id._id)
        _recv_exception_check()
        return _recv_object(ExperimentConfig, nullable=False)

    # [[matt.oexp.olang.lab.model.ExperimentConfigPatch]]
    def to_json(self):
        _ensure_synchronized()
        _sendall(GET_JSON)
        _send_long(self._id._id)
        return _recv_string(nullable=False)

    # [[matt.oexp.olang.lab.model.ExperimentConfigPatch]]
    def to_dict(self):
        return json.loads(self.to_json())

    # [[matt.oexp.olang.lab.model.ExperimentConfigPatch]]
    def to_data(self):
        from mstuff.mstuff import Obj

        return Obj(self.to_dict())

    # [[matt.oexp.olang.lab.model.ExperimentConfigPatch]]
    def __eq__(self, other):
        _ensure_synchronized()
        if isinstance(other, KBClass):
            _sendall(CHECK_EQUALITY)
            _send_long(self._id._id)
            _send_long(other._id._id)
            return _recv_bool()
        else:
            return False


def subject(id=NO_DEFAULT, demographic=DEFAULT_VALUE, events=DEFAULT_VALUE):
    _check_required_parameters(**dict(id=id))
    return Subject(id, demographic, events)


# [[matt.oexp.olang.lab.model.Subject]]
class Subject(KBClass):
    def __init__(self, *args, _id=None):
        _ensure_synchronized()
        if _id is None:
            jbridge._init_java()
            _sendall(CREATE_OBJECT)
            _send_string("matt.oexp.olang.lab.model.Subject")
            _send_long(args[0]._id._id)
            if args[1] == DEFAULT_VALUE:
                _sendall(b"\x00")
            else:
                _sendall(b"\x01")
                _send_int(len(args[1]))
                for e in args[1]:
                    _send_long(e._id._id)
            if args[2] == DEFAULT_VALUE:
                _sendall(b"\x00")
            else:
                _sendall(b"\x01")
                _send_int(len(args[2]))
                for e in args[2]:
                    _send_long(e._id._id)
            self._id = _object_id(_recv_long())
        else:
            self._id = _object_id(_id)

    # [[matt.oexp.olang.lab.model.Subject#demographic]]
    @property
    def demographic(self) -> List[SubjectDemographicData]:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(0)
        temp = _recv_list(
            elementReceiveFun=lambda: _recv_object(
                SubjectDemographicData, nullable=False
            ),
            nullable=False,
        )
        return temp

    # [[matt.oexp.olang.lab.model.Subject#events]]
    @property
    def events(self) -> List[ExperimentEvent]:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(1)
        temp = _recv_list(
            elementReceiveFun=lambda: _recv_object(ExperimentEvent, nullable=False),
            nullable=False,
        )
        return temp

    # [[matt.oexp.olang.lab.model.Subject#id]]
    @property
    def id(self) -> ProlificParticipantUid:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(2)
        temp = _recv_object(ProlificParticipantUid, nullable=False)
        return temp

    # [[matt.oexp.olang.lab.model.Subject]]
    def to_json(self):
        _ensure_synchronized()
        _sendall(GET_JSON)
        _send_long(self._id._id)
        return _recv_string(nullable=False)

    # [[matt.oexp.olang.lab.model.Subject]]
    def to_dict(self):
        return json.loads(self.to_json())

    # [[matt.oexp.olang.lab.model.Subject]]
    def to_data(self):
        from mstuff.mstuff import Obj

        return Obj(self.to_dict())

    # [[matt.oexp.olang.lab.model.Subject]]
    def __eq__(self, other):
        _ensure_synchronized()
        if isinstance(other, KBClass):
            _sendall(CHECK_EQUALITY)
            _send_long(self._id._id)
            _send_long(other._id._id)
            return _recv_bool()
        else:
            return False


def subject_data(data_version=DEFAULT_VALUE, subjects=DEFAULT_VALUE):
    _check_required_parameters(**dict())
    return SubjectData(data_version, subjects)


# [[matt.oexp.olang.lab.model.SubjectData]]
class SubjectData(KBClass):
    def __init__(self, *args, _id=None):
        _ensure_synchronized()
        if _id is None:
            jbridge._init_java()
            _sendall(CREATE_OBJECT)
            _send_string("matt.oexp.olang.lab.model.SubjectData")
            if args[0] == DEFAULT_VALUE:
                _sendall(b"\x00")
            else:
                _sendall(b"\x01")
                _send_int(args[0])
            if args[1] == DEFAULT_VALUE:
                _sendall(b"\x00")
            else:
                _sendall(b"\x01")
                _send_int(len(args[1]))
                for e in args[1]:
                    _send_long(e._id._id)
            self._id = _object_id(_recv_long())
        else:
            self._id = _object_id(_id)

    # [[matt.oexp.olang.lab.model.SubjectData#dataVersion]]
    @property
    def data_version(self) -> int:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(0)
        temp = _recv_int(nullable=False)
        return temp

    # [[matt.oexp.olang.lab.model.SubjectData#subjects]]
    @property
    def subjects(self) -> List[Subject]:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(1)
        temp = _recv_list(
            elementReceiveFun=lambda: _recv_object(Subject, nullable=False),
            nullable=False,
        )
        return temp

    # [[matt.oexp.olang.lab.model.SubjectData]]
    def to_json(self):
        _ensure_synchronized()
        _sendall(GET_JSON)
        _send_long(self._id._id)
        return _recv_string(nullable=False)

    # [[matt.oexp.olang.lab.model.SubjectData]]
    def to_dict(self):
        return json.loads(self.to_json())

    # [[matt.oexp.olang.lab.model.SubjectData]]
    def to_data(self):
        from mstuff.mstuff import Obj

        return Obj(self.to_dict())

    # [[matt.oexp.olang.lab.model.SubjectData]]
    def __eq__(self, other):
        _ensure_synchronized()
        if isinstance(other, KBClass):
            _sendall(CHECK_EQUALITY)
            _send_long(self._id._id)
            _send_long(other._id._id)
            return _recv_bool()
        else:
            return False


def subject_demographic_data(
    prolific_pid=NO_DEFAULT,
    session_id=DEFAULT_VALUE,
    birth_year=NO_DEFAULT,
    birth_month=NO_DEFAULT,
    gender=NO_DEFAULT,
    ethnicity=NO_DEFAULT,
):
    _check_required_parameters(
        **dict(
            prolific_pid=prolific_pid,
            birth_year=birth_year,
            birth_month=birth_month,
            gender=gender,
            ethnicity=ethnicity,
        )
    )
    return SubjectDemographicData(
        prolific_pid, session_id, birth_year, birth_month, gender, ethnicity
    )


# [[matt.oexp.olang.lab.model.SubjectDemographicData]]
class SubjectDemographicData(KBClass):
    def __init__(self, *args, _id=None):
        _ensure_synchronized()
        if _id is None:
            jbridge._init_java()
            _sendall(CREATE_OBJECT)
            _send_string("matt.oexp.olang.lab.model.SubjectDemographicData")
            _send_long(args[0]._id._id)
            if args[1] == DEFAULT_VALUE:
                _sendall(b"\x00")
            else:
                _sendall(b"\x01")
                if args[1] is None:
                    _sendall(b"\x00")
                else:
                    _sendall(b"\x01")
                if args[1] is not None:
                    _send_long(args[1]._id._id)
            _send_string(args[2])
            _send_string(args[3])
            _send_string(args[4])
            _send_int(len(args[5]))
            for e in args[5]:
                _send_string(e)
            self._id = _object_id(_recv_long())
        else:
            self._id = _object_id(_id)

    # [[matt.oexp.olang.lab.model.SubjectDemographicData#birthMonth]]
    @property
    def birth_month(self) -> str:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(0)
        temp = _recv_string(nullable=False)
        return temp

    # [[matt.oexp.olang.lab.model.SubjectDemographicData#birthYear]]
    @property
    def birth_year(self) -> str:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(1)
        temp = _recv_string(nullable=False)
        return temp

    # [[matt.oexp.olang.lab.model.SubjectDemographicData#ethnicity]]
    @property
    def ethnicity(self) -> List[str]:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(2)
        temp = _recv_list(
            elementReceiveFun=lambda: _recv_string(nullable=False), nullable=False
        )
        return temp

    # [[matt.oexp.olang.lab.model.SubjectDemographicData#gender]]
    @property
    def gender(self) -> str:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(3)
        temp = _recv_string(nullable=False)
        return temp

    # [[matt.oexp.olang.lab.model.SubjectDemographicData#prolificPID]]
    @property
    def prolific_pid(self) -> ProlificParticipantUid:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(4)
        temp = _recv_object(ProlificParticipantUid, nullable=False)
        return temp

    # [[matt.oexp.olang.lab.model.SubjectDemographicData#sessionID]]
    @property
    def session_id(self) -> Optional[ProlificSessionId]:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(5)
        temp = _recv_object(ProlificSessionId, nullable=True)
        return temp

    # [[matt.oexp.olang.lab.model.SubjectDemographicData]]
    def to_json(self):
        _ensure_synchronized()
        _sendall(GET_JSON)
        _send_long(self._id._id)
        return _recv_string(nullable=False)

    # [[matt.oexp.olang.lab.model.SubjectDemographicData]]
    def to_dict(self):
        return json.loads(self.to_json())

    # [[matt.oexp.olang.lab.model.SubjectDemographicData]]
    def to_data(self):
        from mstuff.mstuff import Obj

        return Obj(self.to_dict())

    # [[matt.oexp.olang.lab.model.SubjectDemographicData]]
    def __eq__(self, other):
        _ensure_synchronized()
        if isinstance(other, KBClass):
            _sendall(CHECK_EQUALITY)
            _send_long(self._id._id)
            _send_long(other._id._id)
            return _recv_bool()
        else:
            return False


def trial_manifest(trials=NO_DEFAULT, skip=DEFAULT_VALUE, css_vars=DEFAULT_VALUE):
    _check_required_parameters(**dict(trials=trials))
    return TrialManifest(trials, skip, css_vars)


# [[matt.oexp.olang.lab.model.TrialManifest]]
class TrialManifest(KBDClass):
    def __init__(self, *args, _id=None):
        _ensure_synchronized()
        if _id is None:
            jbridge._init_java()
            _sendall(CREATE_OBJECT)
            _send_string("matt.oexp.olang.lab.model.TrialManifest")
            _send_int(len(args[0]))
            for e in args[0]:
                _send_long(e._id._id)
            if args[1] == DEFAULT_VALUE:
                _sendall(b"\x00")
            else:
                _sendall(b"\x01")
                if args[1]:
                    _sendall(b"\x01")
                else:
                    _sendall(b"\x00")
            if args[2] == DEFAULT_VALUE:
                _sendall(b"\x00")
            else:
                _sendall(b"\x01")
                if args[2] is None:
                    _sendall(b"\x00")
                else:
                    _sendall(b"\x01")
                if args[2] is not None:
                    _send_int(len(args[2]))
                    for k, v in args[2].items():
                        _send_string(k)
                        _send_string(v)
            self._id = _object_id(_recv_long())
        else:
            self._id = _object_id(_id)

    # [[matt.oexp.olang.lab.model.TrialManifest#cssVars]]
    @property
    def css_vars(self) -> Optional[Dict[str, str]]:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(0)
        temp = _recv_map(
            keyReceiveFun=lambda: _recv_string(nullable=False),
            valueReceiveFun=lambda: _recv_string(nullable=False),
            nullable=True,
        )
        return temp

    # [[matt.oexp.olang.lab.model.TrialManifest#skip]]
    @property
    def skip(self) -> bool:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(1)
        temp = _recv_bool(nullable=False)
        return temp

    # [[matt.oexp.olang.lab.model.TrialManifest#trials]]
    @property
    def trials(self) -> List[Phase]:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(2)
        temp = _recv_list(
            elementReceiveFun=lambda: _recv_object(Phase, nullable=False),
            nullable=False,
        )
        return temp

    # [[matt.oexp.olang.lab.model.TrialManifest]]
    def to_json(self):
        _ensure_synchronized()
        _sendall(GET_JSON)
        _send_long(self._id._id)
        return _recv_string(nullable=False)

    # [[matt.oexp.olang.lab.model.TrialManifest]]
    def to_dict(self):
        return json.loads(self.to_json())

    # [[matt.oexp.olang.lab.model.TrialManifest]]
    def to_data(self):
        from mstuff.mstuff import Obj

        return Obj(self.to_dict())

    # [[matt.oexp.olang.lab.model.TrialManifest]]
    def __eq__(self, other):
        _ensure_synchronized()
        if isinstance(other, KBClass):
            _sendall(CHECK_EQUALITY)
            _send_long(self._id._id)
            _send_long(other._id._id)
            return _recv_bool()
        else:
            return False


def choice(value=NO_DEFAULT, image=DEFAULT_VALUE, text=DEFAULT_VALUE):
    _check_required_parameters(**dict(value=value))
    return Choice(value, image, text)


# [[matt.oexp.olang.lab.model.trial.Choice]]
class Choice(KBDClass):
    def __init__(self, *args, _id=None):
        _ensure_synchronized()
        if _id is None:
            jbridge._init_java()
            _sendall(CREATE_OBJECT)
            _send_string("matt.oexp.olang.lab.model.trial.Choice")
            _send_string(args[0])
            if args[1] == DEFAULT_VALUE:
                _sendall(b"\x00")
            else:
                _sendall(b"\x01")
                if args[1] is None:
                    _sendall(b"\x00")
                else:
                    _sendall(b"\x01")
                if args[1] is not None:
                    _send_long(args[1]._id._id)
            if args[2] == DEFAULT_VALUE:
                _sendall(b"\x00")
            else:
                _sendall(b"\x01")
                if args[2] is None:
                    _sendall(b"\x00")
                else:
                    _sendall(b"\x01")
                if args[2] is not None:
                    _send_string(args[2])
            self._id = _object_id(_recv_long())
        else:
            self._id = _object_id(_id)

    # [[matt.oexp.olang.lab.model.trial.Choice#image]]
    @property
    def image(self) -> Optional[Image]:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(0)
        temp = _recv_object(Image, nullable=True)
        return temp

    # [[matt.oexp.olang.lab.model.trial.Choice#text]]
    @property
    def text(self) -> Optional[str]:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(1)
        temp = _recv_string(nullable=True)
        return temp

    # [[matt.oexp.olang.lab.model.trial.Choice#value]]
    @property
    def value(self) -> str:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(2)
        temp = _recv_string(nullable=False)
        return temp

    # [[matt.oexp.olang.lab.model.trial.Choice]]
    def to_json(self):
        _ensure_synchronized()
        _sendall(GET_JSON)
        _send_long(self._id._id)
        return _recv_string(nullable=False)

    # [[matt.oexp.olang.lab.model.trial.Choice]]
    def to_dict(self):
        return json.loads(self.to_json())

    # [[matt.oexp.olang.lab.model.trial.Choice]]
    def to_data(self):
        from mstuff.mstuff import Obj

        return Obj(self.to_dict())

    # [[matt.oexp.olang.lab.model.trial.Choice]]
    def __eq__(self, other):
        _ensure_synchronized()
        if isinstance(other, KBClass):
            _sendall(CHECK_EQUALITY)
            _send_long(self._id._id)
            _send_long(other._id._id)
            return _recv_bool()
        else:
            return False


def image(remote_path=NO_DEFAULT, one_shot=NO_DEFAULT):
    _check_required_parameters(**dict(remote_path=remote_path, one_shot=one_shot))
    return Image(remote_path, one_shot)


# [[matt.oexp.olang.lab.model.trial.Image]]
class Image(KBDClass):
    def __init__(self, *args, _id=None):
        _ensure_synchronized()
        if _id is None:
            jbridge._init_java()
            _sendall(CREATE_OBJECT)
            _send_string("matt.oexp.olang.lab.model.trial.Image")
            _send_string(args[0])
            if args[1]:
                _sendall(b"\x01")
            else:
                _sendall(b"\x00")
            self._id = _object_id(_recv_long())
        else:
            self._id = _object_id(_id)

    # [[matt.oexp.olang.lab.model.trial.Image#oneShot]]
    @property
    def one_shot(self) -> bool:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(0)
        temp = _recv_bool(nullable=False)
        return temp

    # [[matt.oexp.olang.lab.model.trial.Image#remotePath]]
    @property
    def remote_path(self) -> str:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(1)
        temp = _recv_string(nullable=False)
        return temp

    # [[matt.oexp.olang.lab.model.trial.Image]]
    def to_json(self):
        _ensure_synchronized()
        _sendall(GET_JSON)
        _send_long(self._id._id)
        return _recv_string(nullable=False)

    # [[matt.oexp.olang.lab.model.trial.Image]]
    def to_dict(self):
        return json.loads(self.to_json())

    # [[matt.oexp.olang.lab.model.trial.Image]]
    def to_data(self):
        from mstuff.mstuff import Obj

        return Obj(self.to_dict())

    # [[matt.oexp.olang.lab.model.trial.Image]]
    def __eq__(self, other):
        _ensure_synchronized()
        if isinstance(other, KBClass):
            _sendall(CHECK_EQUALITY)
            _send_long(self._id._id)
            _send_long(other._id._id)
            return _recv_bool()
        else:
            return False


def orient(image=NO_DEFAULT):
    _check_required_parameters(**dict(image=image))
    return Orient(image)


# [[matt.oexp.olang.lab.model.trial.Orient]]
class Orient(KBDClass):
    def __init__(self, *args, _id=None):
        _ensure_synchronized()
        if _id is None:
            jbridge._init_java()
            _sendall(CREATE_OBJECT)
            _send_string("matt.oexp.olang.lab.model.trial.Orient")
            _send_long(args[0]._id._id)
            self._id = _object_id(_recv_long())
        else:
            self._id = _object_id(_id)

    # [[matt.oexp.olang.lab.model.trial.Orient#image]]
    @property
    def image(self) -> Image:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(0)
        temp = _recv_object(Image, nullable=False)
        return temp

    # [[matt.oexp.olang.lab.model.trial.Orient]]
    def to_json(self):
        _ensure_synchronized()
        _sendall(GET_JSON)
        _send_long(self._id._id)
        return _recv_string(nullable=False)

    # [[matt.oexp.olang.lab.model.trial.Orient]]
    def to_dict(self):
        return json.loads(self.to_json())

    # [[matt.oexp.olang.lab.model.trial.Orient]]
    def to_data(self):
        from mstuff.mstuff import Obj

        return Obj(self.to_dict())

    # [[matt.oexp.olang.lab.model.trial.Orient]]
    def __eq__(self, other):
        _ensure_synchronized()
        if isinstance(other, KBClass):
            _sendall(CHECK_EQUALITY)
            _send_long(self._id._id)
            _send_long(other._id._id)
            return _recv_bool()
        else:
            return False


# [[matt.oexp.olang.lab.model.trial.Phase]]
class Phase(KBClass, abc.ABC):
    # [[matt.oexp.olang.lab.model.trial.Phase#images]]
    @abc.abstractmethod
    def images(self) -> List[Image]:
        pass

    # [[matt.oexp.olang.lab.model.trial.Phase]]
    def to_json(self):
        _ensure_synchronized()
        _sendall(GET_JSON)
        _send_long(self._id._id)
        return _recv_string(nullable=False)

    # [[matt.oexp.olang.lab.model.trial.Phase]]
    def to_dict(self):
        return json.loads(self.to_json())

    # [[matt.oexp.olang.lab.model.trial.Phase]]
    def to_data(self):
        from mstuff.mstuff import Obj

        return Obj(self.to_dict())


def prompt(text=DEFAULT_VALUE, image=DEFAULT_VALUE):
    _check_required_parameters(**dict())
    return Prompt(text, image)


# [[matt.oexp.olang.lab.model.trial.Prompt]]
class Prompt(Phase, KBDClass):
    def __init__(self, *args, _id=None):
        _ensure_synchronized()
        if _id is None:
            jbridge._init_java()
            _sendall(CREATE_OBJECT)
            _send_string("matt.oexp.olang.lab.model.trial.Prompt")
            if args[0] == DEFAULT_VALUE:
                _sendall(b"\x00")
            else:
                _sendall(b"\x01")
                if args[0] is None:
                    _sendall(b"\x00")
                else:
                    _sendall(b"\x01")
                if args[0] is not None:
                    _send_string(args[0])
            if args[1] == DEFAULT_VALUE:
                _sendall(b"\x00")
            else:
                _sendall(b"\x01")
                if args[1] is None:
                    _sendall(b"\x00")
                else:
                    _sendall(b"\x01")
                if args[1] is not None:
                    _send_long(args[1]._id._id)
            self._id = _object_id(_recv_long())
        else:
            self._id = _object_id(_id)

    # [[matt.oexp.olang.lab.model.trial.Prompt#image]]
    @property
    def image(self) -> Optional[Image]:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(0)
        temp = _recv_object(Image, nullable=True)
        return temp

    # [[matt.oexp.olang.lab.model.trial.Prompt#text]]
    @property
    def text(self) -> Optional[str]:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(1)
        temp = _recv_string(nullable=True)
        return temp

    # [[matt.oexp.olang.lab.model.trial.Prompt#images]]
    def images(self) -> List[Image]:
        _ensure_synchronized()
        _check_required_parameters(**dict())
        _sendall(CALL_FUN)
        _send_long(self._id._id)
        _send_int(0)
        _recv_exception_check()
        return _recv_list(
            elementReceiveFun=lambda: _recv_object(Image, nullable=False),
            nullable=False,
        )

    # [[matt.oexp.olang.lab.model.trial.Prompt]]
    def to_json(self):
        _ensure_synchronized()
        _sendall(GET_JSON)
        _send_long(self._id._id)
        return _recv_string(nullable=False)

    # [[matt.oexp.olang.lab.model.trial.Prompt]]
    def to_dict(self):
        return json.loads(self.to_json())

    # [[matt.oexp.olang.lab.model.trial.Prompt]]
    def to_data(self):
        from mstuff.mstuff import Obj

        return Obj(self.to_dict())

    # [[matt.oexp.olang.lab.model.trial.Prompt]]
    def __eq__(self, other):
        _ensure_synchronized()
        if isinstance(other, KBClass):
            _sendall(CHECK_EQUALITY)
            _send_long(self._id._id)
            _send_long(other._id._id)
            return _recv_bool()
        else:
            return False


# [[matt.oexp.olang.lab.model.trial.Trial]]
class Trial(Phase, KBClass, abc.ABC):
    # [[matt.oexp.olang.lab.model.trial.Trial#images]]
    @abc.abstractmethod
    def images(self) -> List[Image]:
        pass

    # [[matt.oexp.olang.lab.model.trial.Trial]]
    def to_json(self):
        _ensure_synchronized()
        _sendall(GET_JSON)
        _send_long(self._id._id)
        return _recv_string(nullable=False)

    # [[matt.oexp.olang.lab.model.trial.Trial]]
    def to_dict(self):
        return json.loads(self.to_json())

    # [[matt.oexp.olang.lab.model.trial.Trial]]
    def to_data(self):
        from mstuff.mstuff import Obj

        return Obj(self.to_dict())


# [[matt.oexp.olang.model.ExperimentEvent]]
class ExperimentEvent(KBClass, abc.ABC):
    # [[matt.oexp.olang.model.ExperimentEvent#expUID]]
    @property
    @abc.abstractmethod
    def exp_uid(self) -> ExperimentUid:
        pass

    # [[matt.oexp.olang.model.ExperimentEvent#pid]]
    @property
    @abc.abstractmethod
    def pid(self) -> ProlificParticipantUid:
        pass

    # [[matt.oexp.olang.model.ExperimentEvent#sessionID]]
    @property
    @abc.abstractmethod
    def session_id(self) -> ProlificSessionId:
        pass

    # [[matt.oexp.olang.model.ExperimentEvent#sessionNumber]]
    @property
    @abc.abstractmethod
    def session_number(self) -> SessionNumber:
        pass

    # [[matt.oexp.olang.model.ExperimentEvent]]
    def to_json(self):
        _ensure_synchronized()
        _sendall(GET_JSON)
        _send_long(self._id._id)
        return _recv_string(nullable=False)

    # [[matt.oexp.olang.model.ExperimentEvent]]
    def to_dict(self):
        return json.loads(self.to_json())

    # [[matt.oexp.olang.model.ExperimentEvent]]
    def to_data(self):
        from mstuff.mstuff import Obj

        return Obj(self.to_dict())


def experiment_start(
    pid=NO_DEFAULT,
    session_id=NO_DEFAULT,
    unix_time_millis=NO_DEFAULT,
    session_number=NO_DEFAULT,
    exp_uid=NO_DEFAULT,
    query_params=DEFAULT_VALUE,
):
    _check_required_parameters(
        **dict(
            pid=pid,
            session_id=session_id,
            unix_time_millis=unix_time_millis,
            session_number=session_number,
            exp_uid=exp_uid,
        )
    )
    return ExperimentStart(
        pid, session_id, unix_time_millis, session_number, exp_uid, query_params
    )


# [[matt.oexp.olang.model.ExperimentStart]]
class ExperimentStart(ExperimentEvent, KBClass):
    def __init__(self, *args, _id=None):
        _ensure_synchronized()
        if _id is None:
            jbridge._init_java()
            _sendall(CREATE_OBJECT)
            _send_string("matt.oexp.olang.model.ExperimentStart")
            _send_long(args[0]._id._id)
            _send_long(args[1]._id._id)
            _send_long(args[2])
            _send_long(args[3]._id._id)
            _send_long(args[4]._id._id)
            if args[5] == DEFAULT_VALUE:
                _sendall(b"\x00")
            else:
                _sendall(b"\x01")
                if args[5] is None:
                    _sendall(b"\x00")
                else:
                    _sendall(b"\x01")
                if args[5] is not None:
                    _send_int(len(args[5]))
                    for k, v in args[5].items():
                        _send_string(k)
                        _send_int(len(v))
                        for e in v:
                            _send_string(e)
            self._id = _object_id(_recv_long())
        else:
            self._id = _object_id(_id)

    # [[matt.oexp.olang.model.ExperimentStart#expUID]]
    @property
    def exp_uid(self) -> ExperimentUid:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(0)
        temp = _recv_object(ExperimentUid, nullable=False)
        return temp

    # [[matt.oexp.olang.model.ExperimentStart#pid]]
    @property
    def pid(self) -> ProlificParticipantUid:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(1)
        temp = _recv_object(ProlificParticipantUid, nullable=False)
        return temp

    # [[matt.oexp.olang.model.ExperimentStart#queryParams]]
    @property
    def query_params(self) -> Optional[Dict[str, List[str]]]:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(2)
        temp = _recv_map(
            keyReceiveFun=lambda: _recv_string(nullable=False),
            valueReceiveFun=lambda: _recv_list(
                elementReceiveFun=lambda: _recv_string(nullable=False), nullable=False
            ),
            nullable=True,
        )
        return temp

    # [[matt.oexp.olang.model.ExperimentStart#sessionID]]
    @property
    def session_id(self) -> ProlificSessionId:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(3)
        temp = _recv_object(ProlificSessionId, nullable=False)
        return temp

    # [[matt.oexp.olang.model.ExperimentStart#sessionNumber]]
    @property
    def session_number(self) -> SessionNumber:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(4)
        temp = _recv_object(SessionNumber, nullable=False)
        return temp

    # [[matt.oexp.olang.model.ExperimentStart#unixTimeMillis]]
    @property
    def unix_time_millis(self) -> int:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(5)
        temp = _recv_long(nullable=False)
        return temp

    # [[matt.oexp.olang.model.ExperimentStart]]
    def to_json(self):
        _ensure_synchronized()
        _sendall(GET_JSON)
        _send_long(self._id._id)
        return _recv_string(nullable=False)

    # [[matt.oexp.olang.model.ExperimentStart]]
    def to_dict(self):
        return json.loads(self.to_json())

    # [[matt.oexp.olang.model.ExperimentStart]]
    def to_data(self):
        from mstuff.mstuff import Obj

        return Obj(self.to_dict())

    # [[matt.oexp.olang.model.ExperimentStart]]
    def __eq__(self, other):
        _ensure_synchronized()
        if isinstance(other, KBClass):
            _sendall(CHECK_EQUALITY)
            _send_long(self._id._id)
            _send_long(other._id._id)
            return _recv_bool()
        else:
            return False


# [[matt.oexp.olang.model.TrialData]]
class TrialData(ExperimentEvent, KBClass, abc.ABC):
    # [[matt.oexp.olang.model.TrialData#log]]
    @property
    @abc.abstractmethod
    def log(self) -> List[SubjectTrialEvent]:
        pass

    # [[matt.oexp.olang.model.TrialData#pid]]
    @property
    @abc.abstractmethod
    def pid(self) -> ProlificParticipantUid:
        pass

    # [[matt.oexp.olang.model.TrialData#response]]
    @property
    @abc.abstractmethod
    def response(self) -> TrialResponse:
        pass

    # [[matt.oexp.olang.model.TrialData#sessionID]]
    @property
    @abc.abstractmethod
    def session_id(self) -> ProlificSessionId:
        pass

    # [[matt.oexp.olang.model.TrialData#sessionNumber]]
    @property
    @abc.abstractmethod
    def session_number(self) -> SessionNumber:
        pass

    # [[matt.oexp.olang.model.TrialData#startTimeUnixMillis]]
    @property
    @abc.abstractmethod
    def start_time_unix_millis(self) -> int:
        pass

    # [[matt.oexp.olang.model.TrialData#stimuli]]
    @property
    @abc.abstractmethod
    def stimuli(self) -> S:
        pass

    # [[matt.oexp.olang.model.TrialData#trialIndex]]
    @property
    @abc.abstractmethod
    def trial_index(self) -> int:
        pass

    # [[matt.oexp.olang.model.TrialData#expUID]]
    @property
    @abc.abstractmethod
    def exp_uid(self) -> ExperimentUid:
        pass


def completion_code(code=NO_DEFAULT, code_type=NO_DEFAULT, actions=NO_DEFAULT):
    _check_required_parameters(**dict(code=code, code_type=code_type, actions=actions))
    return CompletionCode(code, code_type, actions)


# [[matt.oexp.olang.model.prolific.CompletionCode]]
class CompletionCode(KBDClass):
    def __init__(self, *args, _id=None):
        _ensure_synchronized()
        if _id is None:
            jbridge._init_java()
            _sendall(CREATE_OBJECT)
            _send_string("matt.oexp.olang.model.prolific.CompletionCode")
            _send_string(args[0])
            _send_string(args[1])
            _send_int(len(args[2]))
            for e in args[2]:
                _send_int(len(e))
                for k, v in e.items():
                    _send_string(k)
                    _send_string(v)
            self._id = _object_id(_recv_long())
        else:
            self._id = _object_id(_id)

    # [[matt.oexp.olang.model.prolific.CompletionCode#actions]]
    @property
    def actions(self) -> List[Dict[str, str]]:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(0)
        temp = _recv_list(
            elementReceiveFun=lambda: _recv_map(
                keyReceiveFun=lambda: _recv_string(nullable=False),
                valueReceiveFun=lambda: _recv_string(nullable=False),
                nullable=False,
            ),
            nullable=False,
        )
        return temp

    # [[matt.oexp.olang.model.prolific.CompletionCode#code]]
    @property
    def code(self) -> str:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(1)
        temp = _recv_string(nullable=False)
        return temp

    # [[matt.oexp.olang.model.prolific.CompletionCode#code_type]]
    @property
    def code_type(self) -> str:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(2)
        temp = _recv_string(nullable=False)
        return temp

    # [[matt.oexp.olang.model.prolific.CompletionCode]]
    def to_json(self):
        _ensure_synchronized()
        _sendall(GET_JSON)
        _send_long(self._id._id)
        return _recv_string(nullable=False)

    # [[matt.oexp.olang.model.prolific.CompletionCode]]
    def to_dict(self):
        return json.loads(self.to_json())

    # [[matt.oexp.olang.model.prolific.CompletionCode]]
    def to_data(self):
        from mstuff.mstuff import Obj

        return Obj(self.to_dict())

    # [[matt.oexp.olang.model.prolific.CompletionCode]]
    def __eq__(self, other):
        _ensure_synchronized()
        if isinstance(other, KBClass):
            _sendall(CHECK_EQUALITY)
            _send_long(self._id._id)
            _send_long(other._id._id)
            return _recv_bool()
        else:
            return False


# [[matt.oexp.olang.model.prolific.CompletionOption]]
class CompletionOption(Enum):
    url = 0
    code = 1
    # [[matt.oexp.olang.model.prolific.CompletionOption]]
    def to_json(self):
        _ensure_synchronized()
        _sendall(GET_JSON)
        _send_long(self._id._id)
        return _recv_string(nullable=False)

    # [[matt.oexp.olang.model.prolific.CompletionOption]]
    def to_dict(self):
        return json.loads(self.to_json())

    # [[matt.oexp.olang.model.prolific.CompletionOption]]
    def to_data(self):
        from mstuff.mstuff import Obj

        return Obj(self.to_dict())


def prolific_study_data(
    external_study_url=NO_DEFAULT,
    completion_option=NO_DEFAULT,
    completion_codes=NO_DEFAULT,
):
    _check_required_parameters(
        **dict(
            external_study_url=external_study_url,
            completion_option=completion_option,
            completion_codes=completion_codes,
        )
    )
    return ProlificStudyData(external_study_url, completion_option, completion_codes)


# [[matt.oexp.olang.model.prolific.ProlificStudyData]]
class ProlificStudyData(KBDClass):
    def __init__(self, *args, _id=None):
        _ensure_synchronized()
        if _id is None:
            jbridge._init_java()
            _sendall(CREATE_OBJECT)
            _send_string("matt.oexp.olang.model.prolific.ProlificStudyData")
            _send_string(args[0])
            _send_short(args[1].value)
            _send_int(len(args[2]))
            for e in args[2]:
                _send_long(e._id._id)
            self._id = _object_id(_recv_long())
        else:
            self._id = _object_id(_id)

    # [[matt.oexp.olang.model.prolific.ProlificStudyData#completion_codes]]
    @property
    def completion_codes(self) -> List[CompletionCode]:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(0)
        temp = _recv_list(
            elementReceiveFun=lambda: _recv_object(CompletionCode, nullable=False),
            nullable=False,
        )
        return temp

    # [[matt.oexp.olang.model.prolific.ProlificStudyData#completion_option]]
    @property
    def completion_option(self) -> CompletionOption:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(1)
        temp = _recv_enum(CompletionOption, nullable=False)
        return temp

    # [[matt.oexp.olang.model.prolific.ProlificStudyData#external_study_url]]
    @property
    def external_study_url(self) -> str:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(2)
        temp = _recv_string(nullable=False)
        return temp

    # [[matt.oexp.olang.model.prolific.ProlificStudyData]]
    def to_json(self):
        _ensure_synchronized()
        _sendall(GET_JSON)
        _send_long(self._id._id)
        return _recv_string(nullable=False)

    # [[matt.oexp.olang.model.prolific.ProlificStudyData]]
    def to_dict(self):
        return json.loads(self.to_json())

    # [[matt.oexp.olang.model.prolific.ProlificStudyData]]
    def to_data(self):
        from mstuff.mstuff import Obj

        return Obj(self.to_dict())

    # [[matt.oexp.olang.model.prolific.ProlificStudyData]]
    def __eq__(self, other):
        _ensure_synchronized()
        if isinstance(other, KBClass):
            _sendall(CHECK_EQUALITY)
            _send_long(self._id._id)
            _send_long(other._id._id)
            return _recv_bool()
        else:
            return False


# [[matt.oexp.olang.model.response.TrialResponse]]
class TrialResponse(KBClass, abc.ABC):
    # [[matt.oexp.olang.model.response.TrialResponse]]
    def to_json(self):
        _ensure_synchronized()
        _sendall(GET_JSON)
        _send_long(self._id._id)
        return _recv_string(nullable=False)

    # [[matt.oexp.olang.model.response.TrialResponse]]
    def to_dict(self):
        return json.loads(self.to_json())

    # [[matt.oexp.olang.model.response.TrialResponse]]
    def to_data(self):
        from mstuff.mstuff import Obj

        return Obj(self.to_dict())


# [[matt.oexp.olang.model.stim.TrialStimuli]]
class TrialStimuli(KBClass, abc.ABC):
    # [[matt.oexp.olang.model.stim.TrialStimuli#isEncrypted]]
    @property
    @abc.abstractmethod
    def is_encrypted(self) -> bool:
        pass

    # [[matt.oexp.olang.model.stim.TrialStimuli#allImages]]
    @abc.abstractmethod
    def all_images(self) -> List[IarpaTrialStimulus]:
        pass

    # [[matt.oexp.olang.model.stim.TrialStimuli#decrypt]]
    @abc.abstractmethod
    def decrypt(self, cipher=NO_DEFAULT) -> TrialStimuli:
        pass

    # [[matt.oexp.olang.model.stim.TrialStimuli#encrypt]]
    @abc.abstractmethod
    def encrypt(self, cipher=NO_DEFAULT) -> TrialStimuli:
        pass

    # [[matt.oexp.olang.model.stim.TrialStimuli]]
    def to_json(self):
        _ensure_synchronized()
        _sendall(GET_JSON)
        _send_long(self._id._id)
        return _recv_string(nullable=False)

    # [[matt.oexp.olang.model.stim.TrialStimuli]]
    def to_dict(self):
        return json.loads(self.to_json())

    # [[matt.oexp.olang.model.stim.TrialStimuli]]
    def to_data(self):
        from mstuff.mstuff import Obj

        return Obj(self.to_dict())


def encrypted_stimulus_path(cipher_path=NO_DEFAULT):
    _check_required_parameters(**dict(cipher_path=cipher_path))
    return EncryptedStimulusPath(cipher_path)


# [[matt.oexp.olang.model.stim.image.EncryptedStimulusPath]]
class EncryptedStimulusPath(KBDClass):
    def __init__(self, *args, _id=None):
        _ensure_synchronized()
        if _id is None:
            jbridge._init_java()
            _sendall(CREATE_OBJECT)
            _send_string("matt.oexp.olang.model.stim.image.EncryptedStimulusPath")
            _send_string(args[0])
            self._id = _object_id(_recv_long())
        else:
            self._id = _object_id(_id)

    # [[matt.oexp.olang.model.stim.image.EncryptedStimulusPath#cipherPath]]
    @property
    def cipher_path(self) -> str:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(0)
        temp = _recv_string(nullable=False)
        return temp

    # [[matt.oexp.olang.model.stim.image.EncryptedStimulusPath]]
    def to_json(self):
        _ensure_synchronized()
        _sendall(GET_JSON)
        _send_long(self._id._id)
        return _recv_string(nullable=False)

    # [[matt.oexp.olang.model.stim.image.EncryptedStimulusPath]]
    def to_dict(self):
        return json.loads(self.to_json())

    # [[matt.oexp.olang.model.stim.image.EncryptedStimulusPath]]
    def to_data(self):
        from mstuff.mstuff import Obj

        return Obj(self.to_dict())

    # [[matt.oexp.olang.model.stim.image.EncryptedStimulusPath]]
    def __eq__(self, other):
        _ensure_synchronized()
        if isinstance(other, KBClass):
            _sendall(CHECK_EQUALITY)
            _send_long(self._id._id)
            _send_long(other._id._id)
            return _recv_bool()
        else:
            return False


# [[matt.oexp.olang.model.stim.image.IarpaTrialStimulus]]
class IarpaTrialStimulus(KBClass, abc.ABC):
    # [[matt.oexp.olang.model.stim.image.IarpaTrialStimulus#url]]
    @property
    @abc.abstractmethod
    def url(self) -> str:
        pass

    # [[matt.oexp.olang.model.stim.image.IarpaTrialStimulus]]
    def to_json(self):
        _ensure_synchronized()
        _sendall(GET_JSON)
        _send_long(self._id._id)
        return _recv_string(nullable=False)

    # [[matt.oexp.olang.model.stim.image.IarpaTrialStimulus]]
    def to_dict(self):
        return json.loads(self.to_json())

    # [[matt.oexp.olang.model.stim.image.IarpaTrialStimulus]]
    def to_data(self):
        from mstuff.mstuff import Obj

        return Obj(self.to_dict())


# [[matt.oexp.olang.model.stim.image.RawTrialStim]]
class RawTrialStim(IarpaTrialStimulus, KBClass, abc.ABC):
    # [[matt.oexp.olang.model.stim.image.RawTrialStim#url]]
    @property
    @abc.abstractmethod
    def url(self) -> str:
        pass

    # [[matt.oexp.olang.model.stim.image.RawTrialStim]]
    def to_json(self):
        _ensure_synchronized()
        _sendall(GET_JSON)
        _send_long(self._id._id)
        return _recv_string(nullable=False)

    # [[matt.oexp.olang.model.stim.image.RawTrialStim]]
    def to_dict(self):
        return json.loads(self.to_json())

    # [[matt.oexp.olang.model.stim.image.RawTrialStim]]
    def to_data(self):
        from mstuff.mstuff import Obj

        return Obj(self.to_dict())


# [[matt.oexp.olang.model.trialevent.SubjectTrialEvent]]
class SubjectTrialEvent(KBClass, abc.ABC):
    # [[matt.oexp.olang.model.trialevent.SubjectTrialEvent#timeMillis]]
    @property
    @abc.abstractmethod
    def time_millis(self) -> int:
        pass

    # [[matt.oexp.olang.model.trialevent.SubjectTrialEvent]]
    def to_json(self):
        _ensure_synchronized()
        _sendall(GET_JSON)
        _send_long(self._id._id)
        return _recv_string(nullable=False)

    # [[matt.oexp.olang.model.trialevent.SubjectTrialEvent]]
    def to_dict(self):
        return json.loads(self.to_json())

    # [[matt.oexp.olang.model.trialevent.SubjectTrialEvent]]
    def to_data(self):
        from mstuff.mstuff import Obj

        return Obj(self.to_dict())


def experiment_uid(uid=NO_DEFAULT):
    _check_required_parameters(**dict(uid=uid))
    return ExperimentUid(uid)


# [[matt.oexp.olang.model.uid.ExperimentUID]]
class ExperimentUid(KBVClass):
    def __init__(self, *args, _id=None):
        _ensure_synchronized()
        if _id is None:
            jbridge._init_java()
            _sendall(CREATE_OBJECT)
            _send_string("matt.oexp.olang.model.uid.ExperimentUID")
            _send_long(args[0])
            self._id = _object_id(_recv_long())
        else:
            self._id = _object_id(_id)

    # [[matt.oexp.olang.model.uid.ExperimentUID#uid]]
    @property
    def uid(self) -> int:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(0)
        temp = _recv_long(nullable=False)
        return temp

    # [[matt.oexp.olang.model.uid.ExperimentUID]]
    def to_json(self):
        _ensure_synchronized()
        _sendall(GET_JSON)
        _send_long(self._id._id)
        return _recv_string(nullable=False)

    # [[matt.oexp.olang.model.uid.ExperimentUID]]
    def to_dict(self):
        return json.loads(self.to_json())

    # [[matt.oexp.olang.model.uid.ExperimentUID]]
    def to_data(self):
        from mstuff.mstuff import Obj

        return Obj(self.to_dict())

    # [[matt.oexp.olang.model.uid.ExperimentUID]]
    def __eq__(self, other):
        _ensure_synchronized()
        return type(other) == type(self) and other.uid == self.uid


def manifest_number(num=NO_DEFAULT):
    _check_required_parameters(**dict(num=num))
    return ManifestNumber(num)


# [[matt.oexp.olang.model.uid.ManifestNumber]]
class ManifestNumber(KBVClass):
    def __init__(self, *args, _id=None):
        _ensure_synchronized()
        if _id is None:
            jbridge._init_java()
            _sendall(CREATE_OBJECT)
            _send_string("matt.oexp.olang.model.uid.ManifestNumber")
            _send_int(args[0])
            self._id = _object_id(_recv_long())
        else:
            self._id = _object_id(_id)

    # [[matt.oexp.olang.model.uid.ManifestNumber#num]]
    @property
    def num(self) -> int:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(0)
        temp = _recv_int(nullable=False)
        return temp

    # [[matt.oexp.olang.model.uid.ManifestNumber]]
    def to_json(self):
        _ensure_synchronized()
        _sendall(GET_JSON)
        _send_long(self._id._id)
        return _recv_string(nullable=False)

    # [[matt.oexp.olang.model.uid.ManifestNumber]]
    def to_dict(self):
        return json.loads(self.to_json())

    # [[matt.oexp.olang.model.uid.ManifestNumber]]
    def to_data(self):
        from mstuff.mstuff import Obj

        return Obj(self.to_dict())

    # [[matt.oexp.olang.model.uid.ManifestNumber]]
    def __eq__(self, other):
        _ensure_synchronized()
        return type(other) == type(self) and other.num == self.num


def prolific_participant_uid(pid=NO_DEFAULT):
    _check_required_parameters(**dict(pid=pid))
    return ProlificParticipantUid(pid)


# [[matt.oexp.olang.model.uid.ProlificParticipantUid]]
class ProlificParticipantUid(KBVClass):
    def __init__(self, *args, _id=None):
        _ensure_synchronized()
        if _id is None:
            jbridge._init_java()
            _sendall(CREATE_OBJECT)
            _send_string("matt.oexp.olang.model.uid.ProlificParticipantUid")
            _send_string(args[0])
            self._id = _object_id(_recv_long())
        else:
            self._id = _object_id(_id)

    # [[matt.oexp.olang.model.uid.ProlificParticipantUid#pid]]
    @property
    def pid(self) -> str:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(0)
        temp = _recv_string(nullable=False)
        return temp

    # [[matt.oexp.olang.model.uid.ProlificParticipantUid]]
    def to_json(self):
        _ensure_synchronized()
        _sendall(GET_JSON)
        _send_long(self._id._id)
        return _recv_string(nullable=False)

    # [[matt.oexp.olang.model.uid.ProlificParticipantUid]]
    def to_dict(self):
        return json.loads(self.to_json())

    # [[matt.oexp.olang.model.uid.ProlificParticipantUid]]
    def to_data(self):
        from mstuff.mstuff import Obj

        return Obj(self.to_dict())

    # [[matt.oexp.olang.model.uid.ProlificParticipantUid]]
    def __eq__(self, other):
        _ensure_synchronized()
        return type(other) == type(self) and other.pid == self.pid


def prolific_session_id(id=NO_DEFAULT):
    _check_required_parameters(**dict(id=id))
    return ProlificSessionId(id)


# [[matt.oexp.olang.model.uid.ProlificSessionId]]
class ProlificSessionId(KBVClass):
    def __init__(self, *args, _id=None):
        _ensure_synchronized()
        if _id is None:
            jbridge._init_java()
            _sendall(CREATE_OBJECT)
            _send_string("matt.oexp.olang.model.uid.ProlificSessionId")
            _send_string(args[0])
            self._id = _object_id(_recv_long())
        else:
            self._id = _object_id(_id)

    # [[matt.oexp.olang.model.uid.ProlificSessionId#id]]
    @property
    def id(self) -> str:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(0)
        temp = _recv_string(nullable=False)
        return temp

    # [[matt.oexp.olang.model.uid.ProlificSessionId]]
    def to_json(self):
        _ensure_synchronized()
        _sendall(GET_JSON)
        _send_long(self._id._id)
        return _recv_string(nullable=False)

    # [[matt.oexp.olang.model.uid.ProlificSessionId]]
    def to_dict(self):
        return json.loads(self.to_json())

    # [[matt.oexp.olang.model.uid.ProlificSessionId]]
    def to_data(self):
        from mstuff.mstuff import Obj

        return Obj(self.to_dict())

    # [[matt.oexp.olang.model.uid.ProlificSessionId]]
    def __eq__(self, other):
        _ensure_synchronized()
        return type(other) == type(self) and other.id == self.id


def prolific_study_id(id=NO_DEFAULT):
    _check_required_parameters(**dict(id=id))
    return ProlificStudyId(id)


# [[matt.oexp.olang.model.uid.ProlificStudyID]]
class ProlificStudyId(KBVClass):
    def __init__(self, *args, _id=None):
        _ensure_synchronized()
        if _id is None:
            jbridge._init_java()
            _sendall(CREATE_OBJECT)
            _send_string("matt.oexp.olang.model.uid.ProlificStudyID")
            _send_string(args[0])
            self._id = _object_id(_recv_long())
        else:
            self._id = _object_id(_id)

    # [[matt.oexp.olang.model.uid.ProlificStudyID#id]]
    @property
    def id(self) -> str:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(0)
        temp = _recv_string(nullable=False)
        return temp

    # [[matt.oexp.olang.model.uid.ProlificStudyID]]
    def to_json(self):
        _ensure_synchronized()
        _sendall(GET_JSON)
        _send_long(self._id._id)
        return _recv_string(nullable=False)

    # [[matt.oexp.olang.model.uid.ProlificStudyID]]
    def to_dict(self):
        return json.loads(self.to_json())

    # [[matt.oexp.olang.model.uid.ProlificStudyID]]
    def to_data(self):
        from mstuff.mstuff import Obj

        return Obj(self.to_dict())

    # [[matt.oexp.olang.model.uid.ProlificStudyID]]
    def __eq__(self, other):
        _ensure_synchronized()
        return type(other) == type(self) and other.id == self.id


def session_number(num=NO_DEFAULT):
    _check_required_parameters(**dict(num=num))
    return SessionNumber(num)


# [[matt.oexp.olang.model.uid.SessionNumber]]
class SessionNumber(KBVClass):
    def __init__(self, *args, _id=None):
        _ensure_synchronized()
        if _id is None:
            jbridge._init_java()
            _sendall(CREATE_OBJECT)
            _send_string("matt.oexp.olang.model.uid.SessionNumber")
            _send_long(args[0])
            self._id = _object_id(_recv_long())
        else:
            self._id = _object_id(_id)

    # [[matt.oexp.olang.model.uid.SessionNumber#num]]
    @property
    def num(self) -> int:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(0)
        temp = _recv_long(nullable=False)
        return temp

    # [[matt.oexp.olang.model.uid.SessionNumber]]
    def to_json(self):
        _ensure_synchronized()
        _sendall(GET_JSON)
        _send_long(self._id._id)
        return _recv_string(nullable=False)

    # [[matt.oexp.olang.model.uid.SessionNumber]]
    def to_dict(self):
        return json.loads(self.to_json())

    # [[matt.oexp.olang.model.uid.SessionNumber]]
    def to_data(self):
        from mstuff.mstuff import Obj

        return Obj(self.to_dict())

    # [[matt.oexp.olang.model.uid.SessionNumber]]
    def __eq__(self, other):
        _ensure_synchronized()
        return type(other) == type(self) and other.num == self.num


def choice_trial(image=NO_DEFAULT, choices=NO_DEFAULT):
    _check_required_parameters(**dict(image=image, choices=choices))
    return ChoiceTrial(image, choices)


# [[matt.oexp.olang.lab.model.trial.ChoiceTrial]]
class ChoiceTrial(Trial, KBDClass):
    def __init__(self, *args, _id=None):
        _ensure_synchronized()
        if _id is None:
            jbridge._init_java()
            _sendall(CREATE_OBJECT)
            _send_string("matt.oexp.olang.lab.model.trial.ChoiceTrial")
            _send_long(args[0]._id._id)
            _send_int(len(args[1]))
            for e in args[1]:
                _send_long(e._id._id)
            self._id = _object_id(_recv_long())
        else:
            self._id = _object_id(_id)

    # [[matt.oexp.olang.lab.model.trial.ChoiceTrial#choices]]
    @property
    def choices(self) -> List[Choice]:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(0)
        temp = _recv_list(
            elementReceiveFun=lambda: _recv_object(Choice, nullable=False),
            nullable=False,
        )
        return temp

    # [[matt.oexp.olang.lab.model.trial.ChoiceTrial#image]]
    @property
    def image(self) -> Image:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(1)
        temp = _recv_object(Image, nullable=False)
        return temp

    # [[matt.oexp.olang.lab.model.trial.ChoiceTrial#images]]
    def images(self) -> List[Image]:
        _ensure_synchronized()
        _check_required_parameters(**dict())
        _sendall(CALL_FUN)
        _send_long(self._id._id)
        _send_int(0)
        _recv_exception_check()
        return _recv_list(
            elementReceiveFun=lambda: _recv_object(Image, nullable=False),
            nullable=False,
        )

    # [[matt.oexp.olang.lab.model.trial.ChoiceTrial]]
    def to_json(self):
        _ensure_synchronized()
        _sendall(GET_JSON)
        _send_long(self._id._id)
        return _recv_string(nullable=False)

    # [[matt.oexp.olang.lab.model.trial.ChoiceTrial]]
    def to_dict(self):
        return json.loads(self.to_json())

    # [[matt.oexp.olang.lab.model.trial.ChoiceTrial]]
    def to_data(self):
        from mstuff.mstuff import Obj

        return Obj(self.to_dict())

    # [[matt.oexp.olang.lab.model.trial.ChoiceTrial]]
    def __eq__(self, other):
        _ensure_synchronized()
        if isinstance(other, KBClass):
            _sendall(CHECK_EQUALITY)
            _send_long(self._id._id)
            _send_long(other._id._id)
            return _recv_bool()
        else:
            return False


def gallery_trial(query=NO_DEFAULT, distractors=NO_DEFAULT):
    _check_required_parameters(**dict(query=query, distractors=distractors))
    return GalleryTrial(query, distractors)


# [[matt.oexp.olang.lab.model.trial.GalleryTrial]]
class GalleryTrial(Trial, KBDClass):
    def __init__(self, *args, _id=None):
        _ensure_synchronized()
        if _id is None:
            jbridge._init_java()
            _sendall(CREATE_OBJECT)
            _send_string("matt.oexp.olang.lab.model.trial.GalleryTrial")
            _send_long(args[0]._id._id)
            _send_int(len(args[1]))
            for e in args[1]:
                _send_long(e._id._id)
            self._id = _object_id(_recv_long())
        else:
            self._id = _object_id(_id)

    # [[matt.oexp.olang.lab.model.trial.GalleryTrial#distractors]]
    @property
    def distractors(self) -> List[Image]:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(0)
        temp = _recv_list(
            elementReceiveFun=lambda: _recv_object(Image, nullable=False),
            nullable=False,
        )
        return temp

    # [[matt.oexp.olang.lab.model.trial.GalleryTrial#query]]
    @property
    def query(self) -> Image:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(1)
        temp = _recv_object(Image, nullable=False)
        return temp

    # [[matt.oexp.olang.lab.model.trial.GalleryTrial#images]]
    def images(self) -> List[Image]:
        _ensure_synchronized()
        _check_required_parameters(**dict())
        _sendall(CALL_FUN)
        _send_long(self._id._id)
        _send_int(0)
        _recv_exception_check()
        return _recv_list(
            elementReceiveFun=lambda: _recv_object(Image, nullable=False),
            nullable=False,
        )

    # [[matt.oexp.olang.lab.model.trial.GalleryTrial]]
    def to_json(self):
        _ensure_synchronized()
        _sendall(GET_JSON)
        _send_long(self._id._id)
        return _recv_string(nullable=False)

    # [[matt.oexp.olang.lab.model.trial.GalleryTrial]]
    def to_dict(self):
        return json.loads(self.to_json())

    # [[matt.oexp.olang.lab.model.trial.GalleryTrial]]
    def to_data(self):
        from mstuff.mstuff import Obj

        return Obj(self.to_dict())

    # [[matt.oexp.olang.lab.model.trial.GalleryTrial]]
    def __eq__(self, other):
        _ensure_synchronized()
        if isinstance(other, KBClass):
            _sendall(CHECK_EQUALITY)
            _send_long(self._id._id)
            _send_long(other._id._id)
            return _recv_bool()
        else:
            return False


def orient_trial(image=NO_DEFAULT, orient=NO_DEFAULT):
    _check_required_parameters(**dict(image=image, orient=orient))
    return OrientTrial(image, orient)


# [[matt.oexp.olang.lab.model.trial.OrientTrial]]
class OrientTrial(Trial, KBDClass):
    def __init__(self, *args, _id=None):
        _ensure_synchronized()
        if _id is None:
            jbridge._init_java()
            _sendall(CREATE_OBJECT)
            _send_string("matt.oexp.olang.lab.model.trial.OrientTrial")
            _send_long(args[0]._id._id)
            _send_long(args[1]._id._id)
            self._id = _object_id(_recv_long())
        else:
            self._id = _object_id(_id)

    # [[matt.oexp.olang.lab.model.trial.OrientTrial#image]]
    @property
    def image(self) -> Image:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(0)
        temp = _recv_object(Image, nullable=False)
        return temp

    # [[matt.oexp.olang.lab.model.trial.OrientTrial#orient]]
    @property
    def orient(self) -> Orient:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(1)
        temp = _recv_object(Orient, nullable=False)
        return temp

    # [[matt.oexp.olang.lab.model.trial.OrientTrial#images]]
    def images(self) -> List[Image]:
        _ensure_synchronized()
        _check_required_parameters(**dict())
        _sendall(CALL_FUN)
        _send_long(self._id._id)
        _send_int(0)
        _recv_exception_check()
        return _recv_list(
            elementReceiveFun=lambda: _recv_object(Image, nullable=False),
            nullable=False,
        )

    # [[matt.oexp.olang.lab.model.trial.OrientTrial]]
    def to_json(self):
        _ensure_synchronized()
        _sendall(GET_JSON)
        _send_long(self._id._id)
        return _recv_string(nullable=False)

    # [[matt.oexp.olang.lab.model.trial.OrientTrial]]
    def to_dict(self):
        return json.loads(self.to_json())

    # [[matt.oexp.olang.lab.model.trial.OrientTrial]]
    def to_data(self):
        from mstuff.mstuff import Obj

        return Obj(self.to_dict())

    # [[matt.oexp.olang.lab.model.trial.OrientTrial]]
    def __eq__(self, other):
        _ensure_synchronized()
        if isinstance(other, KBClass):
            _sendall(CHECK_EQUALITY)
            _send_long(self._id._id)
            _send_long(other._id._id)
            return _recv_bool()
        else:
            return False


def exit_full_screen_event(
    pid=NO_DEFAULT,
    session_id=NO_DEFAULT,
    unix_time_millis=NO_DEFAULT,
    session_number=NO_DEFAULT,
    exp_uid=NO_DEFAULT,
):
    _check_required_parameters(
        **dict(
            pid=pid,
            session_id=session_id,
            unix_time_millis=unix_time_millis,
            session_number=session_number,
            exp_uid=exp_uid,
        )
    )
    return ExitFullScreenEvent(
        pid, session_id, unix_time_millis, session_number, exp_uid
    )


# [[matt.oexp.olang.model.ExitFullScreenEvent]]
class ExitFullScreenEvent(ExperimentEvent, KBClass):
    def __init__(self, *args, _id=None):
        _ensure_synchronized()
        if _id is None:
            jbridge._init_java()
            _sendall(CREATE_OBJECT)
            _send_string("matt.oexp.olang.model.ExitFullScreenEvent")
            _send_long(args[0]._id._id)
            _send_long(args[1]._id._id)
            _send_long(args[2])
            _send_long(args[3]._id._id)
            _send_long(args[4]._id._id)
            self._id = _object_id(_recv_long())
        else:
            self._id = _object_id(_id)

    # [[matt.oexp.olang.model.ExitFullScreenEvent#expUID]]
    @property
    def exp_uid(self) -> ExperimentUid:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(0)
        temp = _recv_object(ExperimentUid, nullable=False)
        return temp

    # [[matt.oexp.olang.model.ExitFullScreenEvent#pid]]
    @property
    def pid(self) -> ProlificParticipantUid:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(1)
        temp = _recv_object(ProlificParticipantUid, nullable=False)
        return temp

    # [[matt.oexp.olang.model.ExitFullScreenEvent#sessionID]]
    @property
    def session_id(self) -> ProlificSessionId:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(2)
        temp = _recv_object(ProlificSessionId, nullable=False)
        return temp

    # [[matt.oexp.olang.model.ExitFullScreenEvent#sessionNumber]]
    @property
    def session_number(self) -> SessionNumber:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(3)
        temp = _recv_object(SessionNumber, nullable=False)
        return temp

    # [[matt.oexp.olang.model.ExitFullScreenEvent#unixTimeMillis]]
    @property
    def unix_time_millis(self) -> int:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(4)
        temp = _recv_long(nullable=False)
        return temp

    # [[matt.oexp.olang.model.ExitFullScreenEvent]]
    def to_json(self):
        _ensure_synchronized()
        _sendall(GET_JSON)
        _send_long(self._id._id)
        return _recv_string(nullable=False)

    # [[matt.oexp.olang.model.ExitFullScreenEvent]]
    def to_dict(self):
        return json.loads(self.to_json())

    # [[matt.oexp.olang.model.ExitFullScreenEvent]]
    def to_data(self):
        from mstuff.mstuff import Obj

        return Obj(self.to_dict())

    # [[matt.oexp.olang.model.ExitFullScreenEvent]]
    def __eq__(self, other):
        _ensure_synchronized()
        if isinstance(other, KBClass):
            _sendall(CHECK_EQUALITY)
            _send_long(self._id._id)
            _send_long(other._id._id)
            return _recv_bool()
        else:
            return False


def subject_trial_data(
    pid=NO_DEFAULT,
    session_number=NO_DEFAULT,
    session_id=NO_DEFAULT,
    trial_index=NO_DEFAULT,
    stimuli=NO_DEFAULT,
    response=NO_DEFAULT,
    start_time_unix_millis=NO_DEFAULT,
    log=DEFAULT_VALUE,
    exp_uid=NO_DEFAULT,
):
    _check_required_parameters(
        **dict(
            pid=pid,
            session_number=session_number,
            session_id=session_id,
            trial_index=trial_index,
            stimuli=stimuli,
            response=response,
            start_time_unix_millis=start_time_unix_millis,
            exp_uid=exp_uid,
        )
    )
    return SubjectTrialData(
        pid,
        session_number,
        session_id,
        trial_index,
        stimuli,
        response,
        start_time_unix_millis,
        log,
        exp_uid,
    )


# [[matt.oexp.olang.model.SubjectTrialData]]
class SubjectTrialData(TrialData, ExperimentEvent, KBDClass):
    def __init__(self, *args, _id=None):
        _ensure_synchronized()
        if _id is None:
            jbridge._init_java()
            _sendall(CREATE_OBJECT)
            _send_string("matt.oexp.olang.model.SubjectTrialData")
            _send_long(args[0]._id._id)
            _send_long(args[1]._id._id)
            _send_long(args[2]._id._id)
            _send_int(args[3])
            _send_long(args[4]._id._id)
            _send_long(args[5]._id._id)
            _send_long(args[6])
            if args[7] == DEFAULT_VALUE:
                _sendall(b"\x00")
            else:
                _sendall(b"\x01")
                _send_int(len(args[7]))
                for e in args[7]:
                    _send_long(e._id._id)
            _send_long(args[8]._id._id)
            self._id = _object_id(_recv_long())
        else:
            self._id = _object_id(_id)

    # [[matt.oexp.olang.model.SubjectTrialData#expUID]]
    @property
    def exp_uid(self) -> ExperimentUid:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(0)
        temp = _recv_object(ExperimentUid, nullable=False)
        return temp

    # [[matt.oexp.olang.model.SubjectTrialData#log]]
    @property
    def log(self) -> List[SubjectTrialEvent]:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(1)
        temp = _recv_list(
            elementReceiveFun=lambda: _recv_object(SubjectTrialEvent, nullable=False),
            nullable=False,
        )
        return temp

    # [[matt.oexp.olang.model.SubjectTrialData#pid]]
    @property
    def pid(self) -> ProlificParticipantUid:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(2)
        temp = _recv_object(ProlificParticipantUid, nullable=False)
        return temp

    # [[matt.oexp.olang.model.SubjectTrialData#response]]
    @property
    def response(self) -> TrialResponse:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(3)
        temp = _recv_object(TrialResponse, nullable=False)
        return temp

    # [[matt.oexp.olang.model.SubjectTrialData#sessionID]]
    @property
    def session_id(self) -> ProlificSessionId:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(4)
        temp = _recv_object(ProlificSessionId, nullable=False)
        return temp

    # [[matt.oexp.olang.model.SubjectTrialData#sessionNumber]]
    @property
    def session_number(self) -> SessionNumber:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(5)
        temp = _recv_object(SessionNumber, nullable=False)
        return temp

    # [[matt.oexp.olang.model.SubjectTrialData#startTimeUnixMillis]]
    @property
    def start_time_unix_millis(self) -> int:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(6)
        temp = _recv_long(nullable=False)
        return temp

    # [[matt.oexp.olang.model.SubjectTrialData#stimuli]]
    @property
    def stimuli(self) -> TrialStimuli:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(7)
        temp = _recv_object(TrialStimuli, nullable=False)
        return temp

    @stimuli.setter
    def stimuli(self, value) -> TrialStimuli:
        _ensure_synchronized()
        _sendall(SET_VAR)
        _send_long(self._id._id)
        _send_int(7)
        _send_long(value._id._id)
        _recv_confirmation()

    # [[matt.oexp.olang.model.SubjectTrialData#trialIndex]]
    @property
    def trial_index(self) -> int:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(8)
        temp = _recv_int(nullable=False)
        return temp

    # [[matt.oexp.olang.model.SubjectTrialData]]
    def to_json(self):
        _ensure_synchronized()
        _sendall(GET_JSON)
        _send_long(self._id._id)
        return _recv_string(nullable=False)

    # [[matt.oexp.olang.model.SubjectTrialData]]
    def to_dict(self):
        return json.loads(self.to_json())

    # [[matt.oexp.olang.model.SubjectTrialData]]
    def to_data(self):
        from mstuff.mstuff import Obj

        return Obj(self.to_dict())

    # [[matt.oexp.olang.model.SubjectTrialData]]
    def __eq__(self, other):
        _ensure_synchronized()
        if isinstance(other, KBClass):
            _sendall(CHECK_EQUALITY)
            _send_long(self._id._id)
            _send_long(other._id._id)
            return _recv_bool()
        else:
            return False


def choice_response(choice=NO_DEFAULT):
    _check_required_parameters(**dict(choice=choice))
    return ChoiceResponse(choice)


# [[matt.oexp.olang.model.response.ChoiceResponse]]
class ChoiceResponse(TrialResponse, KBClass):
    def __init__(self, *args, _id=None):
        _ensure_synchronized()
        if _id is None:
            jbridge._init_java()
            _sendall(CREATE_OBJECT)
            _send_string("matt.oexp.olang.model.response.ChoiceResponse")
            _send_string(args[0])
            self._id = _object_id(_recv_long())
        else:
            self._id = _object_id(_id)

    # [[matt.oexp.olang.model.response.ChoiceResponse#choice]]
    @property
    def choice(self) -> str:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(0)
        temp = _recv_string(nullable=False)
        return temp

    # [[matt.oexp.olang.model.response.ChoiceResponse]]
    def to_json(self):
        _ensure_synchronized()
        _sendall(GET_JSON)
        _send_long(self._id._id)
        return _recv_string(nullable=False)

    # [[matt.oexp.olang.model.response.ChoiceResponse]]
    def to_dict(self):
        return json.loads(self.to_json())

    # [[matt.oexp.olang.model.response.ChoiceResponse]]
    def to_data(self):
        from mstuff.mstuff import Obj

        return Obj(self.to_dict())

    # [[matt.oexp.olang.model.response.ChoiceResponse]]
    def __eq__(self, other):
        _ensure_synchronized()
        if isinstance(other, KBClass):
            _sendall(CHECK_EQUALITY)
            _send_long(self._id._id)
            _send_long(other._id._id)
            return _recv_bool()
        else:
            return False


def gallery_selections(selection_indices=NO_DEFAULT):
    _check_required_parameters(**dict(selection_indices=selection_indices))
    return GallerySelections(selection_indices)


# [[matt.oexp.olang.model.response.GallerySelections]]
class GallerySelections(TrialResponse, KBClass):
    def __init__(self, *args, _id=None):
        _ensure_synchronized()
        if _id is None:
            jbridge._init_java()
            _sendall(CREATE_OBJECT)
            _send_string("matt.oexp.olang.model.response.GallerySelections")
            _send_int(len(args[0]))
            for e in args[0]:
                _send_int(e)
            self._id = _object_id(_recv_long())
        else:
            self._id = _object_id(_id)

    # [[matt.oexp.olang.model.response.GallerySelections#selectionIndices]]
    @property
    def selection_indices(self) -> List[int]:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(0)
        temp = _recv_list(
            elementReceiveFun=lambda: _recv_int(nullable=False), nullable=False
        )
        return temp

    # [[matt.oexp.olang.model.response.GallerySelections]]
    def to_json(self):
        _ensure_synchronized()
        _sendall(GET_JSON)
        _send_long(self._id._id)
        return _recv_string(nullable=False)

    # [[matt.oexp.olang.model.response.GallerySelections]]
    def to_dict(self):
        return json.loads(self.to_json())

    # [[matt.oexp.olang.model.response.GallerySelections]]
    def to_data(self):
        from mstuff.mstuff import Obj

        return Obj(self.to_dict())

    # [[matt.oexp.olang.model.response.GallerySelections]]
    def __eq__(self, other):
        _ensure_synchronized()
        if isinstance(other, KBClass):
            _sendall(CHECK_EQUALITY)
            _send_long(self._id._id)
            _send_long(other._id._id)
            return _recv_bool()
        else:
            return False


def orient_response(
    pitch_of_head_to_head_base=NO_DEFAULT, yaw_of_head_to_head_base=NO_DEFAULT
):
    _check_required_parameters(
        **dict(
            pitch_of_head_to_head_base=pitch_of_head_to_head_base,
            yaw_of_head_to_head_base=yaw_of_head_to_head_base,
        )
    )
    return OrientResponse(pitch_of_head_to_head_base, yaw_of_head_to_head_base)


# [[matt.oexp.olang.model.response.OrientResponse]]
class OrientResponse(TrialResponse, KBClass):
    def __init__(self, *args, _id=None):
        _ensure_synchronized()
        if _id is None:
            jbridge._init_java()
            _sendall(CREATE_OBJECT)
            _send_string("matt.oexp.olang.model.response.OrientResponse")
            _send_long(args[0]._id._id)
            _send_long(args[1]._id._id)
            self._id = _object_id(_recv_long())
        else:
            self._id = _object_id(_id)

    # [[matt.oexp.olang.model.response.OrientResponse#pitchOfHeadToHeadBase]]
    @property
    def pitch_of_head_to_head_base(self) -> DegreesDouble:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(0)
        temp = _recv_object(DegreesDouble, nullable=False)
        return temp

    # [[matt.oexp.olang.model.response.OrientResponse#yawOfHeadToHeadBase]]
    @property
    def yaw_of_head_to_head_base(self) -> DegreesDouble:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(1)
        temp = _recv_object(DegreesDouble, nullable=False)
        return temp

    # [[matt.oexp.olang.model.response.OrientResponse]]
    def to_json(self):
        _ensure_synchronized()
        _sendall(GET_JSON)
        _send_long(self._id._id)
        return _recv_string(nullable=False)

    # [[matt.oexp.olang.model.response.OrientResponse]]
    def to_dict(self):
        return json.loads(self.to_json())

    # [[matt.oexp.olang.model.response.OrientResponse]]
    def to_data(self):
        from mstuff.mstuff import Obj

        return Obj(self.to_dict())

    # [[matt.oexp.olang.model.response.OrientResponse]]
    def __eq__(self, other):
        _ensure_synchronized()
        if isinstance(other, KBClass):
            _sendall(CHECK_EQUALITY)
            _send_long(self._id._id)
            _send_long(other._id._id)
            return _recv_bool()
        else:
            return False


# [[matt.oexp.olang.model.stim.image.EncryptedTrialStim]]
class EncryptedTrialStim(IarpaTrialStimulus, KBClass, abc.ABC):
    # [[matt.oexp.olang.model.stim.image.EncryptedTrialStim#url]]
    @property
    @abc.abstractmethod
    def url(self) -> str:
        pass

    # [[matt.oexp.olang.model.stim.image.EncryptedTrialStim]]
    def to_json(self):
        _ensure_synchronized()
        _sendall(GET_JSON)
        _send_long(self._id._id)
        return _recv_string(nullable=False)

    # [[matt.oexp.olang.model.stim.image.EncryptedTrialStim]]
    def to_dict(self):
        return json.loads(self.to_json())

    # [[matt.oexp.olang.model.stim.image.EncryptedTrialStim]]
    def to_data(self):
        from mstuff.mstuff import Obj

        return Obj(self.to_dict())


def raw_stim_path(path=NO_DEFAULT):
    _check_required_parameters(**dict(path=path))
    return RawStimPath(path)


# [[matt.oexp.olang.model.stim.image.RawStimPath]]
class RawStimPath(EncryptedTrialStim, KBDClass):
    def __init__(self, *args, _id=None):
        _ensure_synchronized()
        if _id is None:
            jbridge._init_java()
            _sendall(CREATE_OBJECT)
            _send_string("matt.oexp.olang.model.stim.image.RawStimPath")
            _send_string(args[0])
            self._id = _object_id(_recv_long())
        else:
            self._id = _object_id(_id)

    # [[matt.oexp.olang.model.stim.image.RawStimPath#path]]
    @property
    def path(self) -> str:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(0)
        temp = _recv_string(nullable=False)
        return temp

    # [[matt.oexp.olang.model.stim.image.RawStimPath#url]]
    @property
    def url(self) -> str:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(1)
        temp = _recv_string(nullable=False)
        return temp

    # [[matt.oexp.olang.model.stim.image.RawStimPath]]
    def to_json(self):
        _ensure_synchronized()
        _sendall(GET_JSON)
        _send_long(self._id._id)
        return _recv_string(nullable=False)

    # [[matt.oexp.olang.model.stim.image.RawStimPath]]
    def to_dict(self):
        return json.loads(self.to_json())

    # [[matt.oexp.olang.model.stim.image.RawStimPath]]
    def to_data(self):
        from mstuff.mstuff import Obj

        return Obj(self.to_dict())

    # [[matt.oexp.olang.model.stim.image.RawStimPath]]
    def __eq__(self, other):
        _ensure_synchronized()
        if isinstance(other, KBClass):
            _sendall(CHECK_EQUALITY)
            _send_long(self._id._id)
            _send_long(other._id._id)
            return _recv_bool()
        else:
            return False


def temporary_encrypted_stimulus(path=NO_DEFAULT, temp_url=NO_DEFAULT):
    _check_required_parameters(**dict(path=path, temp_url=temp_url))
    return TemporaryEncryptedStimulus(path, temp_url)


# [[matt.oexp.olang.model.stim.image.TemporaryEncryptedStimulus]]
class TemporaryEncryptedStimulus(EncryptedTrialStim, KBClass):
    def __init__(self, *args, _id=None):
        _ensure_synchronized()
        if _id is None:
            jbridge._init_java()
            _sendall(CREATE_OBJECT)
            _send_string("matt.oexp.olang.model.stim.image.TemporaryEncryptedStimulus")
            _send_long(args[0]._id._id)
            _send_string(args[1])
            self._id = _object_id(_recv_long())
        else:
            self._id = _object_id(_id)

    # [[matt.oexp.olang.model.stim.image.TemporaryEncryptedStimulus#path]]
    @property
    def path(self) -> EncryptedStimulusPath:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(0)
        temp = _recv_object(EncryptedStimulusPath, nullable=False)
        return temp

    # [[matt.oexp.olang.model.stim.image.TemporaryEncryptedStimulus#url]]
    @property
    def url(self) -> str:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(1)
        temp = _recv_string(nullable=False)
        return temp

    # [[matt.oexp.olang.model.stim.image.TemporaryEncryptedStimulus]]
    def to_json(self):
        _ensure_synchronized()
        _sendall(GET_JSON)
        _send_long(self._id._id)
        return _recv_string(nullable=False)

    # [[matt.oexp.olang.model.stim.image.TemporaryEncryptedStimulus]]
    def to_dict(self):
        return json.loads(self.to_json())

    # [[matt.oexp.olang.model.stim.image.TemporaryEncryptedStimulus]]
    def to_data(self):
        from mstuff.mstuff import Obj

        return Obj(self.to_dict())

    # [[matt.oexp.olang.model.stim.image.TemporaryEncryptedStimulus]]
    def __eq__(self, other):
        _ensure_synchronized()
        if isinstance(other, KBClass):
            _sendall(CHECK_EQUALITY)
            _send_long(self._id._id)
            _send_long(other._id._id)
            return _recv_bool()
        else:
            return False


def button_event(time_millis=NO_DEFAULT, button=NO_DEFAULT):
    _check_required_parameters(**dict(time_millis=time_millis, button=button))
    return ButtonEvent(time_millis, button)


# [[matt.oexp.olang.model.trialevent.ButtonEvent]]
class ButtonEvent(SubjectTrialEvent, KBClass):
    def __init__(self, *args, _id=None):
        _ensure_synchronized()
        if _id is None:
            jbridge._init_java()
            _sendall(CREATE_OBJECT)
            _send_string("matt.oexp.olang.model.trialevent.ButtonEvent")
            _send_int(args[0])
            _send_string(args[1])
            self._id = _object_id(_recv_long())
        else:
            self._id = _object_id(_id)

    # [[matt.oexp.olang.model.trialevent.ButtonEvent#button]]
    @property
    def button(self) -> str:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(0)
        temp = _recv_string(nullable=False)
        return temp

    # [[matt.oexp.olang.model.trialevent.ButtonEvent#timeMillis]]
    @property
    def time_millis(self) -> int:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(1)
        temp = _recv_int(nullable=False)
        return temp

    # [[matt.oexp.olang.model.trialevent.ButtonEvent]]
    def to_json(self):
        _ensure_synchronized()
        _sendall(GET_JSON)
        _send_long(self._id._id)
        return _recv_string(nullable=False)

    # [[matt.oexp.olang.model.trialevent.ButtonEvent]]
    def to_dict(self):
        return json.loads(self.to_json())

    # [[matt.oexp.olang.model.trialevent.ButtonEvent]]
    def to_data(self):
        from mstuff.mstuff import Obj

        return Obj(self.to_dict())

    # [[matt.oexp.olang.model.trialevent.ButtonEvent]]
    def __eq__(self, other):
        _ensure_synchronized()
        if isinstance(other, KBClass):
            _sendall(CHECK_EQUALITY)
            _send_long(self._id._id)
            _send_long(other._id._id)
            return _recv_bool()
        else:
            return False


def selection_event(
    time_millis=NO_DEFAULT, selection_index=NO_DEFAULT, distractor_index=NO_DEFAULT
):
    _check_required_parameters(
        **dict(
            time_millis=time_millis,
            selection_index=selection_index,
            distractor_index=distractor_index,
        )
    )
    return SelectionEvent(time_millis, selection_index, distractor_index)


# [[matt.oexp.olang.model.trialevent.SelectionEvent]]
class SelectionEvent(SubjectTrialEvent, KBClass):
    def __init__(self, *args, _id=None):
        _ensure_synchronized()
        if _id is None:
            jbridge._init_java()
            _sendall(CREATE_OBJECT)
            _send_string("matt.oexp.olang.model.trialevent.SelectionEvent")
            _send_int(args[0])
            _send_int(args[1])
            _send_int(args[2])
            self._id = _object_id(_recv_long())
        else:
            self._id = _object_id(_id)

    # [[matt.oexp.olang.model.trialevent.SelectionEvent#distractorIndex]]
    @property
    def distractor_index(self) -> int:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(0)
        temp = _recv_int(nullable=False)
        return temp

    # [[matt.oexp.olang.model.trialevent.SelectionEvent#selectionIndex]]
    @property
    def selection_index(self) -> int:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(1)
        temp = _recv_int(nullable=False)
        return temp

    # [[matt.oexp.olang.model.trialevent.SelectionEvent#timeMillis]]
    @property
    def time_millis(self) -> int:
        _ensure_synchronized()
        _sendall(GET_VAL)
        _send_long(self._id._id)
        _send_int(2)
        temp = _recv_int(nullable=False)
        return temp

    # [[matt.oexp.olang.model.trialevent.SelectionEvent]]
    def to_json(self):
        _ensure_synchronized()
        _sendall(GET_JSON)
        _send_long(self._id._id)
        return _recv_string(nullable=False)

    # [[matt.oexp.olang.model.trialevent.SelectionEvent]]
    def to_dict(self):
        return json.loads(self.to_json())

    # [[matt.oexp.olang.model.trialevent.SelectionEvent]]
    def to_data(self):
        from mstuff.mstuff import Obj

        return Obj(self.to_dict())

    # [[matt.oexp.olang.model.trialevent.SelectionEvent]]
    def __eq__(self, other):
        _ensure_synchronized()
        if isinstance(other, KBClass):
            _sendall(CHECK_EQUALITY)
            _send_long(self._id._id)
            _send_long(other._id._id)
            return _recv_bool()
        else:
            return False
