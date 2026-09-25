system_wrappers_sources = [
  'source/clock.cc',
  'source/metrics.cc',
]

system_headers = [
  'include/clock.h',
  'include/metrics.h',
  'include/ntp_time.h',
]

install_headers(system_headers,
    subdir: join_paths(include_subdir, 'system_wrappers', 'include')
)

libsystem_wrappers = static_library('system_wrappers',
    system_wrappers_sources,
    dependencies: common_deps,
    include_directories: webrtc_inc,
    c_args : common_cflags,
    cpp_args : common_cxxflags
)

system_wrappers_dep = declare_dependency(
    link_with: libsystem_wrappers
)
