Updating
=====

Assembling some quick notes on maintaining this tree vs. the upstream WebRTC
project source code.

1. The code is currently synced agains whatever revision of the upstream
   webrtc git repository Chromium uses.

2. Instructions on checking out the Chromium tree are on the
   [WebRTC repo][get-webrtc]. As a shortcut, you can look at the DEPS file
   in the Chromium tree for the current webrtc version being used, and then
   just use that commit hash with the webrtc tree.

3. [Meld][meld] is a great tool for diffing two directories. Start by running
   it on ```webrtc-audio-processing/webrtc``` and
   ```chromium/third_party/webrtc```.

   * For each directory in the ```webrtc-audio-processing``` tree, go over the
     corresponding code in the ```chromium``` tree.

   * Examine changed files, and pick any new changes. A small number of files
     in the ```webrtc-audio-processing``` tree have been changed by hand, make
     sure that those are not overwritten.

   * unittest files have been left out since they are not built or used.

   * BUILD.gn files have been copied to keep track of changes to the build
     system upstreama.

   * Arch-specific files usually have special handling in the corresponding
     meson.build.

   * ```webrtc/experiments/registered_field_trials.h``` is generated at build
     time upstream. Regenerate it with
     ```python3 webrtc/experiments/field_trials.py header --output webrtc/experiments/registered_field_trials.h```.

   * ```webrtc/third_party/pffft``` and ```webrtc/third_party/rnnoise``` come
     from the Chromium tree (```chromium/src/third_party```), not WebRTC.

   * Re-apply the patches in ```patches/``` and refresh them against the new
     code.

   * Unit tests (```*_unittest.cc```) and the test helpers they need are
     copied from upstream at their upstream paths as well, and listed in
     ```tests/meson.build```. Tests that read upstream test resources go in
     ```resource_unittest_sources```, and the ```.sha1``` files for the
     resources they use go in ```webrtc/resources/``` (copied from upstream's
     ```resources/```). Run ```meson test``` with ```-Dtests=enabled``` after
     updating.

4. Once everything has been copied and updated, everything needs to be built.
   Missing dependencies (files that were not copied, or new modules that are
   being depended on) will first turn up here.

   * Copy new deps as needed, leaving out testing-only dependencies insofar as
     this is possible.

5. ```webrtc/modules/audio_processing/include/audio_processing.h``` is the main
   include file, so look for API changes here.

   * The current policy is that we mirror upstream API as-is.

   * Update soversion in meson.build with the appropriate version info  based on how the
     code has changed. Details on how to do this are included in the
     [libtool documentation][libtool-version-info].

5. Build PulseAudio (and/or any other dependent projects) against the new code.
   The easy way to do this is via a prefixed install.

   * Configure webrtc-audio-processing with
     ```meson build -D prefix=$(pwd)/install```, then do a ```ninja -C build/ install```

   * Configure PulseAudio with
     ```meson build -D pkg_config_path=/path/to/webrtc-audio-processing/install/lib64/pkgconfig/```, which will cause the
     build to pick up the prefixed install. Then do a ```ninja -C build```, run the built
     PulseAudio, and load ```module-echo-cancel``` to make sure it loads fine.

   * Run some test streams through the canceller to make sure it is working
     fine.

[get-webrtc]: https://webrtc.googlesource.com/src/
[meld]: http://meldmerge.org/
[libtool-version-info]: https://www.gnu.org/software/libtool/manual/html_node/Updating-version-info.html
