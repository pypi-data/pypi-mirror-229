// This file is part of Eigen, a lightweight C++ template library
// for linear algebra.
//
// Mehdi Goli    Codeplay Software Ltd.
// Ralph Potter  Codeplay Software Ltd.
// Luke Iwanski  Codeplay Software Ltd.
// Contact: <eigen@codeplay.com>
//
// This Source Code Form is subject to the terms of the Mozilla
// Public License v. 2.0. If a copy of the MPL was not distributed
// with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

/*****************************************************************
 * PacketMath.h
 *
 * \brief:
 *  PacketMath
 *
 *****************************************************************/

#ifndef EIGEN_PACKET_MATH_SYCL_H
#define EIGEN_PACKET_MATH_SYCL_H
#include <type_traits>

#include "../../InternalHeaderCheck.h"

namespace Eigen {

namespace internal {
#ifdef SYCL_DEVICE_ONLY
#define SYCL_PLOAD(packet_type, AlignedType)                          \
  template <>                                                         \
  EIGEN_DEVICE_FUNC EIGEN_ALWAYS_INLINE packet_type                   \
      pload##AlignedType<packet_type>(                                \
          const typename unpacket_traits<packet_type>::type* from) {  \
   auto ptr = cl::sycl::address_space_cast<cl::sycl::access::address_space::generic_space, cl::sycl::access::decorated::no>(from);\
    packet_type res{};                                                \
    res.load(0, ptr);                                     \
    return res;                                                       \
  }

SYCL_PLOAD(cl::sycl::cl_float4, u)
SYCL_PLOAD(cl::sycl::cl_float4, )
SYCL_PLOAD(cl::sycl::cl_double2, u)
SYCL_PLOAD(cl::sycl::cl_double2, )

#undef SYCL_PLOAD

#define SYCL_PSTORE(scalar, packet_type, alignment)             \
  template <>                                                   \
  EIGEN_DEVICE_FUNC EIGEN_ALWAYS_INLINE void pstore##alignment( \
      scalar* to, const packet_type& from) {                    \
    auto ptr = cl::sycl::address_space_cast<cl::sycl::access::address_space::generic_space, cl::sycl::access::decorated::no>(to);\
    from.store(0, ptr);                               \
  }

SYCL_PSTORE(float, cl::sycl::cl_float4, )
SYCL_PSTORE(float, cl::sycl::cl_float4, u)
SYCL_PSTORE(double, cl::sycl::cl_double2, )
SYCL_PSTORE(double, cl::sycl::cl_double2, u)

#undef SYCL_PSTORE

#define SYCL_PSET1(packet_type)                                         \
  template <>                                                           \
  EIGEN_DEVICE_FUNC EIGEN_ALWAYS_INLINE packet_type pset1<packet_type>( \
      const typename unpacket_traits<packet_type>::type& from) {        \
    return packet_type(from);                                           \
  }

// global space
SYCL_PSET1(cl::sycl::cl_float4)
SYCL_PSET1(cl::sycl::cl_double2)

#undef SYCL_PSET1

template <typename packet_type>
struct get_base_packet {
  template <typename sycl_multi_pointer>
  static EIGEN_DEVICE_FUNC EIGEN_STRONG_INLINE packet_type
  get_ploaddup(sycl_multi_pointer) {}

  template <typename sycl_multi_pointer>
  static EIGEN_DEVICE_FUNC EIGEN_STRONG_INLINE packet_type
  get_pgather(sycl_multi_pointer, Index) {}
};

template <>
struct get_base_packet<cl::sycl::cl_float4> {
  template <typename sycl_multi_pointer>
  static EIGEN_DEVICE_FUNC EIGEN_STRONG_INLINE cl::sycl::cl_float4 get_ploaddup(
      sycl_multi_pointer from) {
    return cl::sycl::cl_float4(from[0], from[0], from[1], from[1]);
  }
  template <typename sycl_multi_pointer>
  static EIGEN_DEVICE_FUNC EIGEN_STRONG_INLINE cl::sycl::cl_float4 get_pgather(
      sycl_multi_pointer from, Index stride) {
    return cl::sycl::cl_float4(from[0 * stride], from[1 * stride],
                               from[2 * stride], from[3 * stride]);
  }

  template <typename sycl_multi_pointer>
  static EIGEN_DEVICE_FUNC EIGEN_STRONG_INLINE void set_pscatter(
      sycl_multi_pointer to, const cl::sycl::cl_float4& from, Index stride) {
    auto tmp = stride;
    to[0] = from.x();
    to[tmp] = from.y();
    to[tmp += stride] = from.z();
    to[tmp += stride] = from.w();
  }
  static EIGEN_DEVICE_FUNC EIGEN_STRONG_INLINE cl::sycl::cl_float4 set_plset(
      const float& a) {
    return cl::sycl::cl_float4(static_cast<float>(a), static_cast<float>(a + 1),
                               static_cast<float>(a + 2),
                               static_cast<float>(a + 3));
  }
};

template <>
struct get_base_packet<cl::sycl::cl_double2> {
  template <typename sycl_multi_pointer>
  static EIGEN_DEVICE_FUNC EIGEN_STRONG_INLINE cl::sycl::cl_double2
  get_ploaddup(const sycl_multi_pointer from) {
    return cl::sycl::cl_double2(from[0], from[0]);
  }

  template <typename sycl_multi_pointer, typename Index>
  static EIGEN_DEVICE_FUNC EIGEN_STRONG_INLINE cl::sycl::cl_double2 get_pgather(
      const sycl_multi_pointer from, Index stride) {
    return cl::sycl::cl_double2(from[0 * stride], from[1 * stride]);
  }

  template <typename sycl_multi_pointer>
  static EIGEN_DEVICE_FUNC EIGEN_STRONG_INLINE void set_pscatter(
      sycl_multi_pointer to, const cl::sycl::cl_double2& from, Index stride) {
    to[0] = from.x();
    to[stride] = from.y();
  }

  static EIGEN_DEVICE_FUNC EIGEN_STRONG_INLINE cl::sycl::cl_double2 set_plset(
      const double& a) {
    return cl::sycl::cl_double2(static_cast<double>(a),
                                static_cast<double>(a + 1));
  }
};

#define SYCL_PLOAD_DUP_SPECILIZE(packet_type)                              \
  template <>                                                              \
  EIGEN_DEVICE_FUNC EIGEN_STRONG_INLINE packet_type ploaddup<packet_type>( \
      const typename unpacket_traits<packet_type>::type* from) {           \
    return get_base_packet<packet_type>::get_ploaddup(from);               \
  }

SYCL_PLOAD_DUP_SPECILIZE(cl::sycl::cl_float4)
SYCL_PLOAD_DUP_SPECILIZE(cl::sycl::cl_double2)

#undef SYCL_PLOAD_DUP_SPECILIZE

#define SYCL_PLSET(packet_type)                                         \
  template <>                                                           \
  EIGEN_DEVICE_FUNC EIGEN_ALWAYS_INLINE packet_type plset<packet_type>( \
      const typename unpacket_traits<packet_type>::type& a) {           \
    return get_base_packet<packet_type>::set_plset(a);                  \
  }
SYCL_PLSET(cl::sycl::cl_float4)
SYCL_PLSET(cl::sycl::cl_double2)

#undef SYCL_PLSET

#define SYCL_PGATHER_SPECILIZE(scalar, packet_type)                            \
  template <>                                                                  \
  EIGEN_DEVICE_FUNC EIGEN_STRONG_INLINE packet_type                            \
  pgather<scalar, packet_type>(                                                \
      const typename unpacket_traits<packet_type>::type* from, Index stride) { \
    return get_base_packet<packet_type>::get_pgather(from, stride);            \
  }

SYCL_PGATHER_SPECILIZE(float, cl::sycl::cl_float4)
SYCL_PGATHER_SPECILIZE(double, cl::sycl::cl_double2)

#undef SYCL_PGATHER_SPECILIZE

#define SYCL_PSCATTER_SPECILIZE(scalar, packet_type)                        \
  template <>                                                               \
  EIGEN_DEVICE_FUNC EIGEN_STRONG_INLINE void pscatter<scalar, packet_type>( \
      typename unpacket_traits<packet_type>::type * to,                     \
      const packet_type& from, Index stride) {                              \
    get_base_packet<packet_type>::set_pscatter(to, from, stride);           \
  }

SYCL_PSCATTER_SPECILIZE(float, cl::sycl::cl_float4)
SYCL_PSCATTER_SPECILIZE(double, cl::sycl::cl_double2)

#undef SYCL_PSCATTER_SPECILIZE

#define SYCL_PMAD(packet_type)                                            \
  template <>                                                             \
  EIGEN_DEVICE_FUNC EIGEN_ALWAYS_INLINE packet_type pmadd(                \
      const packet_type& a, const packet_type& b, const packet_type& c) { \
    return cl::sycl::mad(a, b, c);                                        \
  }

SYCL_PMAD(cl::sycl::cl_float4)
SYCL_PMAD(cl::sycl::cl_double2)
#undef SYCL_PMAD

template <>
EIGEN_DEVICE_FUNC EIGEN_ALWAYS_INLINE float pfirst<cl::sycl::cl_float4>(
    const cl::sycl::cl_float4& a) {
  return a.x();
}
template <>
EIGEN_DEVICE_FUNC EIGEN_ALWAYS_INLINE double pfirst<cl::sycl::cl_double2>(
    const cl::sycl::cl_double2& a) {
  return a.x();
}

template <>
EIGEN_DEVICE_FUNC EIGEN_ALWAYS_INLINE float predux<cl::sycl::cl_float4>(
    const cl::sycl::cl_float4& a) {
  return a.x() + a.y() + a.z() + a.w();
}

template <>
EIGEN_DEVICE_FUNC EIGEN_ALWAYS_INLINE double predux<cl::sycl::cl_double2>(
    const cl::sycl::cl_double2& a) {
  return a.x() + a.y();
}

template <>
EIGEN_DEVICE_FUNC EIGEN_ALWAYS_INLINE float predux_max<cl::sycl::cl_float4>(
    const cl::sycl::cl_float4& a) {
  return cl::sycl::fmax(cl::sycl::fmax(a.x(), a.y()),
                        cl::sycl::fmax(a.z(), a.w()));
}
template <>
EIGEN_DEVICE_FUNC EIGEN_ALWAYS_INLINE double predux_max<cl::sycl::cl_double2>(
    const cl::sycl::cl_double2& a) {
  return cl::sycl::fmax(a.x(), a.y());
}

template <>
EIGEN_DEVICE_FUNC EIGEN_ALWAYS_INLINE float predux_min<cl::sycl::cl_float4>(
    const cl::sycl::cl_float4& a) {
  return cl::sycl::fmin(cl::sycl::fmin(a.x(), a.y()),
                        cl::sycl::fmin(a.z(), a.w()));
}
template <>
EIGEN_DEVICE_FUNC EIGEN_ALWAYS_INLINE double predux_min<cl::sycl::cl_double2>(
    const cl::sycl::cl_double2& a) {
  return cl::sycl::fmin(a.x(), a.y());
}

template <>
EIGEN_DEVICE_FUNC EIGEN_ALWAYS_INLINE float predux_mul<cl::sycl::cl_float4>(
    const cl::sycl::cl_float4& a) {
  return a.x() * a.y() * a.z() * a.w();
}
template <>
EIGEN_DEVICE_FUNC EIGEN_ALWAYS_INLINE double predux_mul<cl::sycl::cl_double2>(
    const cl::sycl::cl_double2& a) {
  return a.x() * a.y();
}

template <>
EIGEN_DEVICE_FUNC EIGEN_ALWAYS_INLINE cl::sycl::cl_float4
pabs<cl::sycl::cl_float4>(const cl::sycl::cl_float4& a) {
  return cl::sycl::cl_float4(cl::sycl::fabs(a.x()), cl::sycl::fabs(a.y()),
                             cl::sycl::fabs(a.z()), cl::sycl::fabs(a.w()));
}
template <>
EIGEN_DEVICE_FUNC EIGEN_ALWAYS_INLINE cl::sycl::cl_double2
pabs<cl::sycl::cl_double2>(const cl::sycl::cl_double2& a) {
  return cl::sycl::cl_double2(cl::sycl::fabs(a.x()), cl::sycl::fabs(a.y()));
}

template <typename Packet>
EIGEN_DEVICE_FUNC EIGEN_ALWAYS_INLINE Packet sycl_pcmp_le(const Packet &a,
                                                          const Packet &b) {
  return (a <= b).template as<Packet>();
}

template <typename Packet>
EIGEN_DEVICE_FUNC EIGEN_ALWAYS_INLINE Packet sycl_pcmp_lt(const Packet &a,
                                                          const Packet &b) {
  return (a < b).template as<Packet>();
}

template <typename Packet>
EIGEN_DEVICE_FUNC EIGEN_ALWAYS_INLINE Packet sycl_pcmp_eq(const Packet &a,
                                                          const Packet &b) {
  return (a == b).template as<Packet>();
}

#define SYCL_PCMP(OP, TYPE)                                                    \
  template <>                                                                  \
  EIGEN_DEVICE_FUNC EIGEN_ALWAYS_INLINE TYPE pcmp_##OP<TYPE>(const TYPE &a,    \
                                                             const TYPE &b) {  \
    return sycl_pcmp_##OP<TYPE>(a, b);                                         \
  }

SYCL_PCMP(le, cl::sycl::cl_float4)
SYCL_PCMP(lt, cl::sycl::cl_float4)
SYCL_PCMP(eq, cl::sycl::cl_float4)
SYCL_PCMP(le, cl::sycl::cl_double2)
SYCL_PCMP(lt, cl::sycl::cl_double2)
SYCL_PCMP(eq, cl::sycl::cl_double2)
#undef SYCL_PCMP

EIGEN_DEVICE_FUNC EIGEN_ALWAYS_INLINE void ptranspose(
    PacketBlock<cl::sycl::cl_float4, 4>& kernel) {
  float tmp = kernel.packet[0].y();
  kernel.packet[0].y() = kernel.packet[1].x();
  kernel.packet[1].x() = tmp;

  tmp = kernel.packet[0].z();
  kernel.packet[0].z() = kernel.packet[2].x();
  kernel.packet[2].x() = tmp;

  tmp = kernel.packet[0].w();
  kernel.packet[0].w() = kernel.packet[3].x();
  kernel.packet[3].x() = tmp;

  tmp = kernel.packet[1].z();
  kernel.packet[1].z() = kernel.packet[2].y();
  kernel.packet[2].y() = tmp;

  tmp = kernel.packet[1].w();
  kernel.packet[1].w() = kernel.packet[3].y();
  kernel.packet[3].y() = tmp;

  tmp = kernel.packet[2].w();
  kernel.packet[2].w() = kernel.packet[3].z();
  kernel.packet[3].z() = tmp;
}

EIGEN_DEVICE_FUNC EIGEN_ALWAYS_INLINE void ptranspose(
    PacketBlock<cl::sycl::cl_double2, 2>& kernel) {
  double tmp = kernel.packet[0].y();
  kernel.packet[0].y() = kernel.packet[1].x();
  kernel.packet[1].x() = tmp;
}

template <>
EIGEN_DEVICE_FUNC EIGEN_ALWAYS_INLINE cl::sycl::cl_float4 pblend(
    const Selector<unpacket_traits<cl::sycl::cl_float4>::size>& ifPacket,
    const cl::sycl::cl_float4& thenPacket,
    const cl::sycl::cl_float4& elsePacket) {
  cl::sycl::cl_int4 condition(
      ifPacket.select[0] ? 0 : -1, ifPacket.select[1] ? 0 : -1,
      ifPacket.select[2] ? 0 : -1, ifPacket.select[3] ? 0 : -1);
  return cl::sycl::select(thenPacket, elsePacket, condition);
}

template <>
inline cl::sycl::cl_double2 pblend(
    const Selector<unpacket_traits<cl::sycl::cl_double2>::size>& ifPacket,
    const cl::sycl::cl_double2& thenPacket,
    const cl::sycl::cl_double2& elsePacket) {
  cl::sycl::cl_long2 condition(ifPacket.select[0] ? 0 : -1,
                               ifPacket.select[1] ? 0 : -1);
  return cl::sycl::select(thenPacket, elsePacket, condition);
}
#endif  // SYCL_DEVICE_ONLY

}  // end namespace internal

}  // end namespace Eigen

#endif  // EIGEN_PACKET_MATH_SYCL_H
