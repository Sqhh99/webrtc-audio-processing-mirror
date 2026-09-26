/*
 * Test main for the upstream WebRTC unit tests.
 *
 * This is a trimmed down version of upstream's test/test_main_lib.cc, without
 * the perf metrics, tracing and SSL setup that the audio processing tests do
 * not need.
 *
 * Use of this source code is governed by a BSD-style license
 * that can be found in the LICENSE file in the root of the source
 * tree.
 */

#include <cstdlib>
#include <filesystem>
#include <iostream>
#include <string>
#include <utility>
#include <vector>

#include "absl/flags/parse.h"
#include "api/environment/force_test_environment.h"
#include "rtc_base/logging.h"
#include "system_wrappers/include/metrics.h"
#include "test/gmock.h"

namespace {

// Exit code that makes meson (and automake) report the test as skipped.
constexpr int kSkipExitCode = 77;

bool HaveTestResources() {
  const char* dir = std::getenv("WEBRTC_TEST_RESOURCES_DIR");
  if (dir == nullptr || *dir == '\0') {
    return false;
  }
  // Written by tests/download_resources.py once all files are fetched.
  std::error_code ec;
  return std::filesystem::exists(std::filesystem::path(dir) / ".complete", ec);
}

}  // namespace

int main(int argc, char* argv[]) {
  testing::InitGoogleMock(&argc, argv);
  // Handles --force_fieldtrials (see test/create_test_field_trials.cc).
  absl::ParseCommandLine(argc, argv);

#if defined(WEBRTC_TEST_NEEDS_RESOURCES)
  if (!GTEST_FLAG_GET(list_tests) && !HaveTestResources()) {
    std::cerr << "Test resources not found, skipping. Run "
                 "tests/download_resources.py and point "
                 "WEBRTC_TEST_RESOURCES_DIR at the output directory."
              << std::endl;
    return kSkipExitCode;
  }
#endif

  webrtc::SetForceTestEnvironment(true);

  webrtc::LoggingConfig config;
  config.set_min_severity(webrtc::LS_WARNING);
  config.set_debug_severity(webrtc::LS_WARNING);
  config.set_log_to_stderr(true);
  webrtc::InitializeLogging(std::move(config));

  webrtc::metrics::Enable();

  return RUN_ALL_TESTS();
}
