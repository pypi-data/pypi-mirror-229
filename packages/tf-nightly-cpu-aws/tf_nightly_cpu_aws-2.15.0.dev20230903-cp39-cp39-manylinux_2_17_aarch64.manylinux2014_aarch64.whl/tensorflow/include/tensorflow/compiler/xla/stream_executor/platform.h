/* Copyright 2015 The TensorFlow Authors. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
==============================================================================*/

// Defines types and declares functions for identifying and extracting
// information about the types of platforms and supporting libraries for which
// StreamExecutor implementations exist.
#ifndef TENSORFLOW_COMPILER_XLA_STREAM_EXECUTOR_PLATFORM_H_
#define TENSORFLOW_COMPILER_XLA_STREAM_EXECUTOR_PLATFORM_H_

#include <map>
#include <memory>

#include "tensorflow/compiler/xla/stream_executor/device_description.h"
#include "tensorflow/compiler/xla/stream_executor/device_options.h"
#include "tensorflow/compiler/xla/stream_executor/platform/port.h"
#include "tensorflow/compiler/xla/stream_executor/plugin.h"
#include "tensorflow/compiler/xla/stream_executor/trace_listener.h"
#include "tensorflow/tsl/platform/status.h"
#include "tensorflow/tsl/platform/statusor.h"

namespace stream_executor {

class StreamExecutor;
class DeviceDescription;

// An enum to represent different levels of stream priorities.
// This is to avoid platform-specific representations in abstractions.
enum class StreamPriority { Default = 0, Lowest, Highest };

// Returns a printable description of StreamPriority.
std::string StreamPriorityToString(StreamPriority priority);

// StreamExecutorConfig encapsulates the set of options for constructing a
// StreamExecutor for a given platform.
struct StreamExecutorConfig {
  // Sets members to defaults: -1 for ordinal (must be changed), and default
  // PluginConfig and DeviceOptions.
  StreamExecutorConfig();

  // Simple ordinal-setting constructor.
  explicit StreamExecutorConfig(int ordinal);

  // The GPU stream for which we are searching the executor.
  // If this field is specified for the search, others will be ignored.
  void* gpu_stream = nullptr;

  // The ordinal of the device to be managed by the returned StreamExecutor.
  int ordinal;

  // The PluginConfig for the returned StreamExecutor.
  PluginConfig plugin_config;

  // The DeviceOptions for the returned StreamExecutor.
  DeviceOptions device_options;
};

// Abstract base class for a platform registered with the MultiPlatformManager.
class Platform {
 public:
  virtual ~Platform();

  // A platform ID is a unique identifier for each registered platform type -
  // each platform is required to expose an ID to ensure unique registration and
  // as a target against which plugins can register.
  //
  // The macro below is provided to help generate a [process-unique] identifier.
  using Id = void*;

// Helper macro to define a plugin ID. To be used only inside plugin
// implementation files. Works by "reserving" an address/value (guaranteed to be
// unique) inside a process space.
#define PLATFORM_DEFINE_ID(ID_VAR_NAME) \
  namespace {                           \
  int plugin_id_value;                  \
  }                                     \
  const ::stream_executor::Platform::Id ID_VAR_NAME = &plugin_id_value;

  // Returns a key uniquely identifying this platform.
  virtual Id id() const = 0;

  // Name of this platform.
  virtual const std::string& Name() const = 0;

  // Returns the number of devices accessible on this platform.
  //
  // Note that, though these devices are visible, if there is only one userspace
  // context allowed for the device at a time and another process is using this
  // device, a call to ExecutorForDevice may return an error status.
  virtual int VisibleDeviceCount() const = 0;

  // Returns true iff the platform has been initialized.
  virtual bool Initialized() const;

  // Initializes the platform with a custom set of options. The platform must be
  // initialized before obtaining StreamExecutor objects.  The interpretation of
  // the platform_options argument is implementation specific.  This method may
  // return an error if unrecognized options are provided.  If using
  // MultiPlatformManager, this method will be called automatically by
  // InitializePlatformWithId/InitializePlatformWithName.
  virtual tsl::Status Initialize(
      const std::map<std::string, std::string>& platform_options);

  // Returns a populated DeviceDescription for the device at the given ordinal.
  // This should not require device initialization. Note that not all platforms
  // may support acquiring the DeviceDescription indirectly.
  //
  // Alternatively callers may call GetDeviceDescription() on the StreamExecutor
  // which returns a cached instance specific to the initialized StreamExecutor.
  virtual tsl::StatusOr<std::unique_ptr<DeviceDescription>>
  DescriptionForDevice(int ordinal) const = 0;

  // Returns a device with the given ordinal on this platform with a default
  // plugin configuration or, if none can be found with the given ordinal or
  // there is an error in opening a context to communicate with the device, an
  // error status is returned.
  //
  // Ownership of the executor is NOT transferred to the caller --
  // the Platform owns the executors in a singleton-like fashion.
  virtual tsl::StatusOr<StreamExecutor*> ExecutorForDevice(int ordinal) = 0;

  // Returns a device constructed with the options specified in "config".
  // Ownership of the executor is NOT transferred to the caller.
  virtual tsl::StatusOr<StreamExecutor*> GetExecutor(
      const StreamExecutorConfig& config) = 0;

  // Returns a device constructed with the options specified in "config" without
  // looking in or storing to the Platform's executor cache.
  // Ownership IS transferred to the caller.
  virtual tsl::StatusOr<std::unique_ptr<StreamExecutor>> GetUncachedExecutor(
      const StreamExecutorConfig& config) = 0;

 protected:
  // SE_DISALLOW_COPY_AND_ASSIGN declares a constructor, which suppresses the
  // presence of the default constructor. This statement re-enables it, which
  // simplifies subclassing.
  Platform() = default;

 private:
  SE_DISALLOW_COPY_AND_ASSIGN(Platform);
};

}  // namespace stream_executor

#endif  // TENSORFLOW_COMPILER_XLA_STREAM_EXECUTOR_PLATFORM_H_
