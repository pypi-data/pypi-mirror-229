# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: tensorflow/lite/toco/logging/toco_conversion_log.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n6tensorflow/lite/toco/logging/toco_conversion_log.proto\x12\x04toco\"\xc9\x04\n\x11TocoConversionLog\x12\x0f\n\x07op_list\x18\x01 \x03(\t\x12=\n\x0c\x62uilt_in_ops\x18\x02 \x03(\x0b\x32\'.toco.TocoConversionLog.BuiltInOpsEntry\x12:\n\ncustom_ops\x18\x03 \x03(\x0b\x32&.toco.TocoConversionLog.CustomOpsEntry\x12:\n\nselect_ops\x18\x04 \x03(\x0b\x32&.toco.TocoConversionLog.SelectOpsEntry\x12\x15\n\rop_signatures\x18\x05 \x03(\t\x12\x1a\n\x12input_tensor_types\x18\x06 \x03(\t\x12\x1b\n\x13output_tensor_types\x18\x07 \x03(\t\x12\x19\n\x11log_generation_ts\x18\x08 \x01(\x03\x12\x12\n\nmodel_size\x18\t \x01(\x05\x12\x17\n\x0ftf_lite_version\x18\n \x01(\t\x12\x12\n\nos_version\x18\x0b \x01(\t\x12\x12\n\nmodel_hash\x18\x0c \x01(\t\x12\x15\n\rtoco_err_logs\x18\r \x01(\t\x1a\x31\n\x0f\x42uiltInOpsEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\x05:\x02\x38\x01\x1a\x30\n\x0e\x43ustomOpsEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\x05:\x02\x38\x01\x1a\x30\n\x0eSelectOpsEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\x05:\x02\x38\x01')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'tensorflow.lite.toco.logging.toco_conversion_log_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _TOCOCONVERSIONLOG_BUILTINOPSENTRY._options = None
  _TOCOCONVERSIONLOG_BUILTINOPSENTRY._serialized_options = b'8\001'
  _TOCOCONVERSIONLOG_CUSTOMOPSENTRY._options = None
  _TOCOCONVERSIONLOG_CUSTOMOPSENTRY._serialized_options = b'8\001'
  _TOCOCONVERSIONLOG_SELECTOPSENTRY._options = None
  _TOCOCONVERSIONLOG_SELECTOPSENTRY._serialized_options = b'8\001'
  _TOCOCONVERSIONLOG._serialized_start=65
  _TOCOCONVERSIONLOG._serialized_end=650
  _TOCOCONVERSIONLOG_BUILTINOPSENTRY._serialized_start=501
  _TOCOCONVERSIONLOG_BUILTINOPSENTRY._serialized_end=550
  _TOCOCONVERSIONLOG_CUSTOMOPSENTRY._serialized_start=552
  _TOCOCONVERSIONLOG_CUSTOMOPSENTRY._serialized_end=600
  _TOCOCONVERSIONLOG_SELECTOPSENTRY._serialized_start=602
  _TOCOCONVERSIONLOG_SELECTOPSENTRY._serialized_end=650
# @@protoc_insertion_point(module_scope)
