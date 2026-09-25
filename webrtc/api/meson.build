api_sources = [
  'audio/audio_frame.cc',
  'audio/audio_processing.cc',
  'audio/audio_processing_statistics.cc',
  'audio/builtin_audio_processing_builder.cc',
  'audio/channel_layout.cc',
  'audio/echo_canceller3_config.cc',
  'environment/deprecated_global_field_trials.cc',
  'environment/environment_factory.cc',
  'environment/force_test_environment.cc',
  'field_trials_registry.cc',
  'rtc_event_log/rtc_event_log.cc',
  'rtp_headers.cc',
  'task_queue/default_task_queue_factory_stdlib.cc',
  'task_queue/task_queue_base.cc',
  'units/frequency.cc',
  'units/time_delta.cc',
  'units/timestamp.cc',
  'video/color_space.cc',
  'video/hdr_metadata.cc',
  'video/video_content_type.cc',
  'video/video_timing.cc',
]

api_headers = [
  ['', 'array_view.h'],
  ['', 'field_trials_view.h'],
  ['', 'location.h'],
  ['', 'ref_count.h'],
  ['', 'ref_counted_base.h'],
  ['', 'rtc_event_log_output.h'],
  ['', 'scoped_refptr.h'],
  ['audio', 'audio_processing.h'],
  ['audio', 'audio_processing_statistics.h'],
  ['audio', 'builtin_audio_processing_builder.h'],
  ['audio', 'echo_canceller3_config.h'],
  ['audio', 'echo_control.h'],
  ['audio', 'neural_residual_echo_estimator.h'],
  ['environment', 'environment.h'],
  ['environment', 'environment_factory.h'],
  ['rtc_event_log', 'rtc_event.h'],
  ['rtc_event_log', 'rtc_event_log.h'],
  ['task_queue', 'task_queue_base.h'],
  ['task_queue', 'task_queue_factory.h'],
  ['units', 'time_delta.h'],
  ['units', 'timestamp.h'],
]

foreach h : api_headers
  install_headers(
    join_paths(h[0], h[1]),
    subdir: join_paths(include_subdir, 'api', h[0])
  )
endforeach


libapi = static_library('libapi',
    api_sources,
    dependencies: common_deps,
    include_directories: webrtc_inc,
    # builtin_audio_processing_builder.cc includes APM internals
    cpp_args : common_cxxflags + ['-DWEBRTC_APM_DEBUG_DUMP=0']
)

# link_whole so that public API entry points that are not referenced inside the
# library (e.g. CreateEnvironment(), BuiltinAudioProcessingBuilder) are kept
api_dep = declare_dependency(
    link_whole: libapi
)

