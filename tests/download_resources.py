#!/usr/bin/env python3
#
# Downloads the upstream WebRTC test resources used by the unit tests.
#
# Upstream keeps these files in Google Cloud Storage, and only checks in a
# `<name>.sha1` file next to where each resource should go (see the
# download_from_google_storage hook in upstream's DEPS). This script does the
# same for the .sha1 files in webrtc/resources/.
#
# Usage: download_resources.py [OUTPUT_DIR]
#
# OUTPUT_DIR defaults to ./test-resources. Point the tests at it with
# -Dtest-resources-dir=OUTPUT_DIR, or run the download into
# <builddir>/test-resources, which is the default location.

import hashlib
import os
import sys
import urllib.request

BUCKET_URL = 'https://storage.googleapis.com/chromium-webrtc-resources/'
SRC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..',
                       'webrtc', 'resources')


def sha1_of(path):
    h = hashlib.sha1()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    out_dir = os.path.abspath(sys.argv[1] if len(sys.argv) > 1
                              else 'test-resources')
    stamp = os.path.join(out_dir, '.complete')
    if os.path.exists(stamp):
        os.remove(stamp)

    for root, _, files in os.walk(SRC_DIR):
        for name in sorted(files):
            if not name.endswith('.sha1'):
                continue
            with open(os.path.join(root, name)) as f:
                digest = f.read().strip()
            rel = os.path.relpath(os.path.join(root, name[:-len('.sha1')]),
                                  SRC_DIR)
            dest = os.path.join(out_dir, rel)
            if os.path.exists(dest) and sha1_of(dest) == digest:
                continue
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            print('Downloading', rel)
            tmp = dest + '.part'
            urllib.request.urlretrieve(BUCKET_URL + digest, tmp)
            actual = sha1_of(tmp)
            if actual != digest:
                os.remove(tmp)
                sys.exit('SHA-1 mismatch for %s: expected %s, got %s' %
                         (rel, digest, actual))
            os.replace(tmp, dest)

    # Lets the test binary know that the resources are all there.
    with open(stamp, 'w'):
        pass
    print('Test resources are in', out_dir)


if __name__ == '__main__':
    main()
