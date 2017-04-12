#pylint: skip-file
import unittest
import selinux
import sys
from Atomic import util
from Atomic.backends._docker import DockerBackend
import time

no_mock = True
try:
    from unittest.mock import MagicMock, patch
    no_mock = False
except ImportError:
    try:
        from mock import MagicMock, patch
        no_mock = False
    except ImportError:
        # Mock is already set to False
        pass

def _new_enough():
    py_version = sys.version_info
    if (py_version.major, py_version.minor, py_version.micro) >= (2, 7, 6):
        return True
    return False

new_enough = _new_enough()

if no_mock:
    # If there is no mock, we need need to create a fake
    # patch decorator
    def fake_patch(a, new=''):
        def foo(func):
            def wrapper(*args, **kwargs):
                ret = func(*args, **kwargs)
                return ret
            return wrapper
        return foo

    patch = fake_patch


class TestAtomicUtil(unittest.TestCase):

    def test_image_by_name(self):
        matches = util.image_by_name('atomic-test-1')
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]['Labels']['Name'],
                         'atomic-test-1')

    def test_image_by_name_glob(self):
        matches = util.image_by_name('atomic-test-*')
        self.assertTrue(len(matches) > 2)
        self.assertTrue(all([m['Labels']['Name'].startswith('atomic-test-')
                             for m in matches]))

    def test_image_by_name_registry_match(self):
        matches = util.image_by_name('/centos:latest')
        self.assertTrue(len(matches) == 1)

    def test_image_by_name_no_match(self):
        matches = util.image_by_name('this is not a real image name')
        self.assertTrue(len(matches) == 0)

    def test_default_container_context(self):
        default = util.default_container_context()
        if selinux.is_selinux_enabled():
            # newer policies use container_file_t
            self.assertTrue(default in
                            ['system_u:object_r:container_file_t:s0',
                             'system_u:object_r:svirt_sandbox_file_t:s0'])
        else:
            self.assertEqual(default, '')

    def test_check_call(self):
        exception_raised = False
        try:
            util.check_call(['/usr/bin/does_not_exist'])
        except util.FileNotFound:
            exception_raised = True
        self.assertTrue(exception_raised)

    def test_call(self):
        exception_raised = False
        try:
            util.call(['/usr/bin/does_not_exist'])
        except util.FileNotFound:
            exception_raised = True
        self.assertTrue(exception_raised)

    def test_check_output(self):
        exception_raised = False
        try:
            util.check_call(['/usr/bin/does_not_exist'])
        except util.FileNotFound:
            exception_raised = True
        self.assertTrue(exception_raised)

    def test_decompose(self):
        images = [('docker.io/library/busybox', ('docker.io', 'library','busybox', 'latest', '')),
                  ('docker.io/library/foobar/busybox', ('docker.io', 'library/foobar', 'busybox', 'latest', '')),
                  ('docker.io/library/foobar/busybox:2.1', ('docker.io', 'library/foobar', 'busybox', '2.1', '')),
                  ('docker.io/busybox:2.1', ('docker.io', 'library', 'busybox', '2.1', '')),
                  ('docker.io/busybox', ('docker.io', 'library', 'busybox', 'latest', '')),
                  ('busybox', ('', '', 'busybox', 'latest', '')),
                  ('busybox:2.1', ('', '', 'busybox', '2.1', '')),
                  ('library/busybox', ('', 'library', 'busybox', 'latest', '')),
                  ('library/busybox:2.1', ('', 'library', 'busybox', '2.1', '')),
                  ('registry.access.redhat.com/rhel7:latest', ('registry.access.redhat.com', '', 'rhel7', 'latest', '')),
                  ('registry.access.redhat.com/rhel7', ('registry.access.redhat.com', '', 'rhel7', 'latest', '')),
                  ('fedora@sha256:64a02df6aac27d1200c2572fe4b9949f1970d05f74d367ce4af994ba5dc3669e', ('', '', 'fedora', '', 'sha256:64a02df6aac27d1200c2572fe4b9949f1970d05f74d367ce4af994ba5dc3669e')),
                  ('docker.io/library/fedora@sha256:64a02df6aac27d1200c2572fe4b9949f1970d05f74d367ce4af994ba5dc3669e', ('docker.io', 'library', 'fedora', '', 'sha256:64a02df6aac27d1200c2572fe4b9949f1970d05f74d367ce4af994ba5dc3669e')),
                  ('docker.io/fedora@sha256:64a02df6aac27d1200c2572fe4b9949f1970d05f74d367ce4af994ba5dc3669e', ('docker.io', 'library', 'fedora', '', 'sha256:64a02df6aac27d1200c2572fe4b9949f1970d05f74d367ce4af994ba5dc3669e'))
                  ]

        for image in images:
            self.assertEqual(util.Decompose(image[0]).all, image[1])

    @unittest.skipUnless(new_enough, "Requires 2.7.6 or newer")
    def test_valid_uri(self):
        valid_uris = ['example.com', 'example.com:5000', 'example.US.com', 'example.com/image/name:version1', 'example.com:5000/foo/bar/image:tag', 'example_inc.com']
        invalid_uris = ['example.com/Image/name', 'example.com/image(name):latest', 'example.com/foo_bar', 'example[us].com', 'example.com#foo/bar']
        for uri in valid_uris:
            self.assertTrue(util.is_valid_image_uri(uri))

        for uri in invalid_uris:
            exception_raised = False
            try:
                util.is_valid_image_uri(uri)
            except ValueError:
                exception_raised = True
            self.assertTrue(exception_raised)


class MockIO(object):
    original_data = {"install_test": {"install_date": "2017-03-22 17:19:41", "id": "49779293ca711789a77bbdc35547a6b9ecb193a51b4e360fea95c4d206605d18"}}
    new_data_fq = {"install_date": "2017-04-22 17:19:41","id": "16e9fdecc1febc87fb1ca09271009cf5f28eb8d4aec5515922ef298c145a6726"}
    new_data_name= {"install_date": "2017-04-22 17:19:41","id": "16e9fdecc1febc87fb1ca09271009cf5f28eb8d4aec5515922ef298c145a6726"}
    install_data = original_data

    @classmethod
    def read_mock(cls):
        return cls.install_data

    @classmethod
    def write_mock(cls, val):
        cls.install_data = val

    @classmethod
    def reset_data(cls):
        cls.install_data = {}
        cls.install_data = cls.original_data

    @classmethod
    def grow_data(cls, var_name, name):
        cls.install_data[name] = getattr(cls, var_name)

if __name__ == '__main__':
    unittest.main()
