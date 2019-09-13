import unittest
import hecate
from adcommon.creds import kinit_for_gssapi
from samba.credentials import Credentials, MUST_USE_KERBEROS
from getpass import getpass
from subprocess import Popen, PIPE
import re, six
from time import sleep
import random, string

def randomName(length=10):
    return ''.join(random.choice(string.ascii_lowercase) for i in range(length)).title()

class AdminToolsTestCase(unittest.TestCase):
    def assertSeen(self, what, msg=None, timeout=10):
        try:
            self.at.await_text(what, timeout=timeout)
        except hecate.hecate.Timeout:
            pass
        self.assertIn(what, self.at.screenshot(), msg)

    def assertNotSeen(self, what, msg=None, timeout=10):
        sleep(.5)
        slept = 0
        while slept < timeout:
            slept += .1
            if what not in self.at.screenshot():
                break
            sleep(.1)
        self.assertNotIn(what, self.at.screenshot(), msg)

    def press(self, msg):
        self.at.press(msg)
        sleep(.1)

    def __validate_kinit(self):
        return Popen(['klist', '-s'], stdout=PIPE, stderr=PIPE).wait() == 0

    def __validate_kinit(self):
        out, _ = Popen(['klist'], stdout=PIPE, stderr=PIPE).communicate()
        m = re.findall(six.b('Default principal:\s*(\w+)@([\w\.]+)'), out)
        if len(m) == 0:
            return False
        user, realm = m[0]
        self.creds.set_username(user.decode())
        self.creds.set_domain(realm.decode())
        with Popen(['klist', '-s'], stdout=PIPE, stderr=PIPE) as p:
            if p.wait() != 0:
                return False
        self.creds.set_kerberos_state(MUST_USE_KERBEROS)
        return True

    def kinit(self):
        while not self.__validate_kinit():
            print('Domain administrator credentials are required to run the test.')
            upn = '%s@%s' % (self.creds.get_username(), self.creds.get_domain()) if self.creds.get_username() and self.creds.get_domain() else None
            username = input('Domain user principal name%s: ' % (' (%s)' % upn if upn else ''))
            if username:
                self.creds.set_username(username)
            else:
                self.creds.set_username(upn)
            self.creds.set_password(getpass('Password for %s: ' % self.creds.get_username()))
            kinit_for_gssapi(self.creds, None)

    def setUp(self):
        self.creds = Credentials()
        self.kinit()
        self.at = hecate.Runner("admin-tools", width=120, height=50)

    def tearDown(self):
        self.at.shutdown()
