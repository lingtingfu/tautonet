# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: inner.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


import explorer_pb2 as explorer__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='inner.proto',
  package='protos',
  syntax='proto3',
  serialized_options=None,
  serialized_pb=_b('\n\x0binner.proto\x12\x06protos\x1a\x0e\x65xplorer.proto\"\xa8\x02\n\x12PeerStatusResponse\x12\x13\n\x0b\x63rrRoleName\x18\x01 \x01(\t\x12\x14\n\x0c\x63rrFSMStatus\x18\x02 \x01(\t\x12\x0f\n\x07\x63ssRole\x18\x03 \x01(\r\x12\x0f\n\x07\x63ssMode\x18\x04 \x01(\r\x12\x16\n\x0e\x63rrGspPeersCnt\x18\x05 \x01(\r\x12\x1c\n\x14\x63rrPowCntInDSHandler\x18\x06 \x01(\r\x12\x1b\n\x13\x63rrMBCntInDSHandler\x18\x07 \x01(\r\x12\x13\n\x0b\x63rrDSHeight\x18\x08 \x01(\r\x12\x13\n\x0b\x63rrTxHeight\x18\t \x01(\r\x12\x12\n\ntotalTXNum\x18\n \x01(\r\x12\x0f\n\x07shardId\x18\x0b \x01(\r\x12\x11\n\ttxPending\x18\x0c \x01(\r\x12\x10\n\x08txQueued\x18\r \x01(\r2L\n\x05Inner\x12\x43\n\rGetPeerStatus\x12\x14.protos.EmptyRequest\x1a\x1a.protos.PeerStatusResponse\"\x00\x62\x06proto3')
  ,
  dependencies=[explorer__pb2.DESCRIPTOR,])




_PEERSTATUSRESPONSE = _descriptor.Descriptor(
  name='PeerStatusResponse',
  full_name='protos.PeerStatusResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='crrRoleName', full_name='protos.PeerStatusResponse.crrRoleName', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='crrFSMStatus', full_name='protos.PeerStatusResponse.crrFSMStatus', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='cssRole', full_name='protos.PeerStatusResponse.cssRole', index=2,
      number=3, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='cssMode', full_name='protos.PeerStatusResponse.cssMode', index=3,
      number=4, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='crrGspPeersCnt', full_name='protos.PeerStatusResponse.crrGspPeersCnt', index=4,
      number=5, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='crrPowCntInDSHandler', full_name='protos.PeerStatusResponse.crrPowCntInDSHandler', index=5,
      number=6, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='crrMBCntInDSHandler', full_name='protos.PeerStatusResponse.crrMBCntInDSHandler', index=6,
      number=7, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='crrDSHeight', full_name='protos.PeerStatusResponse.crrDSHeight', index=7,
      number=8, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='crrTxHeight', full_name='protos.PeerStatusResponse.crrTxHeight', index=8,
      number=9, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='totalTXNum', full_name='protos.PeerStatusResponse.totalTXNum', index=9,
      number=10, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='shardId', full_name='protos.PeerStatusResponse.shardId', index=10,
      number=11, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='txPending', full_name='protos.PeerStatusResponse.txPending', index=11,
      number=12, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='txQueued', full_name='protos.PeerStatusResponse.txQueued', index=12,
      number=13, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=40,
  serialized_end=336,
)

DESCRIPTOR.message_types_by_name['PeerStatusResponse'] = _PEERSTATUSRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

PeerStatusResponse = _reflection.GeneratedProtocolMessageType('PeerStatusResponse', (_message.Message,), dict(
  DESCRIPTOR = _PEERSTATUSRESPONSE,
  __module__ = 'inner_pb2'
  # @@protoc_insertion_point(class_scope:protos.PeerStatusResponse)
  ))
_sym_db.RegisterMessage(PeerStatusResponse)



_INNER = _descriptor.ServiceDescriptor(
  name='Inner',
  full_name='protos.Inner',
  file=DESCRIPTOR,
  index=0,
  serialized_options=None,
  serialized_start=338,
  serialized_end=414,
  methods=[
  _descriptor.MethodDescriptor(
    name='GetPeerStatus',
    full_name='protos.Inner.GetPeerStatus',
    index=0,
    containing_service=None,
    input_type=explorer__pb2._EMPTYREQUEST,
    output_type=_PEERSTATUSRESPONSE,
    serialized_options=None,
  ),
])
_sym_db.RegisterServiceDescriptor(_INNER)

DESCRIPTOR.services_by_name['Inner'] = _INNER

# @@protoc_insertion_point(module_scope)