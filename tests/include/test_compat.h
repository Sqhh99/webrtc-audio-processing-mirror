// Force-included into the upstream unit tests (see tests/meson.build).
//
// Some tests use `#if defined(__has_feature) && __has_feature(...)`, which
// only preprocesses with compilers that know __has_feature (clang, GCC >= 14).
#ifndef __has_feature
#define __has_feature(x) 0
#endif
