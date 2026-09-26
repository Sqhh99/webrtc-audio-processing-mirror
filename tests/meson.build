# Upstream WebRTC unit tests for the audio processing module and its
# dependencies. The test sources and helpers live at their upstream paths in
# the webrtc/ tree; this directory only contains the glue to build and run
# them.

gtest_dep = dependency('gtest', main: false, required: get_option('tests'),
  default_options: ['default_library=static'])
gmock_dep = dependency('gmock', required: get_option('tests'),
  default_options: ['default_library=static'])
absl_flags_parse_dep = dependency('absl_flags_parse', required: get_option('tests'))

if not (gtest_dep.found() and gmock_dep.found() and absl_flags_parse_dep.found())
  subdir_done()
endif

test_inc = include_directories('include')

test_cflags = common_cxxflags + apm_flags + [
  # Upstream builds its tests with this defined, see webrtc.gni
  '-DWEBRTC_UNIT_TEST',
]

# Compiler compatibility shims for code written against clang.
if cpp.get_argument_syntax() == 'msvc'
  test_cflags += ['/FI' + meson.current_source_dir() / 'include' / 'test_compat.h']
else
  test_cflags += ['-include', meson.current_source_dir() / 'include' / 'test_compat.h']
endif

# GCC rejects a member function named after a type used earlier in the class,
# which upstream (built with clang) does in a couple of tests.
test_cflags += cpp.get_supported_arguments('-Wno-changes-meaning')

test_deps = [
  base_dep,
  api_dep,
  system_wrappers_dep,
  common_audio_dep,
  pffft_dep,
  rnnoise_dep,
  gtest_dep,
  gmock_dep,
  absl_flags_parse_dep,
] + common_deps

# Upstream test helpers, plus our replacement for the parts of upstream's
# test support that depend on the Chromium checkout layout.
test_support_sources = [
  '../webrtc/api/field_trials.cc',
  '../webrtc/api/test/time_controller.cc',
  '../webrtc/common_audio/wav_file.cc',
  '../webrtc/common_audio/wav_header.cc',
  '../webrtc/modules/audio_coding/neteq/tools/input_audio_file.cc',
  '../webrtc/modules/audio_processing/aec3/mock/mock_block_processor.cc',
  '../webrtc/modules/audio_processing/aec3/mock/mock_echo_remover.cc',
  '../webrtc/modules/audio_processing/aec3/mock/mock_render_delay_buffer.cc',
  '../webrtc/modules/audio_processing/aec3/mock/mock_render_delay_controller.cc',
  '../webrtc/modules/audio_processing/agc2/rnn_vad/test_utils.cc',
  '../webrtc/modules/audio_processing/test/audio_buffer_tools.cc',
  '../webrtc/modules/audio_processing/test/bitexactness_tools.cc',
  '../webrtc/modules/audio_processing/test/echo_canceller_test_tools.cc',
  '../webrtc/modules/audio_processing/test/fake_recording_device.cc',
  '../webrtc/modules/audio_processing/test/performance_timer.cc',
  '../webrtc/modules/audio_processing/test/test_utils.cc',
  '../webrtc/test/create_test_environment.cc',
  '../webrtc/test/create_test_field_trials.cc',
  '../webrtc/test/testsupport/file_utils.cc',
  'support/file_utils_override.cc',
  'support/neural_residual_echo_estimator_test_helper_stub.cc',
]

libtest_support = static_library('webrtc_test_support',
  test_support_sources,
  include_directories: [webrtc_inc, test_inc],
  dependencies: test_deps,
  cpp_args: test_cflags,
)

# The tests exercise internal classes, so link the library's objects directly
# rather than the shared library (which, on Windows, only exports the public
# API).
apm_objects = libwebrtc_audio_processing.extract_all_objects(recursive: false)

# Tests that run without any external data.
unittest_sources = [
  '../webrtc/common_audio/audio_converter_unittest.cc',
  '../webrtc/common_audio/audio_util_unittest.cc',
  '../webrtc/common_audio/channel_buffer_unittest.cc',
  '../webrtc/common_audio/fir_filter_unittest.cc',
  '../webrtc/common_audio/resampler/push_resampler_unittest.cc',
  '../webrtc/common_audio/resampler/push_sinc_resampler_unittest.cc',
  '../webrtc/common_audio/resampler/resampler_unittest.cc',
  '../webrtc/common_audio/resampler/sinc_resampler_unittest.cc',
  '../webrtc/common_audio/ring_buffer_unittest.cc',
  '../webrtc/common_audio/signal_processing/signal_processing_unittest.cc',
  '../webrtc/common_audio/smoothing_filter_unittest.cc',
  '../webrtc/common_audio/vad/vad_core_unittest.cc',
  '../webrtc/common_audio/vad/vad_filterbank_unittest.cc',
  '../webrtc/common_audio/vad/vad_gmm_unittest.cc',
  '../webrtc/common_audio/vad/vad_sp_unittest.cc',
  '../webrtc/common_audio/vad/vad_unittest.cc',
  '../webrtc/modules/audio_processing/aec3/adaptive_fir_filter_erl_unittest.cc',
  '../webrtc/modules/audio_processing/aec3/adaptive_fir_filter_unittest.cc',
  '../webrtc/modules/audio_processing/aec3/aec3_fft_unittest.cc',
  '../webrtc/modules/audio_processing/aec3/aec_state_unittest.cc',
  '../webrtc/modules/audio_processing/aec3/alignment_mixer_unittest.cc',
  '../webrtc/modules/audio_processing/aec3/api_call_jitter_metrics_unittest.cc',
  '../webrtc/modules/audio_processing/aec3/block_delay_buffer_unittest.cc',
  '../webrtc/modules/audio_processing/aec3/block_framer_unittest.cc',
  '../webrtc/modules/audio_processing/aec3/block_processor_metrics_unittest.cc',
  '../webrtc/modules/audio_processing/aec3/block_processor_unittest.cc',
  '../webrtc/modules/audio_processing/aec3/clockdrift_detector_unittest.cc',
  '../webrtc/modules/audio_processing/aec3/coarse_filter_update_gain_unittest.cc',
  '../webrtc/modules/audio_processing/aec3/comfort_noise_generator_unittest.cc',
  '../webrtc/modules/audio_processing/aec3/config_selector_unittest.cc',
  '../webrtc/modules/audio_processing/aec3/decimator_unittest.cc',
  '../webrtc/modules/audio_processing/aec3/echo_canceller3_unittest.cc',
  '../webrtc/modules/audio_processing/aec3/echo_path_delay_estimator_unittest.cc',
  '../webrtc/modules/audio_processing/aec3/echo_path_variability_unittest.cc',
  '../webrtc/modules/audio_processing/aec3/echo_remover_metrics_unittest.cc',
  '../webrtc/modules/audio_processing/aec3/echo_remover_unittest.cc',
  '../webrtc/modules/audio_processing/aec3/erl_estimator_unittest.cc',
  '../webrtc/modules/audio_processing/aec3/erle_estimator_unittest.cc',
  '../webrtc/modules/audio_processing/aec3/fft_data_unittest.cc',
  '../webrtc/modules/audio_processing/aec3/filter_analyzer_unittest.cc',
  '../webrtc/modules/audio_processing/aec3/frame_blocker_unittest.cc',
  '../webrtc/modules/audio_processing/aec3/matched_filter_lag_aggregator_unittest.cc',
  '../webrtc/modules/audio_processing/aec3/matched_filter_unittest.cc',
  '../webrtc/modules/audio_processing/aec3/moving_average_spectrum_unittest.cc',
  '../webrtc/modules/audio_processing/aec3/multi_channel_content_detector_unittest.cc',
  '../webrtc/modules/audio_processing/aec3/refined_filter_update_gain_unittest.cc',
  '../webrtc/modules/audio_processing/aec3/render_buffer_unittest.cc',
  '../webrtc/modules/audio_processing/aec3/render_delay_buffer_unittest.cc',
  '../webrtc/modules/audio_processing/aec3/render_delay_controller_metrics_unittest.cc',
  '../webrtc/modules/audio_processing/aec3/render_delay_controller_unittest.cc',
  '../webrtc/modules/audio_processing/aec3/render_signal_analyzer_unittest.cc',
  '../webrtc/modules/audio_processing/aec3/residual_echo_estimator_unittest.cc',
  '../webrtc/modules/audio_processing/aec3/reverb_model_estimator_unittest.cc',
  '../webrtc/modules/audio_processing/aec3/signal_dependent_erle_estimator_unittest.cc',
  '../webrtc/modules/audio_processing/aec3/subtractor_unittest.cc',
  '../webrtc/modules/audio_processing/aec3/suppression_filter_unittest.cc',
  '../webrtc/modules/audio_processing/aec3/suppression_gain_unittest.cc',
  '../webrtc/modules/audio_processing/aec3/vector_math_unittest.cc',
  '../webrtc/modules/audio_processing/agc2/adaptive_digital_gain_controller_unittest.cc',
  '../webrtc/modules/audio_processing/agc2/agc2_testing_common_unittest.cc',
  '../webrtc/modules/audio_processing/agc2/biquad_filter_unittest.cc',
  '../webrtc/modules/audio_processing/agc2/clipping_predictor_level_buffer_unittest.cc',
  '../webrtc/modules/audio_processing/agc2/clipping_predictor_unittest.cc',
  '../webrtc/modules/audio_processing/agc2/fixed_digital_level_estimator_unittest.cc',
  '../webrtc/modules/audio_processing/agc2/gain_applier_unittest.cc',
  '../webrtc/modules/audio_processing/agc2/input_volume_stats_reporter_unittest.cc',
  '../webrtc/modules/audio_processing/agc2/interpolated_gain_curve_unittest.cc',
  '../webrtc/modules/audio_processing/agc2/limiter_db_gain_curve_unittest.cc',
  '../webrtc/modules/audio_processing/agc2/limiter_unittest.cc',
  '../webrtc/modules/audio_processing/agc2/noise_level_estimator_unittest.cc',
  '../webrtc/modules/audio_processing/agc2/rnn_vad/features_extraction_unittest.cc',
  '../webrtc/modules/audio_processing/agc2/rnn_vad/ring_buffer_unittest.cc',
  '../webrtc/modules/audio_processing/agc2/rnn_vad/rnn_fc_unittest.cc',
  '../webrtc/modules/audio_processing/agc2/rnn_vad/rnn_unittest.cc',
  '../webrtc/modules/audio_processing/agc2/rnn_vad/sequence_buffer_unittest.cc',
  '../webrtc/modules/audio_processing/agc2/rnn_vad/spectral_features_internal_unittest.cc',
  '../webrtc/modules/audio_processing/agc2/rnn_vad/spectral_features_unittest.cc',
  '../webrtc/modules/audio_processing/agc2/rnn_vad/symmetric_matrix_buffer_unittest.cc',
  '../webrtc/modules/audio_processing/agc2/rnn_vad/vector_math_unittest.cc',
  '../webrtc/modules/audio_processing/agc2/saturation_protector_buffer_unittest.cc',
  '../webrtc/modules/audio_processing/agc2/saturation_protector_unittest.cc',
  '../webrtc/modules/audio_processing/agc2/speech_level_estimator_experimental_unittest.cc',
  '../webrtc/modules/audio_processing/agc2/speech_level_estimator_unittest.cc',
  '../webrtc/modules/audio_processing/agc2/speech_probability_buffer_unittest.cc',
  '../webrtc/modules/audio_processing/agc2/vad_wrapper_unittest.cc',
  '../webrtc/modules/audio_processing/audio_buffer_unittest.cc',
  '../webrtc/modules/audio_processing/audio_frame_view_unittest.cc',
  '../webrtc/modules/audio_processing/audio_processing_impl_locking_unittest.cc',
  '../webrtc/modules/audio_processing/audio_processing_impl_unittest.cc',
  '../webrtc/modules/audio_processing/capture_levels_adjuster/audio_samples_scaler_unittest.cc',
  '../webrtc/modules/audio_processing/capture_levels_adjuster/capture_levels_adjuster_unittest.cc',
  '../webrtc/modules/audio_processing/capture_mixer/audio_content_analyzer_unittest.cc',
  '../webrtc/modules/audio_processing/capture_mixer/capture_mixer_unittest.cc',
  '../webrtc/modules/audio_processing/capture_mixer/channel_content_remixer_unittest.cc',
  '../webrtc/modules/audio_processing/capture_mixer/dc_levels_estimator_unittest.cc',
  '../webrtc/modules/audio_processing/capture_mixer/energy_estimator_unittest.cc',
  '../webrtc/modules/audio_processing/capture_mixer/remixing_logic_unittest.cc',
  '../webrtc/modules/audio_processing/capture_mixer/saturation_estimator_unittest.cc',
  '../webrtc/modules/audio_processing/echo_detector/circular_buffer_unittest.cc',
  '../webrtc/modules/audio_processing/echo_detector/mean_variance_estimator_unittest.cc',
  '../webrtc/modules/audio_processing/echo_detector/moving_max_unittest.cc',
  '../webrtc/modules/audio_processing/echo_detector/normalized_covariance_estimator_unittest.cc',
  '../webrtc/modules/audio_processing/high_pass_filter_unittest.cc',
  '../webrtc/modules/audio_processing/ns/noise_suppressor_unittest.cc',
  '../webrtc/modules/audio_processing/post_filter_unittest.cc',
  '../webrtc/modules/audio_processing/residual_echo_detector_unittest.cc',
  '../webrtc/modules/audio_processing/rms_level_unittest.cc',
  '../webrtc/modules/audio_processing/splitting_filter_unittest.cc',
  '../webrtc/modules/audio_processing/test/echo_canceller_test_tools_unittest.cc',
  '../webrtc/modules/audio_processing/test/fake_recording_device_unittest.cc',
  '../webrtc/modules/audio_processing/utility/cascaded_biquad_filter_unittest.cc',
  '../webrtc/modules/audio_processing/utility/pffft_wrapper_unittest.cc',
  '../webrtc/modules/audio_processing/vad/gmm_unittest.cc',
  '../webrtc/modules/audio_processing/vad/pitch_internal_unittest.cc',
  '../webrtc/modules/audio_processing/vad/pole_zero_filter_unittest.cc',
  '../webrtc/modules/audio_processing/vad/vad_circular_buffer_unittest.cc',
]

webrtc_unittests = executable('webrtc_unittests',
  unittest_sources + ['support/test_main.cc'],
  objects: apm_objects,
  link_with: [libtest_support] + extra_libs,
  include_directories: [webrtc_inc, test_inc],
  dependencies: test_deps,
  cpp_args: test_cflags,
)

# Tests that need the upstream test resources (audio files and reference
# data), see download_resources.py. Without them, this binary reports itself as
# skipped.
resource_unittest_sources = [
  '../webrtc/modules/audio_processing/agc/agc_manager_direct_unittest.cc',
  '../webrtc/modules/audio_processing/agc/loudness_histogram_unittest.cc',
  '../webrtc/modules/audio_processing/agc2/input_volume_controller_unittest.cc',
  '../webrtc/modules/audio_processing/agc2/rnn_vad/auto_correlation_unittest.cc',
  '../webrtc/modules/audio_processing/agc2/rnn_vad/lp_residual_unittest.cc',
  '../webrtc/modules/audio_processing/agc2/rnn_vad/pitch_search_internal_unittest.cc',
  '../webrtc/modules/audio_processing/agc2/rnn_vad/pitch_search_unittest.cc',
  '../webrtc/modules/audio_processing/agc2/rnn_vad/rnn_gru_unittest.cc',
  '../webrtc/modules/audio_processing/agc2/rnn_vad/rnn_vad_unittest.cc',
  '../webrtc/modules/audio_processing/gain_control_unittest.cc',
  '../webrtc/modules/audio_processing/gain_controller2_unittest.cc',
  '../webrtc/modules/audio_processing/vad/pitch_based_vad_unittest.cc',
  '../webrtc/modules/audio_processing/vad/standalone_vad_unittest.cc',
  '../webrtc/modules/audio_processing/vad/vad_audio_proc_unittest.cc',
  '../webrtc/modules/audio_processing/vad/voice_activity_detector_unittest.cc',
]

webrtc_resource_unittests = executable('webrtc_resource_unittests',
  resource_unittest_sources + ['support/test_main.cc'],
  objects: apm_objects,
  link_with: [libtest_support] + extra_libs,
  include_directories: [webrtc_inc, test_inc],
  dependencies: test_deps,
  cpp_args: test_cflags + ['-DWEBRTC_TEST_NEEDS_RESOURCES'],
)

test_resources_dir = get_option('test-resources-dir')
if test_resources_dir == ''
  test_resources_dir = meson.project_build_root() / 'test-resources'
endif

test('webrtc_resource_unittests', webrtc_resource_unittests,
  env: ['WEBRTC_TEST_RESOURCES_DIR=' + test_resources_dir],
  timeout: 1200,
  protocol: 'gtest',
  suite: 'resources',
)

# Tests that need parts of upstream this build leaves out.
excluded_tests = [
  # Needs TFLite
  'AudioProcessingImplTest.NeuralResidualEchoEstimatorInjection',
]

test('webrtc_unittests', webrtc_unittests,
  args: ['--gtest_filter=-' + ':'.join(excluded_tests)],
  timeout: 1200,
  protocol: 'gtest',
)
