#!/usr/bin/env python3
#
# Builds and packages webrtc-audio-processing for one release target.
#
# This is what the GitHub Actions workflows run, and it can also be used
# locally. The workflows only set up the toolchain (container, NDK, MSVC, ...)
# and then call this script.
#
#   ci/build.py native  --package NAME [--tests] [-D option=value ...]
#       Builds for the machine it runs on (Linux, macOS, Windows), optionally
#       runs the unit tests, and packages the installed tree as
#       dist/webrtc-audio-processing.NAME.tar.gz (.zip on Windows).
#
#   ci/build.py android [--api LEVEL] [--abi ABI ...]
#       Cross-builds shared libraries for Android with the NDK found in
#       $ANDROID_NDK_HOME, $ANDROID_NDK_LATEST_HOME or $ANDROID_NDK_ROOT, and
#       packages them as dist/webrtc-audio-processing.android.tar.gz.
#
#   ci/build.py ios [--min-version VERSION]
#       Cross-builds static libraries for iOS devices and the simulator, and
#       packages them as dist/WebRTCAudioProcessing.xcframework.zip.

import argparse
import glob
import os
import platform
import shutil
import subprocess
import sys
import tarfile
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACKAGE_PREFIX = 'webrtc-audio-processing'
LIB_NAME = 'webrtc-audio-processing-3'

# Options shared by all release builds. abseil-cpp is built as a subproject
# and linked statically, so the packages don't depend on a system abseil.
COMMON_MESON_OPTIONS = [
    '--buildtype=release',
    '--force-fallback-for=abseil-cpp',
    '--libdir=lib',
]

ANDROID_ABIS = {
    # ABI: (clang target triple, meson cpu_family, meson cpu, NEON)
    'arm64-v8a': ('aarch64-linux-android', 'aarch64', 'aarch64', True),
    'armeabi-v7a': ('armv7a-linux-androideabi', 'arm', 'armv7a', True),
    'x86_64': ('x86_64-linux-android', 'x86_64', 'x86_64', False),
}

IOS_SLICES = [
    # (name, SDK, arch)
    ('ios-arm64', 'iphoneos', 'arm64'),
    ('ios-arm64-simulator', 'iphonesimulator', 'arm64'),
    ('ios-x86_64-simulator', 'iphonesimulator', 'x86_64'),
]


def run(cmd, **kwargs):
    print('+', ' '.join(cmd), flush=True)
    subprocess.run(cmd, check=True, cwd=kwargs.pop('cwd', ROOT), **kwargs)


def clean_dir(path):
    shutil.rmtree(path, ignore_errors=True)
    os.makedirs(path)


def work_dir(*parts):
    return os.path.join(ROOT, 'ci-work', *parts)


def dist_dir():
    path = os.path.join(ROOT, 'dist')
    os.makedirs(path, exist_ok=True)
    return path


def add_licenses(dest, build_dir):
    """Copies the licenses of everything that ends up in the binaries."""
    licenses = os.path.join(dest, 'licenses')
    os.makedirs(licenses, exist_ok=True)
    files = {
        'webrtc-audio-processing.txt': os.path.join(ROOT, 'COPYING'),
        'webrtc-PATENTS.txt': os.path.join(ROOT, 'webrtc', 'PATENTS'),
        'pffft.txt': os.path.join(ROOT, 'webrtc', 'third_party', 'pffft',
                                  'LICENSE'),
        'rnnoise.txt': os.path.join(ROOT, 'webrtc', 'third_party', 'rnnoise',
                                    'COPYING'),
    }
    abseil = glob.glob(os.path.join(ROOT, 'subprojects', 'abseil-cpp-*',
                                    'LICENSE'))
    if abseil:
        files['abseil-cpp.txt'] = abseil[0]
    for name, src in files.items():
        shutil.copyfile(src, os.path.join(licenses, name))
    shutil.copyfile(os.path.join(ROOT, 'NEWS'), os.path.join(dest, 'NEWS'))


def archive(src_dir, name, fmt):
    """Packs the contents of src_dir into dist/NAME.FMT."""
    out = os.path.join(dist_dir(), name + '.' + fmt)
    if fmt == 'zip':
        with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
            for root, _, files in os.walk(src_dir):
                for f in files:
                    path = os.path.join(root, f)
                    z.write(path, os.path.relpath(path, src_dir))
    else:
        with tarfile.open(out, 'w:gz') as t:
            for entry in sorted(os.listdir(src_dir)):
                t.add(os.path.join(src_dir, entry), entry)
    print('Wrote', out)
    return out


def meson_options(defines):
    return ['-D' + d for d in defines]


def build_native(args):
    build = work_dir('build')
    install = work_dir('install')
    shutil.rmtree(build, ignore_errors=True)
    clean_dir(install)

    options = COMMON_MESON_OPTIONS + ['--prefix=' + install]
    if args.tests:
        options.append('-Dtests=enabled')
    run(['meson', 'setup', build] + options + meson_options(args.define))
    run(['meson', 'compile', '-C', build])
    if args.tests:
        run([sys.executable, os.path.join('tests', 'download_resources.py'),
             os.path.join(build, 'test-resources')])
        run(['meson', 'test', '-C', build, '--print-errorlogs'])
    run(['meson', 'install', '-C', build])

    add_licenses(install, build)
    fmt = 'zip' if platform.system() == 'Windows' else 'tar.gz'
    archive(install, PACKAGE_PREFIX + '.' + args.package, fmt)


def find_ndk():
    for var in ('ANDROID_NDK_HOME', 'ANDROID_NDK_LATEST_HOME',
                'ANDROID_NDK_ROOT'):
        path = os.environ.get(var)
        if path and os.path.isdir(path):
            return path
    sys.exit('Android NDK not found, set ANDROID_NDK_HOME')


def check_android_library(readelf, path):
    """Checks that libc++ is linked in and segments are 16 KB aligned."""
    dynamic = subprocess.run([readelf, '-d', path], check=True,
                             capture_output=True, text=True).stdout
    needed = [l.split('[')[-1].rstrip(']') for l in dynamic.splitlines()
              if '(NEEDED)' in l]
    print(os.path.basename(path), 'needs', ', '.join(needed))
    if any('c++' in n for n in needed):
        sys.exit('%s depends on a shared libc++' % path)
    segments = subprocess.run([readelf, '-lW', path], check=True,
                              capture_output=True, text=True).stdout
    for line in segments.splitlines():
        fields = line.split()
        if fields and fields[0] == 'LOAD' and int(fields[-1], 16) < 0x4000:
            sys.exit('%s has LOAD segments aligned below 16 KB' % path)


def build_android(args):
    ndk = find_ndk()
    host_tag = {'Linux': 'linux-x86_64', 'Darwin': 'darwin-x86_64'}[
        platform.system()]
    bindir = os.path.join(ndk, 'toolchains', 'llvm', 'prebuilt', host_tag,
                          'bin')
    package = work_dir('android-package')
    clean_dir(package)

    for abi in args.abi:
        triple, cpu_family, cpu, neon = ANDROID_ABIS[abi]
        build = work_dir('android-build-' + abi)
        install = work_dir('android-install-' + abi)
        shutil.rmtree(build, ignore_errors=True)
        clean_dir(install)

        clang = os.path.join(bindir, '%s%d-clang' % (triple, args.api))
        # Link libc++ statically so that the package is a single .so, and
        # align segments for devices with 16 KB pages.
        link_args = ['-Wl,-z,max-page-size=16384']
        cross_file = os.path.join(work_dir(), 'android-%s.ini' % abi)
        with open(cross_file, 'w') as f:
            f.write(f"""[binaries]
c = '{clang}'
cpp = '{clang}++'
ar = '{os.path.join(bindir, 'llvm-ar')}'
strip = '{os.path.join(bindir, 'llvm-strip')}'

[built-in options]
c_link_args = {link_args!r}
cpp_link_args = {link_args + ['-static-libstdc++']!r}

[host_machine]
system = 'android'
cpu_family = '{cpu_family}'
cpu = '{cpu}'
endian = 'little'
""")
        options = COMMON_MESON_OPTIONS + [
            '--prefix=' + install,
            '--cross-file=' + cross_file,
            '-Dneon=' + ('enabled' if neon else 'disabled'),
        ]
        run(['meson', 'setup', build] + options)
        run(['meson', 'compile', '-C', build])
        run(['meson', 'install', '-C', build, '--strip'])

        if not os.path.exists(os.path.join(package, 'include')):
            shutil.copytree(os.path.join(install, 'include'),
                            os.path.join(package, 'include'))
        libdir = os.path.join(package, 'lib', abi)
        os.makedirs(libdir)
        for so in glob.glob(os.path.join(install, 'lib', '*.so*')):
            shutil.copy(so, libdir)
            check_android_library(os.path.join(bindir, 'llvm-readelf'),
                                  os.path.join(libdir, os.path.basename(so)))

    add_licenses(package, None)
    archive(package, PACKAGE_PREFIX + '.android', 'tar.gz')


def build_ios(args):
    slices = {}
    for name, sdk, arch in IOS_SLICES:
        build = work_dir('ios-build-' + name)
        install = work_dir('ios-install-' + name)
        shutil.rmtree(build, ignore_errors=True)
        clean_dir(install)

        min_flag = ('-mios-simulator-version-min=' if sdk == 'iphonesimulator'
                    else '-miphoneos-version-min=') + args.min_version
        flags = ['-arch', arch, min_flag]
        cross_file = os.path.join(work_dir(), 'ios-%s.ini' % name)
        with open(cross_file, 'w') as f:
            f.write(f"""[binaries]
c = ['xcrun', '--sdk', '{sdk}', 'clang']
cpp = ['xcrun', '--sdk', '{sdk}', 'clang++']
objc = ['xcrun', '--sdk', '{sdk}', 'clang']
objcpp = ['xcrun', '--sdk', '{sdk}', 'clang++']
ar = ['xcrun', '--sdk', '{sdk}', 'ar']
strip = ['xcrun', '--sdk', '{sdk}', 'strip']

[built-in options]
c_args = {flags!r}
cpp_args = {flags!r}
c_link_args = {flags!r}
cpp_link_args = {flags!r}

[properties]
needs_exe_wrapper = true

[host_machine]
system = 'darwin'
subsystem = 'ios'
cpu_family = '{'aarch64' if arch == 'arm64' else arch}'
cpu = '{arch}'
endian = 'little'
""")
        options = COMMON_MESON_OPTIONS + [
            '--prefix=' + install,
            '--cross-file=' + cross_file,
            '-Ddefault_library=static',
            '-Dneon=' + ('enabled' if arch == 'arm64' else 'disabled'),
        ]
        run(['meson', 'setup', build] + options)
        run(['meson', 'compile', '-C', build])
        run(['meson', 'install', '-C', build])

        # Bundle abseil into the library, so that users only need to link one
        # static library.
        lib = os.path.join(work_dir(), 'libwebrtc-audio-processing-%s.a' %
                           name)
        absl_libs = sorted(glob.glob(os.path.join(
            build, 'subprojects', 'abseil-cpp-*', 'libabsl_*.a')))
        run(['libtool', '-static', '-no_warning_for_no_symbols', '-o', lib,
             os.path.join(install, 'lib', 'lib%s.a' % LIB_NAME)] + absl_libs)
        # Make sure abseil really ended up in the library.
        symbols = subprocess.run(['nm', '-gU', lib], check=True,
                                 capture_output=True, text=True).stdout
        if 'absl' not in symbols:
            sys.exit('abseil is missing from ' + lib)
        run(['lipo', '-info', lib])
        slices[name] = (lib, os.path.join(install, 'include'))

    # One xcframework library per platform: merge the simulator architectures.
    sim_lib = os.path.join(work_dir(), 'libwebrtc-audio-processing-sim.a')
    run(['lipo', '-create', slices['ios-arm64-simulator'][0],
         slices['ios-x86_64-simulator'][0], '-output', sim_lib])

    libs = [
        (slices['ios-arm64'][0], slices['ios-arm64'][1], 'device'),
        (sim_lib, slices['ios-arm64-simulator'][1], 'simulator'),
    ]
    xcf_args = []
    for lib, include, kind in libs:
        # xcodebuild names the library in the xcframework after the file.
        staged = os.path.join(work_dir('ios-' + kind), 'libwebrtc-audio-processing.a')
        clean_dir(os.path.dirname(staged))
        shutil.copyfile(lib, staged)
        xcf_args += ['-library', staged, '-headers', include]

    package = work_dir('ios-package')
    clean_dir(package)
    xcframework = os.path.join(package, 'WebRTCAudioProcessing.xcframework')
    run(['xcodebuild', '-create-xcframework'] + xcf_args +
        ['-output', xcframework])
    for entry in sorted(os.listdir(xcframework)):
        print(' ', entry, os.listdir(os.path.join(xcframework, entry))
              if os.path.isdir(os.path.join(xcframework, entry)) else '')
    add_licenses(package, None)
    archive(package, 'WebRTCAudioProcessing.xcframework', 'zip')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='target', required=True)

    native = sub.add_parser('native', help='build for this machine')
    native.add_argument('--package', required=True,
                        help='package name, e.g. ubuntu-24.04_x86_64')
    native.add_argument('--tests', action='store_true',
                        help='build and run the unit tests')
    native.add_argument('-D', dest='define', action='append', default=[],
                        metavar='OPTION=VALUE', help='extra meson option')

    android = sub.add_parser('android', help='cross-build for Android')
    android.add_argument('--api', type=int, default=24,
                         help='minimum Android API level (default: 24)')
    android.add_argument('--abi', action='append', choices=ANDROID_ABIS,
                         help='ABI to build (default: all)')

    ios = sub.add_parser('ios', help='cross-build an iOS xcframework')
    ios.add_argument('--min-version', default='14.0',
                     help='minimum iOS version (default: 14.0)')

    args = parser.parse_args()
    if args.target == 'native':
        build_native(args)
    elif args.target == 'android':
        args.abi = args.abi or list(ANDROID_ABIS)
        build_android(args)
    else:
        build_ios(args)


if __name__ == '__main__':
    main()
