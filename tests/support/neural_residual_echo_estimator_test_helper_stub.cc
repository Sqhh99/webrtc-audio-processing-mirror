/*
 * Stub for upstream's
 * modules/audio_processing/aec3/neural_residual_echo_estimator/
 *   neural_residual_echo_estimator_test_helper.cc
 *
 * The real helper needs TFLite, which is not part of this build (neither is
 * the neural residual echo estimator itself). The only test using it,
 * AudioProcessingImplTest.NeuralResidualEchoEstimatorInjection, is filtered
 * out in tests/meson.build.
 *
 * Use of this source code is governed by a BSD-style license
 * that can be found in the LICENSE file in the root of the source
 * tree.
 */

#include <memory>

#include "modules/audio_processing/aec3/neural_residual_echo_estimator/neural_residual_echo_estimator_test_helper.h"

namespace webrtc {

std::unique_ptr<NeuralResidualEchoEstimatorTestHelper>
CreateNeuralResidualEchoEstimatorTestHelper() {
  return nullptr;
}

}  // namespace webrtc
