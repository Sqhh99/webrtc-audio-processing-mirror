# webrtc-audio-processing

[![Build](https://github.com/Sqhh99/webrtc-audio-processing/actions/workflows/build.yml/badge.svg)](https://github.com/Sqhh99/webrtc-audio-processing/actions/workflows/build.yml)
[![Release](https://img.shields.io/github/v/release/Sqhh99/webrtc-audio-processing)](https://github.com/Sqhh99/webrtc-audio-processing/releases/latest)

The AudioProcessing module (APM) of [WebRTC](https://webrtc.googlesource.com/src),
packaged as a standalone library with a [Meson](https://mesonbuild.com/) build,
with prebuilt binaries for Linux, Raspberry Pi OS, macOS, Windows, Android and
iOS.

The APM is the audio front end of WebRTC. It provides:

* acoustic echo cancellation (AEC3)
* noise suppression
* automatic gain control (AGC1 and AGC2)
* a high-pass filter, capture level adjustment and a capture mixer
* voice activity and echo detection

This repository is based on the
[freedesktop.org webrtc-audio-processing](https://gitlab.freedesktop.org/pulseaudio/webrtc-audio-processing)
project, which PulseAudio and PipeWire use. It keeps the same layout and build
system, and adds:

* newer upstream code: currently WebRTC M153 (WebRTC
  [`9ea5afcad0`](https://webrtc.googlesource.com/src/+/9ea5afcad008b940468c2a15aec339592cf5a935),
  as used by Chromium 153.0.8010.55)
* the upstream unit tests, run in CI on Linux, macOS and Windows
* prebuilt release packages for more platforms

The code under `webrtc/` is kept identical to upstream, except for the small
patches tracked in [`patches/`](patches/).

## Contents

* [Prebuilt binaries](#prebuilt-binaries)
* [Using the library](#using-the-library)
* [Building from source](#building-from-source)
* [Running the tests](#running-the-tests)
* [Repository layout](#repository-layout)
* [Maintenance](#maintenance)
* [Feedback](#feedback)
* [License](#license)

## Prebuilt binaries

Every [release](https://github.com/Sqhh99/webrtc-audio-processing/releases)
provides:

| Package | Platform |
|---|---|
| `webrtc-audio-processing.ubuntu-22.04_x86_64.tar.gz` | Ubuntu 22.04, x86_64 |
| `webrtc-audio-processing.ubuntu-24.04_x86_64.tar.gz` | Ubuntu 24.04, x86_64 |
| `webrtc-audio-processing.ubuntu-26.04_x86_64.tar.gz` | Ubuntu 26.04, x86_64 |
| `webrtc-audio-processing.ubuntu-22.04_armv8.tar.gz` | Ubuntu 22.04, arm64 |
| `webrtc-audio-processing.ubuntu-24.04_armv8.tar.gz` | Ubuntu 24.04, arm64 |
| `webrtc-audio-processing.ubuntu-26.04_armv8.tar.gz` | Ubuntu 26.04, arm64 |
| `webrtc-audio-processing.raspberry-pi-os_armv8.tar.gz` | Raspberry Pi OS 64-bit (Debian bookworm) |
| `webrtc-audio-processing.macos_x86_64.tar.gz` | macOS 12+, Intel |
| `webrtc-audio-processing.macos_arm64.tar.gz` | macOS 12+, Apple silicon |
| `webrtc-audio-processing.windows_x86_64.zip` | Windows, x64 (MSVC) |
| `webrtc-audio-processing.windows_arm64.zip` | Windows, arm64 (MSVC) |
| `webrtc-audio-processing.android.tar.gz` | Android API 24+: `arm64-v8a`, `armeabi-v7a`, `x86_64` |
| `WebRTCAudioProcessing.xcframework.zip` | iOS 14+ devices and simulator (static library) |

The Linux, macOS and Windows packages contain the shared library, its headers
(in `include/webrtc-audio-processing-3`) and a pkg-config file. abseil-cpp is
linked in statically, and its headers are included in `include/absl`. Each
package also contains the licenses of the code it includes.

Releases are tagged after the upstream version they are built from, as
`m<milestone>.<branch>.<branch position>.<build>`. For example,
`m153.8010.0.1` is the second release built from the start of the WebRTC M153
branch (`branch-heads/8010`).

## Using the library

This library exposes the upstream C++ API as is. The main headers are
`api/audio/audio_processing.h` and `api/audio/builtin_audio_processing_builder.h`:

```cpp
#include <cstdint>

#include <api/audio/audio_processing.h>
#include <api/audio/builtin_audio_processing_builder.h>
#include <api/environment/environment_factory.h>

int main() {
  webrtc::AudioProcessing::Config config;
  config.echo_canceller.enabled = true;
  config.noise_suppression.enabled = true;
  config.noise_suppression.level =
      webrtc::AudioProcessing::Config::NoiseSuppression::kHigh;
  config.gain_controller2.enabled = true;
  config.high_pass_filter.enabled = true;

  webrtc::scoped_refptr<webrtc::AudioProcessing> apm =
      webrtc::BuiltinAudioProcessingBuilder(config).Build(
          webrtc::CreateEnvironment());

  // The APM works on 10 ms frames.
  webrtc::StreamConfig stream(/*sample_rate_hz=*/48000, /*num_channels=*/1);
  int16_t playback[480] = {};  // audio about to be played out
  int16_t capture[480] = {};   // audio just captured from the microphone

  apm->ProcessReverseStream(playback, stream, stream, playback);
  apm->set_stream_delay_ms(40);  // delay between the two, if known
  apm->ProcessStream(capture, stream, stream, capture);
  return 0;
}
```

The code needs C++20. To build it against an installed copy of the library:

```sh
c++ -std=c++20 app.cc $(pkg-config --cflags --libs webrtc-audio-processing-3)
```

With a prebuilt package extracted to `$PKG`, point pkg-config at it:

```sh
export PKG_CONFIG_PATH=$PKG/lib/pkgconfig
c++ -std=c++20 app.cc \
  $(pkg-config --define-prefix --cflags --libs webrtc-audio-processing-3)
```

Packages from releases before `m153.8010.0.2` also need `-I$PKG/include`, for
the bundled abseil headers. Without pkg-config (for example with MSVC), add
`$PKG/include` and `$PKG/include/webrtc-audio-processing-3` to the include path,
define `WEBRTC_POSIX` (`WEBRTC_WIN` on Windows), and link with
`webrtc-audio-processing-3`.
[`examples/run-offline.cpp`](examples/run-offline.cpp) is a complete example
that runs echo cancellation over raw audio files.

The upstream API is not stable. When it changes incompatibly, the major version
of the package goes up: it is currently `webrtc-audio-processing-3`, so
different major versions can be installed side by side. See [NEWS](NEWS) for
the changes in each version.

## Building from source

Requirements:

* A C++20 compiler: GCC 11 or newer, Clang, or MSVC
* [Meson](https://mesonbuild.com/) 0.63 or newer, and Ninja
* [abseil-cpp](https://abseil.io/) 20250814 or newer. If it is not installed,
  Meson downloads and builds it as a subproject

```sh
meson setup build --prefix=$PWD/install
meson compile -C build
meson install -C build
```

The library, headers and pkg-config file are then in `install/`. To always use
the abseil subproject rather than a system copy, add
`--force-fallback-for=abseil-cpp` to `meson setup`.

Build options (pass them to `meson setup` as `-Doption=value`):

| Option | Default | Description |
|---|---|---|
| `neon` | `auto` | NEON optimizations on ARM. `auto` does not currently turn them on, so pass `-Dneon=enabled` on ARM (the prebuilt ARM packages do, except on Windows) |
| `inline-sse` | `true` | Inline SSE2 code on x86. Disable it for x86 CPUs without SSE2 |
| `tests` | `disabled` | Build the upstream unit tests, see [below](#running-the-tests) |
| `test-resources-dir` | `<builddir>/test-resources` | Where the tests look for their resource files |
| `gnustl` | `auto` | Use gnustl (Android only) |

To reproduce a release build, or to cross-compile for Android and iOS, use
[`ci/build.py`](ci/build.py), which the CI runs for every release package:

```sh
ci/build.py native --package my-build --tests  # this machine
ci/build.py android                            # needs the Android NDK
ci/build.py ios                                # needs Xcode
```

The packages are written to `dist/`.

## Running the tests

The upstream WebRTC unit tests for the audio processing module (and the
`common_audio` code it uses) are included, about 4,300 tests in all. They need
[GoogleTest](https://github.com/google/googletest), which is taken from the
system or downloaded as a subproject.

```sh
meson setup build -Dtests=enabled
meson compile -C build

# Some tests need audio files and reference data from upstream, which are
# downloaded from Google Cloud Storage (about 19 MB). Without them, those
# tests are reported as skipped.
python3 tests/download_resources.py build/test-resources

meson test -C build --print-errorlogs
```

## Repository layout

| Path | Contents |
|---|---|
| `webrtc/` | Upstream WebRTC code, at the same paths as upstream, with the Meson build files |
| `patches/` | The changes made to the upstream code, as patch files |
| `tests/` | Glue to build and run the upstream unit tests, and the resource download script |
| `examples/` | Example programs |
| `ci/` | The build and packaging script used by CI and releases |
| `subprojects/` | Meson wraps for abseil-cpp and GoogleTest |

## Maintenance

* [UPDATING.md](UPDATING.md) explains how to update the code to a newer
  upstream version
* [RELEASING.md](RELEASING.md) explains how to make a release
* [NEWS](NEWS) lists the changes in each version

## Feedback

Issues and pull requests are welcome in this
[repository](https://github.com/Sqhh99/webrtc-audio-processing/issues). Build
system changes that are useful beyond this repository may also be of interest to
the [freedesktop.org project](https://gitlab.freedesktop.org/pulseaudio/webrtc-audio-processing).

## License

The WebRTC code is under the BSD 3-clause license in [COPYING](COPYING), with
the patent grant in [webrtc/PATENTS](webrtc/PATENTS). The library also includes
third-party code under its own license: abseil-cpp (Apache 2.0), pffft
([FFTPACK license](webrtc/third_party/pffft/LICENSE)) and rnnoise
([BSD license](webrtc/third_party/rnnoise/COPYING)).
