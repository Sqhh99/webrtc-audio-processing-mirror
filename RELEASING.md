# Release process

## Update the code

Follow the instructions in `UPDATING.md` to update the code.

## Update the package version

If there is no API breakage, update the minor version (X.y -> X.y+1). If there
is API breakage, update the major version (X.y -> X+1.0).

## Make sure builds are successful on all platforms

There is CI for `x86_64` and `aarch64` builds, but 32-bit ARM and MIPS builds
need manual verfification (or testing downstream).

## Tag the release

Releases are tagged after the upstream WebRTC version they are based on, as
`m<milestone>.<branch>.<branch position>.<build>`:

  * `milestone`: the Chromium/WebRTC milestone (e.g. `153`)
  * `branch`: the WebRTC `branch-heads/<branch>` number, i.e. the third
    component of the Chromium version (e.g. `8010` for `153.0.8010.55`)
  * `branch position`: the number of commits on that branch head the code is
    synced to (`0` for the branch point)
  * `build`: our own release number for that upstream revision, starting at
    `0` and incremented for releases that only change things on our side

For example, for the first release based on the M153 branch point:

```sh
git tag -s -m 'WebRTC AudioProcessing m153.8010.0.0' m153.8010.0.0
```

Pushing the tag triggers the release workflow, which builds binaries for all
platforms and publishes a GitHub release. It can also be started by hand from
the Actions tab (the "Release" workflow takes the tag name as input).

## Release packages

The release workflow runs the build workflow (`.github/workflows/build.yml`),
whose jobs only set up the toolchains and call `ci/build.py` for each target:

  * `ci/build.py native --package NAME [--tests]` builds on the current
    machine (the Linux packages are built inside the respective distribution
    containers), runs the tests, and packages the installed tree
  * `ci/build.py android` cross-builds for all Android ABIs with the NDK
  * `ci/build.py ios` cross-builds an iOS xcframework

The packages end up in `dist/`, and the same script can be used to reproduce a
release build locally.

## Make a tarball

```sh
# The output will be in build/meson-dist/
meson dist -C build --formats=gztar,xztar --include-subprojects
```

## Do a test build

```sh
tar xvf webrtc-audio-processing-X.y.tar.xz
cd webrtc-audio-processing-X.y
meson . build -Dprefix=$PWD/install
ninja -C build
ninja -C build install
cd ..
```

## Publish the files

```sh
scp webrtc-audio-processing-*.tar.* \
  annarchy.freedesktop.org:/srv/www.freedesktop.org/www/software/pulseaudio/webrtc-audio-processing/
```

## Push the tag

```sh
git push origin master
git push origin vX.y
```

## Update the website

This is currently an embarrassing manual process.

## Send out a release announcement

This goes to the `pulseaudio-discuss` and `gstreamer-devel` mailing lists, and
possibly `discuss-webrtc` if it seems relevant.
