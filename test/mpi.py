#
# Copyright 2012-2016 Ghent University
#
# This file is part of vsc-mympirun,
# originally created by the HPC team of Ghent University (http://ugent.be/hpc/en),
# with support of Ghent University (http://ugent.be/hpc),
# the Flemish Supercomputer Centre (VSC) (https://www.vscentrum.be),
# the Flemish Research Foundation (FWO) (http://www.fwo.be/en)
# and the Department of Economy, Science and Innovation (EWI) (http://www.ewi-vlaanderen.be/en).
#
# https://github.com/hpcugent/vsc-mympirun
#
# vsc-mympirun is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation v2.
#
# vsc-mympirun is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with vsc-mympirun.  If not, see <http://www.gnu.org/licenses/>.
#
"""
Tests for the vsc.utils.missing module.

@author: Jens Timmerman (Ghent University)
"""
import os
import stat
import unittest
from random import choice
from string import ascii_uppercase

from vsc.utils.fancylogger import getLogger
from vsc.utils.run import run_simple
from vsc.mympirun.rm.factory import getinstance
import vsc.mympirun.mpi.mpi as mpim
import vsc.mympirun.mpi.intelmpi as intelmpi
import vsc.mympirun.mpi.openmpi as openmpi
import vsc.mympirun.mpi.mpich as mpich
from vsc.mympirun.rm.local import Local
from vsc.mympirun.option import MympirunOption

# we wish to use the mpirun we ship
os.environ["PATH"] = os.path.dirname(os.path.realpath(__file__)) + os.pathsep + os.environ["PATH"]

_testlogger = getLogger()

class TestMPI(unittest.TestCase):

    #######################
    ## general functions ##
    #######################

    def test_whatMPI(self):
        scriptnames = ["ompirun", "mpirun", "impirun", "mympirun"]
        for scriptname in scriptnames:
            # if the scriptname is an executable located on this machine
            if mpim.which(scriptname):
                (returned_scriptname, mpi, found) = mpim.whatMPI(scriptname)
                _testlogger.debug("%s, %s, %s", returned_scriptname, mpi, found)
                # if an mpi implementation was found
                if mpi:
                    self.assertTrue(mpi in found)
                    self.assertTrue(returned_scriptname == scriptname)
                else:
                    self.assertEqual(returned_scriptname, "mpirun", "")

    def test_stripfake(self):
        """Test if stripfake actually removes the /bin/fake path in $PATH"""
        _testlogger.debug("old path: %s", os.environ["PATH"])
        mpim.stripfake()
        newpath = os.environ["PATH"]
        self.assertFalse(("bin/%s" % mpim.FAKE_SUBDIRECTORY_NAME) in newpath)

    def test_which(self):
        scriptnames = ["ompirun", "mpirun", "impirun", "mympirun"]
        for scriptname in scriptnames:
            mpimwhich = mpim.which(scriptname) +"\n"
            ec, unixwhich = run_simple("which " + scriptname)
            self.assertEqual(mpimwhich, unixwhich, msg=("the return values of unix which and which() aren't the same: "
                "%s != %s") % (mpimwhich, unixwhich))

    ###################
    ## MPI functions ##
    ###################

    def test_options(self):
        """Bad options"""
        m = MympirunOption()
        m.args = ['echo', 'foo']
        # should not throw an error
        try:
            mpi_instance = getinstance(mpim.MPI, Local, m)
            mpi_instance.main()
        except Exception:
            self.fail("mympirun raised an exception")

        optdict = mpi_instance.options

        # why isnt this a dict??
        _testlogger.debug("MPI INSTANCE OPTIONS: %s, type %s", optdict, type(optdict))

        # for opt in m.args:
        #    self.assertFalse(opt in mpi_instance.options)
        _testlogger.debug("11 HALLO")

    def test_is_mpirun_for(self):
        _testlogger.debug("21 HALLO %s" , "HALLO")
        m = MympirunOption()
        _testlogger.debug("22 HALLO")
        ompi_instance = getinstance(openmpi.OpenMPI, Local, m)
        _testlogger.debug("23 HALLO")
        asdf = ompi_instance._mpiscriptname_for[0]
        _testlogger.debug("IS MPIRUN FOR ASDf %s:", asdf)
        path = mpim.which(asdf)
        _testlogger.debug("IS MPIRUN FOR PATH %s:", path)
        res = ompi_instance._is_mpirun_for(path)
        _testlogger.debug("IS MPIRUN FOR RES %s:", res)

    def test_set_omp_threads(self):
        _testlogger.debug("31 HALLO")
        m = MympirunOption()
        _testlogger.debug("32 HALLO")
        mpi_instance = getinstance(mpim.MPI, Local, m)
        _testlogger.debug("33 HALLO")
        mpi_instance.set_omp_threads()
        _testlogger.debug("34 HALLO")
        self.assertTrue(getattr(mpi_instance.options, 'ompthreads', None) is not None)
        self.assertEqual(os.environ["OMP_NUM_THREADS"],getattr(mpi_instance.options, 'ompthreads', None))

#    def test_is_mpirun_for(self):
#        m = MympirunOption()
#        mpi_instance = getinstance(mpim.MPI, Local, m)
#        mpi_instance.set_netmask()

    def test_MPI_local(self):
        """Test the MPI class with the local scheduler"""
        # options
        m = MympirunOption()
        mpi_instance = getinstance(mpim.MPI, Local, m)
        mpi_instance.main()

        # check for correct .mpd.conf file
        mpdconffn = os.path.expanduser('~/.mpd.conf')
        perms = stat.S_IMODE(os.stat(mpdconffn).st_mode)
        self.assertEqual(perms, 0400, msg='permissions %0o for mpd.conf %s' % (perms, mpdconffn))
