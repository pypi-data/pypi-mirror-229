#!/usr/bin/env -S  python  #
# -*- coding: utf-8 -*-

# $BEGIN_RECRUITMENTCURVEFITTING_LICENSE$
# 
# This file is part of the RecruitmentCurveFitting project, a Python
# package for fitting sigmoid and bell-shaped functions to EMG
# recruitment-curve measurements.
# 
# Copyright (c) 2023 Jeremy Hill
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program. If not, see http://www.gnu.org/licenses/ .
# 
# $END_RECRUITMENTCURVEFITTING_LICENSE$

"""
Use the RecruitmentCurveFitting module from the command-line
to fit both an M-wave and an H-reflex recruitment curve from
one or more text files.
"""

import os
import re
import ast
import sys
import glob
import argparse

def OneOrTwoNumbers( s ):
	seq = ast.literal_eval( s.strip( ' [](),' ) + ',' )
	try: x, = seq
	except: x = a, b = seq
	return x

class HelpFormatter( argparse.RawDescriptionHelpFormatter ): pass
#class HelpFormatter( argparse.RawDescriptionHelpFormatter, argparse.ArgumentDefaultsHelpFormatter ): pass
parser = argparse.ArgumentParser( description=__doc__, formatter_class=HelpFormatter, prog='python -m RecruitmentCurveFitting', )
parser.add_argument(       "filenames",         metavar='FILENAME',    nargs='*', help='one or more text files to load (use a dash to denote stdin)' )
parser.add_argument(       "--help-module",     action='store_true',   help='display the docstring for the main package (Python API)' )
parser.add_argument(       "--unpack-examples", action='store_true',   help='write example files to the current directory (do not overwrite) and quit' )
parser.add_argument( "-p", "--plot",            action='store_true',   help='whether to show figures on-screen' )
parser.add_argument( "-g", "--grid",            action='store_true',   help='whether to use a grid for the plots' )
parser.add_argument( "-x", "--xlabel",          metavar='XLABEL',      default='Stimulation Intensity (mA)', help='x-axis label text for the plots' )
parser.add_argument( "-y", "--ylabel",          metavar='YLABEL',      default='Response ($\\mu$V)', help='y-axis label text for the plots' )
parser.add_argument( "-t", "--title",           metavar='TITLE',       default=None, help='override automatically-generated plot titles' )
parser.add_argument(       "--xlim",            metavar='XMIN,XMAX',   default=None, type=OneOrTwoNumbers, help='x-axis limits for the plots' )
parser.add_argument(       "--ylim",            metavar='YMIN,YMAX',   default=None, type=OneOrTwoNumbers, help='y-axis limits for the plots' )
parser.add_argument(       "--mark-mmax",       action='store_true',   help='whether to mark M_max on plots' )
parser.add_argument(       "--mark-hmax",       action='store_true',   help='whether to mark H_max on plots' )
parser.add_argument(       "--threshold",       metavar='MTHRESHOLD',  default=0, type=float, help='unscaled proportion of Mmax (between 0 and 1) to mark as "threshold" for the M-wave curve (set to 0 to leave it unmarked)' )
parser.add_argument( "-s", "--saveas",          metavar='PDFFILENAME', default='', help='name of pdf file in which to save figures (one per page)' )
opts = parser.parse_args()

import numpy

import RecruitmentCurveFitting
from RecruitmentCurveFitting import *

if opts.unpack_examples:
	UnpackExamples()
	if not opts.filenames: raise SystemExit( 'done' )		

if opts.help_module:
	print( RecruitmentCurveFitting.__doc__ )
	raise SystemExit()

def tryeval(x):
	try: return ast.literal_eval( x )
	except: return x
	
filenames = opts.filenames if opts.filenames else [ '-' ]
def myglob( pattern ):
	hits = sorted( glob.glob( os.path.expanduser( pattern ) ) )
	return hits if hits else [ pattern ]
filenames = [ filename for pattern in filenames for filename in myglob( pattern ) ]
conditions = {}
collatedConditionTable = []
collatedDataTable = []
for filename in filenames:
	table = []
	headings = None
	with ( sys.stdin if filename == '-' else open( filename, 'rt' ) ) as fh:
		for line in fh:
			line = line.strip()
			if not line: continue
			if headings is None: line = line.lstrip( '# \t' ) # allow the headings line to start with a comment symbol
			line = re.sub( r'\s*#.*$', '', line ) # otherwise, remove comments entirely
			if not line: continue
			row = [ tryeval( x ) for x in re.sub( r'[\s,;\(\)\[\]\{\}:]+', ' ', line ).split() ]
			if headings is None:
				if all( isinstance( x, str ) for x in row ): headings = row; row = None
				else: headings = ''
			if row: table.append( row )
	lengths = list( { len( row ) for row in table } )
	if len( lengths ) == 0: raise SystemExit( 'no data in %s' % filename )
	if len( lengths ) != 1: raise SystemExit( 'unequal row lengths in %s' % filename )
	if not headings: headings = [ 'Column%d' % i for i in range( len( table[ 0 ] ) ) ]
	conditionTable = [ tuple( zip( headings[ :-3 ], row[ :-3 ] ) ) for row in table ]
	if len( filenames ) > 1:
		conditionTable = [ ( ( 'File', filename ), ) + row for row in conditionTable ]
	dataTable = numpy.array( [ row[ -3: ] for row in table ], dtype=float )
	collatedConditionTable += conditionTable
	collatedDataTable.append( dataTable )
	
conditionIndex = numpy.array( [ conditions.setdefault( conditionRow, len( conditions ) + 1 ) for conditionRow in collatedConditionTable ] )
conditions = { v : dict( k ) for k, v in conditions.items() }
collatedDataTable = numpy.concatenate( collatedDataTable, axis=0 )
stim       = collatedDataTable[ :, -3 ]
mResponse  = collatedDataTable[ :, -2 ]
hResponse  = collatedDataTable[ :, -1 ]
if opts.plot and 'IPython' in sys.modules: import matplotlib; matplotlib.interactive( True )

print( '[' )
for eachCondition, conditionDict in conditions.items():
	selected = conditionIndex == eachCondition
	m = Sigmoid(   stim[ selected ], mResponse[ selected ], **conditionDict )
	h = HillCurve( stim[ selected ], hResponse[ selected ], **conditionDict ) # TODO: add option for ModifiedBrinkworth
	mMax = m.uHeight.finalValue
	mThresholdStim = m.Backward( opts.threshold, scaled=False ) if opts.threshold is not None and 0 < opts.threshold < 1 else None
	hMaxStim, hMax = h.Find( 'max' )
	conditionDict.update( {
		'Mmax' : mMax,
		'MthresholdUnscaled' : opts.threshold,
		'MthresholdStim' : mThresholdStim,
		'Hmax' : hMax,
		'HmaxStim' : hMaxStim,
	} )
	conditionDict.update( { 'M_' + k : v for k, v in m.ResolveParameters( asDict=True ).items() } )
	conditionDict.update( { 'H_' + k : v for k, v in h.ResolveParameters( asDict=True ).items() } )
	print( '%r,\n' % conditionDict )
	if opts.plot or opts.saveas:
		if opts.title is None: opts.title = '@DEFAULT@'
		else: opts.title = ast.literal_eval( '"""' + opts.title + '"""' )
		m.Plot( axes=eachCondition, markX=mThresholdStim, markY=mMax if opts.mark_mmax else None, xlim=opts.xlim )
		h.Plot( axes=eachCondition, markX='max' if opts.mark_hmax else None, markY='max' if opts.mark_hmax else None, hold=True, title=opts.title, grid=opts.grid, xlabel=opts.xlabel, ylabel=opts.ylabel, xlim=opts.xlim, ylim=opts.ylim )
print( ']' )
if opts.saveas:
	opts.saveas = os.path.realpath( os.path.expanduser( opts.saveas ) )
	print( '# saving %d figure%s to %s' % ( len( conditions ), '' if len( conditions ) == 1 else 's',  opts.saveas ) )
	SavePDF( opts.saveas, figures=conditions )
if opts.plot and 'IPython' not in sys.modules: import matplotlib; matplotlib.pyplot.show()
