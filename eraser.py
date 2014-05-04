#!/usr/bin/env python

"""
define PTRACE_TRACEME             0
define PTRACE_PEEKTEXT            1
define PTRACE_PEEKDATA            2
define PTRACE_PEEKUSR             3
define PTRACE_POKETEXT            4
define PTRACE_POKEUSR             6
define PTRACE_CONT                7
define PTRACE_KILL                8
"""

PTRACE_POKEDATA = 5
PTRACE_ATTACH = 16
PTRACE_DETACH = 17

import sys
import os
import ctypes
import re

c_ptrace = ctypes.CDLL("libc.so.6").ptrace
c_pid_t = ctypes.c_int32 # This assumes pid_t is int32_t
c_ptrace.argtypes = [ctypes.c_int, c_pid_t, ctypes.c_void_p, ctypes.c_void_p]

def pattach(pid):
	op = ctypes.c_int(PTRACE_ATTACH)
	c_pid = c_pid_t(pid)
	null = ctypes.c_void_p()
	err = c_ptrace(op, c_pid, null, null)
	if err != 0:
		print "ptrace: %s" % str(err)
		sys.exit(err)

def pdetach(pid):
	op = ctypes.c_int(PTRACE_DETACH)
	c_pid = c_pid_t(pid)
	null = ctypes.c_void_p()
	err = c_ptrace(op, c_pid, null, null)
	if err != 0:
		print "ptrace: %s" % str(err)
		sys.exit(err)

def pokeZero(pid,address):
	op = ctypes.c_int(PTRACE_POKEDATA)
	c_pid = c_pid_t(int(pid))
	err = c_ptrace(op, c_pid, address, 0x90909090)
	if err != 0:
		print "ptrace %s" % str(err)
		#sys.exit(err)

def maps_line_range(line):
	m = re.match(r'([0-9A-Fa-f]+)-([0-9A-Fa-f]+) ([-r])', line)
	return [int(m.group(1), 16), int(m.group(2), 16), m.group(3)]


def erase(pid):
	pattach(int(pid))
	maps_file = open("/proc/" + pid + "/maps", 'r')
	ranges = map(maps_line_range, maps_file.readlines())
	maps_file.close()	
	# we now have the ranges ...
	for r in ranges:
		if r[2] == "r":
			try:
				for i in xrange(r[0],r[1]):
					pokeZero(int(pid),i)	
			except OverflowError:
				pass
	pdetach(int(pid))

if __name__ == "__main__":
	for pid in sys.argv[1:]:
		erase(pid)   
