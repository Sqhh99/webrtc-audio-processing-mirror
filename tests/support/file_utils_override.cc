/*
 * Replacement for upstream's test/testsupport/file_utils_override.cc.
 *
 * Upstream locates resources relative to the Chromium checkout layout, and
 * needs Objective-C helpers on Apple platforms. Here, resources come from the
 * directory in the WEBRTC_TEST_RESOURCES_DIR environment variable (populated
 * by tests/download_resources.py), and output goes to the system temporary
 * directory.
 *
 * Use of this source code is governed by a BSD-style license
 * that can be found in the LICENSE file in the root of the source
 * tree.
 */

#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <filesystem>
#include <random>
#include <string>

#include "absl/strings/string_view.h"
#include "test/testsupport/file_utils_override.h"

namespace webrtc {

// Upstream implements this in rtc_base/crypto_random.cc on top of
// BoringSSL/OpenSSL. file_utils.cc only uses it to name temporary
// directories, so a non-cryptographic generator is fine here.
std::string CreateRandomUuid() {
  std::random_device rd;
  std::mt19937_64 gen(rd());
  uint64_t hi = gen();
  uint64_t lo = gen();
  // Version 4, variant 1.
  hi = (hi & 0xffffffffffff0fffULL) | 0x0000000000004000ULL;
  lo = (lo & 0x3fffffffffffffffULL) | 0x8000000000000000ULL;
  char buf[37];
  std::snprintf(buf, sizeof(buf), "%08x-%04x-%04x-%04x-%012llx",
                static_cast<unsigned>(hi >> 32),
                static_cast<unsigned>((hi >> 16) & 0xffff),
                static_cast<unsigned>(hi & 0xffff),
                static_cast<unsigned>(lo >> 48),
                static_cast<unsigned long long>(lo & 0xffffffffffffULL));
  return buf;
}

namespace test {
namespace internal {

std::string OutputPath() {
  std::error_code ec;
  std::filesystem::path dir = std::filesystem::temp_directory_path(ec);
  if (ec) {
    dir = std::filesystem::current_path();
  }
  return dir.string() + std::string(1, std::filesystem::path::preferred_separator);
}

std::string WorkingDir() {
  return std::filesystem::current_path().string();
}

std::string ResourcePath(absl::string_view name, absl::string_view extension) {
  const char* dir = std::getenv("WEBRTC_TEST_RESOURCES_DIR");
  std::filesystem::path path(dir != nullptr ? dir : "resources");
  path /= std::string(name) + "." + std::string(extension);
  return path.string();
}

}  // namespace internal
}  // namespace test
}  // namespace webrtc
