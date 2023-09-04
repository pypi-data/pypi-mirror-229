// Generated by the protocol buffer compiler.  DO NOT EDIT!
// source: tensorflow/core/protobuf/core_platform_payloads.proto

#ifndef GOOGLE_PROTOBUF_INCLUDED_tensorflow_2fcore_2fprotobuf_2fcore_5fplatform_5fpayloads_2eproto
#define GOOGLE_PROTOBUF_INCLUDED_tensorflow_2fcore_2fprotobuf_2fcore_5fplatform_5fpayloads_2eproto

#include <limits>
#include <string>

#include <google/protobuf/port_def.inc>
#if PROTOBUF_VERSION < 3021000
#error This file was generated by a newer version of protoc which is
#error incompatible with your Protocol Buffer headers. Please update
#error your headers.
#endif
#if 3021009 < PROTOBUF_MIN_PROTOC_VERSION
#error This file was generated by an older version of protoc which is
#error incompatible with your Protocol Buffer headers. Please
#error regenerate this file with a newer version of protoc.
#endif

#include <google/protobuf/port_undef.inc>
#include <google/protobuf/io/coded_stream.h>
#include <google/protobuf/arena.h>
#include <google/protobuf/arenastring.h>
#include <google/protobuf/generated_message_util.h>
#include <google/protobuf/metadata_lite.h>
#include <google/protobuf/generated_message_reflection.h>
#include <google/protobuf/message.h>
#include <google/protobuf/repeated_field.h>  // IWYU pragma: export
#include <google/protobuf/extension_set.h>  // IWYU pragma: export
#include <google/protobuf/generated_enum_reflection.h>
#include <google/protobuf/unknown_field_set.h>
// @@protoc_insertion_point(includes)
#include <google/protobuf/port_def.inc>
#define PROTOBUF_INTERNAL_EXPORT_tensorflow_2fcore_2fprotobuf_2fcore_5fplatform_5fpayloads_2eproto
PROTOBUF_NAMESPACE_OPEN
namespace internal {
class AnyMetadata;
}  // namespace internal
PROTOBUF_NAMESPACE_CLOSE

// Internal implementation detail -- do not use these members.
struct TableStruct_tensorflow_2fcore_2fprotobuf_2fcore_5fplatform_5fpayloads_2eproto {
  static const uint32_t offsets[];
};
extern const ::PROTOBUF_NAMESPACE_ID::internal::DescriptorTable descriptor_table_tensorflow_2fcore_2fprotobuf_2fcore_5fplatform_5fpayloads_2eproto;
namespace tensorflow {
namespace core {
namespace platform {
class ErrorSourceProto;
struct ErrorSourceProtoDefaultTypeInternal;
extern ErrorSourceProtoDefaultTypeInternal _ErrorSourceProto_default_instance_;
}  // namespace platform
}  // namespace core
}  // namespace tensorflow
PROTOBUF_NAMESPACE_OPEN
template<> ::tensorflow::core::platform::ErrorSourceProto* Arena::CreateMaybeMessage<::tensorflow::core::platform::ErrorSourceProto>(Arena*);
PROTOBUF_NAMESPACE_CLOSE
namespace tensorflow {
namespace core {
namespace platform {

enum ErrorSourceProto_ErrorSource : int {
  ErrorSourceProto_ErrorSource_UNKNOWN = 0,
  ErrorSourceProto_ErrorSource_TPU_COMPILE_OP = 1,
  ErrorSourceProto_ErrorSource_TF_XLA_BRIDGE = 2,
  ErrorSourceProto_ErrorSource_MLIR_BRIDGE_PHASE_1 = 3,
  ErrorSourceProto_ErrorSource_MLIR_BRIDGE_PHASE_2 = 4,
  ErrorSourceProto_ErrorSource_EAGER_REMOTE_MGR = 5,
  ErrorSourceProto_ErrorSource_ErrorSourceProto_ErrorSource_INT_MIN_SENTINEL_DO_NOT_USE_ = std::numeric_limits<int32_t>::min(),
  ErrorSourceProto_ErrorSource_ErrorSourceProto_ErrorSource_INT_MAX_SENTINEL_DO_NOT_USE_ = std::numeric_limits<int32_t>::max()
};
bool ErrorSourceProto_ErrorSource_IsValid(int value);
constexpr ErrorSourceProto_ErrorSource ErrorSourceProto_ErrorSource_ErrorSource_MIN = ErrorSourceProto_ErrorSource_UNKNOWN;
constexpr ErrorSourceProto_ErrorSource ErrorSourceProto_ErrorSource_ErrorSource_MAX = ErrorSourceProto_ErrorSource_EAGER_REMOTE_MGR;
constexpr int ErrorSourceProto_ErrorSource_ErrorSource_ARRAYSIZE = ErrorSourceProto_ErrorSource_ErrorSource_MAX + 1;

const ::PROTOBUF_NAMESPACE_ID::EnumDescriptor* ErrorSourceProto_ErrorSource_descriptor();
template<typename T>
inline const std::string& ErrorSourceProto_ErrorSource_Name(T enum_t_value) {
  static_assert(::std::is_same<T, ErrorSourceProto_ErrorSource>::value ||
    ::std::is_integral<T>::value,
    "Incorrect type passed to function ErrorSourceProto_ErrorSource_Name.");
  return ::PROTOBUF_NAMESPACE_ID::internal::NameOfEnum(
    ErrorSourceProto_ErrorSource_descriptor(), enum_t_value);
}
inline bool ErrorSourceProto_ErrorSource_Parse(
    ::PROTOBUF_NAMESPACE_ID::ConstStringParam name, ErrorSourceProto_ErrorSource* value) {
  return ::PROTOBUF_NAMESPACE_ID::internal::ParseNamedEnum<ErrorSourceProto_ErrorSource>(
    ErrorSourceProto_ErrorSource_descriptor(), name, value);
}
// ===================================================================

class ErrorSourceProto final :
    public ::PROTOBUF_NAMESPACE_ID::Message /* @@protoc_insertion_point(class_definition:tensorflow.core.platform.ErrorSourceProto) */ {
 public:
  inline ErrorSourceProto() : ErrorSourceProto(nullptr) {}
  ~ErrorSourceProto() override;
  explicit PROTOBUF_CONSTEXPR ErrorSourceProto(::PROTOBUF_NAMESPACE_ID::internal::ConstantInitialized);

  ErrorSourceProto(const ErrorSourceProto& from);
  ErrorSourceProto(ErrorSourceProto&& from) noexcept
    : ErrorSourceProto() {
    *this = ::std::move(from);
  }

  inline ErrorSourceProto& operator=(const ErrorSourceProto& from) {
    CopyFrom(from);
    return *this;
  }
  inline ErrorSourceProto& operator=(ErrorSourceProto&& from) noexcept {
    if (this == &from) return *this;
    if (GetOwningArena() == from.GetOwningArena()
  #ifdef PROTOBUF_FORCE_COPY_IN_MOVE
        && GetOwningArena() != nullptr
  #endif  // !PROTOBUF_FORCE_COPY_IN_MOVE
    ) {
      InternalSwap(&from);
    } else {
      CopyFrom(from);
    }
    return *this;
  }

  static const ::PROTOBUF_NAMESPACE_ID::Descriptor* descriptor() {
    return GetDescriptor();
  }
  static const ::PROTOBUF_NAMESPACE_ID::Descriptor* GetDescriptor() {
    return default_instance().GetMetadata().descriptor;
  }
  static const ::PROTOBUF_NAMESPACE_ID::Reflection* GetReflection() {
    return default_instance().GetMetadata().reflection;
  }
  static const ErrorSourceProto& default_instance() {
    return *internal_default_instance();
  }
  static inline const ErrorSourceProto* internal_default_instance() {
    return reinterpret_cast<const ErrorSourceProto*>(
               &_ErrorSourceProto_default_instance_);
  }
  static constexpr int kIndexInFileMessages =
    0;

  friend void swap(ErrorSourceProto& a, ErrorSourceProto& b) {
    a.Swap(&b);
  }
  inline void Swap(ErrorSourceProto* other) {
    if (other == this) return;
  #ifdef PROTOBUF_FORCE_COPY_IN_SWAP
    if (GetOwningArena() != nullptr &&
        GetOwningArena() == other->GetOwningArena()) {
   #else  // PROTOBUF_FORCE_COPY_IN_SWAP
    if (GetOwningArena() == other->GetOwningArena()) {
  #endif  // !PROTOBUF_FORCE_COPY_IN_SWAP
      InternalSwap(other);
    } else {
      ::PROTOBUF_NAMESPACE_ID::internal::GenericSwap(this, other);
    }
  }
  void UnsafeArenaSwap(ErrorSourceProto* other) {
    if (other == this) return;
    GOOGLE_DCHECK(GetOwningArena() == other->GetOwningArena());
    InternalSwap(other);
  }

  // implements Message ----------------------------------------------

  ErrorSourceProto* New(::PROTOBUF_NAMESPACE_ID::Arena* arena = nullptr) const final {
    return CreateMaybeMessage<ErrorSourceProto>(arena);
  }
  using ::PROTOBUF_NAMESPACE_ID::Message::CopyFrom;
  void CopyFrom(const ErrorSourceProto& from);
  using ::PROTOBUF_NAMESPACE_ID::Message::MergeFrom;
  void MergeFrom( const ErrorSourceProto& from) {
    ErrorSourceProto::MergeImpl(*this, from);
  }
  private:
  static void MergeImpl(::PROTOBUF_NAMESPACE_ID::Message& to_msg, const ::PROTOBUF_NAMESPACE_ID::Message& from_msg);
  public:
  PROTOBUF_ATTRIBUTE_REINITIALIZES void Clear() final;
  bool IsInitialized() const final;

  size_t ByteSizeLong() const final;
  const char* _InternalParse(const char* ptr, ::PROTOBUF_NAMESPACE_ID::internal::ParseContext* ctx) final;
  uint8_t* _InternalSerialize(
      uint8_t* target, ::PROTOBUF_NAMESPACE_ID::io::EpsCopyOutputStream* stream) const final;
  int GetCachedSize() const final { return _impl_._cached_size_.Get(); }

  private:
  void SharedCtor(::PROTOBUF_NAMESPACE_ID::Arena* arena, bool is_message_owned);
  void SharedDtor();
  void SetCachedSize(int size) const final;
  void InternalSwap(ErrorSourceProto* other);

  private:
  friend class ::PROTOBUF_NAMESPACE_ID::internal::AnyMetadata;
  static ::PROTOBUF_NAMESPACE_ID::StringPiece FullMessageName() {
    return "tensorflow.core.platform.ErrorSourceProto";
  }
  protected:
  explicit ErrorSourceProto(::PROTOBUF_NAMESPACE_ID::Arena* arena,
                       bool is_message_owned = false);
  public:

  static const ClassData _class_data_;
  const ::PROTOBUF_NAMESPACE_ID::Message::ClassData*GetClassData() const final;

  ::PROTOBUF_NAMESPACE_ID::Metadata GetMetadata() const final;

  // nested types ----------------------------------------------------

  typedef ErrorSourceProto_ErrorSource ErrorSource;
  static constexpr ErrorSource UNKNOWN =
    ErrorSourceProto_ErrorSource_UNKNOWN;
  static constexpr ErrorSource TPU_COMPILE_OP =
    ErrorSourceProto_ErrorSource_TPU_COMPILE_OP;
  static constexpr ErrorSource TF_XLA_BRIDGE =
    ErrorSourceProto_ErrorSource_TF_XLA_BRIDGE;
  static constexpr ErrorSource MLIR_BRIDGE_PHASE_1 =
    ErrorSourceProto_ErrorSource_MLIR_BRIDGE_PHASE_1;
  static constexpr ErrorSource MLIR_BRIDGE_PHASE_2 =
    ErrorSourceProto_ErrorSource_MLIR_BRIDGE_PHASE_2;
  static constexpr ErrorSource EAGER_REMOTE_MGR =
    ErrorSourceProto_ErrorSource_EAGER_REMOTE_MGR;
  static inline bool ErrorSource_IsValid(int value) {
    return ErrorSourceProto_ErrorSource_IsValid(value);
  }
  static constexpr ErrorSource ErrorSource_MIN =
    ErrorSourceProto_ErrorSource_ErrorSource_MIN;
  static constexpr ErrorSource ErrorSource_MAX =
    ErrorSourceProto_ErrorSource_ErrorSource_MAX;
  static constexpr int ErrorSource_ARRAYSIZE =
    ErrorSourceProto_ErrorSource_ErrorSource_ARRAYSIZE;
  static inline const ::PROTOBUF_NAMESPACE_ID::EnumDescriptor*
  ErrorSource_descriptor() {
    return ErrorSourceProto_ErrorSource_descriptor();
  }
  template<typename T>
  static inline const std::string& ErrorSource_Name(T enum_t_value) {
    static_assert(::std::is_same<T, ErrorSource>::value ||
      ::std::is_integral<T>::value,
      "Incorrect type passed to function ErrorSource_Name.");
    return ErrorSourceProto_ErrorSource_Name(enum_t_value);
  }
  static inline bool ErrorSource_Parse(::PROTOBUF_NAMESPACE_ID::ConstStringParam name,
      ErrorSource* value) {
    return ErrorSourceProto_ErrorSource_Parse(name, value);
  }

  // accessors -------------------------------------------------------

  enum : int {
    kErrorSourceFieldNumber = 1,
  };
  // .tensorflow.core.platform.ErrorSourceProto.ErrorSource error_source = 1;
  void clear_error_source();
  ::tensorflow::core::platform::ErrorSourceProto_ErrorSource error_source() const;
  void set_error_source(::tensorflow::core::platform::ErrorSourceProto_ErrorSource value);
  private:
  ::tensorflow::core::platform::ErrorSourceProto_ErrorSource _internal_error_source() const;
  void _internal_set_error_source(::tensorflow::core::platform::ErrorSourceProto_ErrorSource value);
  public:

  // @@protoc_insertion_point(class_scope:tensorflow.core.platform.ErrorSourceProto)
 private:
  class _Internal;

  template <typename T> friend class ::PROTOBUF_NAMESPACE_ID::Arena::InternalHelper;
  typedef void InternalArenaConstructable_;
  typedef void DestructorSkippable_;
  struct Impl_ {
    int error_source_;
    mutable ::PROTOBUF_NAMESPACE_ID::internal::CachedSize _cached_size_;
  };
  union { Impl_ _impl_; };
  friend struct ::TableStruct_tensorflow_2fcore_2fprotobuf_2fcore_5fplatform_5fpayloads_2eproto;
};
// ===================================================================


// ===================================================================

#ifdef __GNUC__
  #pragma GCC diagnostic push
  #pragma GCC diagnostic ignored "-Wstrict-aliasing"
#endif  // __GNUC__
// ErrorSourceProto

// .tensorflow.core.platform.ErrorSourceProto.ErrorSource error_source = 1;
inline void ErrorSourceProto::clear_error_source() {
  _impl_.error_source_ = 0;
}
inline ::tensorflow::core::platform::ErrorSourceProto_ErrorSource ErrorSourceProto::_internal_error_source() const {
  return static_cast< ::tensorflow::core::platform::ErrorSourceProto_ErrorSource >(_impl_.error_source_);
}
inline ::tensorflow::core::platform::ErrorSourceProto_ErrorSource ErrorSourceProto::error_source() const {
  // @@protoc_insertion_point(field_get:tensorflow.core.platform.ErrorSourceProto.error_source)
  return _internal_error_source();
}
inline void ErrorSourceProto::_internal_set_error_source(::tensorflow::core::platform::ErrorSourceProto_ErrorSource value) {
  
  _impl_.error_source_ = value;
}
inline void ErrorSourceProto::set_error_source(::tensorflow::core::platform::ErrorSourceProto_ErrorSource value) {
  _internal_set_error_source(value);
  // @@protoc_insertion_point(field_set:tensorflow.core.platform.ErrorSourceProto.error_source)
}

#ifdef __GNUC__
  #pragma GCC diagnostic pop
#endif  // __GNUC__

// @@protoc_insertion_point(namespace_scope)

}  // namespace platform
}  // namespace core
}  // namespace tensorflow

PROTOBUF_NAMESPACE_OPEN

template <> struct is_proto_enum< ::tensorflow::core::platform::ErrorSourceProto_ErrorSource> : ::std::true_type {};
template <>
inline const EnumDescriptor* GetEnumDescriptor< ::tensorflow::core::platform::ErrorSourceProto_ErrorSource>() {
  return ::tensorflow::core::platform::ErrorSourceProto_ErrorSource_descriptor();
}

PROTOBUF_NAMESPACE_CLOSE

// @@protoc_insertion_point(global_scope)

#include <google/protobuf/port_undef.inc>
#endif  // GOOGLE_PROTOBUF_INCLUDED_GOOGLE_PROTOBUF_INCLUDED_tensorflow_2fcore_2fprotobuf_2fcore_5fplatform_5fpayloads_2eproto
