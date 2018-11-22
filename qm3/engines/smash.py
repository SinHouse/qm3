# -*- coding: iso-8859-1 -*-

from __future__ import print_function, division
import	sys
if( sys.version_info[0] == 2 ):
	range = xrange
import	os
import	qm3.utils
import	qm3.engines



class smash( qm3.engines.qmbase ):

	def __init__( self, mol, ini, sele, nbnd = [], link = [] ):
		qm3.engines.qmbase.__init__( self, mol, sele, nbnd, link )
		self.ini = ini
		self.exe = "mpirun -n 2 /Users/smarti/Devel/smash/2.2.0/smash_mpi < smash.inp > smash.out"


	def mk_input( self, mol, run ):
		f = open( "smash.inp", "wt" )
		k = "runtype=energy"
		if( run != "ener" ):
			k = "runtype=gradient"
		f.write( self.ini % ( k ) )
		f.write( "\ngeom\n" )
		j = 0
		for i in self.sel:
			i3 = i * 3
			f.write( "%2s%20.10lf%20.10lf%20.10lf\n"%( self.smb[j], 
				mol.coor[i3]   - mol.boxl[0] * round( mol.coor[i3]   / mol.boxl[0], 0 ), 
				mol.coor[i3+1] - mol.boxl[1] * round( mol.coor[i3+1] / mol.boxl[1], 0 ),
				mol.coor[i3+2] - mol.boxl[2] * round( mol.coor[i3+2] / mol.boxl[2], 0 ) ) )
			j += 1
		if( self.lnk ):
			self.vla = []
			k = len( self.sel )
			for i,j in self.lnk:
				c, v = qm3.utils.LA_coordinates( i, j, mol )
				f.write( "%-2s%20.10lf%20.10lf%20.10lf\n"%( "H", c[0], c[1], c[2] ) )
				self.vla.append( ( self.sel.index( i ), k, v[:] ) )
				k += 1
		if( self.nbn ):
			for i in self.nbn:
				i3 = i * 3
				f.write( "X %20.10lf%20.10lf%20.10lf\n"%( 
					mol.coor[i3]   - mol.boxl[0] * round( mol.coor[i3] / mol.boxl[0], 0 ), 
					mol.coor[i3+1] - mol.boxl[1] * round( mol.coor[i3+1] / mol.boxl[1], 0 ),
					mol.coor[i3+2] - mol.boxl[2] * round( mol.coor[i3+2] / mol.boxl[2], 0 ) ) )
			f.write( "\ncharge\n" )
			k = len( self.sel ) + len( self.lnk ) + 1
			for i in self.nbn:
				f.write( "%-6d%8.3lf\n"%( k, mol.chrg[i] ) )
				k += 1
		f.close()


	def parse_log( self, mol, run ):
		f = open( "smash.out", "rt" )
		l = f.readline()
		e = 0.0
		g_qm = []
		g_mm = []
		while( l != "" ):
			if( l.find( "Energy =" ) > 0 ):
				e = float( l.strip().split()[-2] ) * self._ce
			if( l.find( "Gradient (Hartree/Bohr)" ) > 0 ):
				f.readline(); f.readline()
				for i in range( len( self.sel ) + len( self.lnk ) ):
					g_qm += [ float( i ) * self._cg for i in f.readline().strip().split()[1:] ]
				for i in range( len( self.nbn ) ):
					g_mm += [ float( i ) * self._cg for i in f.readline().strip().split()[1:] ]
			if( l.find( "Mulliken Population Analysis" ) > 0 ):
				f.readline(); f.readline()
				for i in self.sel:
					mol.chrg[i] = float( f.readline().strip().split()[-1] )
			l = f.readline()
		f.close()
		mol.func += e
		if( run == "grad" ):
			qm3.utils.LA_gradient( self.vla, g_qm )
			for i in range( len( self.sel ) ):
				i3 = i * 3
				for j in [0, 1, 2]:
					mol.grad[3*self.sel[i]+j] += g_qm[i3+j]
			if( self.nbn ):
				k = 0
				for i in range( len( self.nbn ) ):
					for j in [0, 1, 2]:
						mol.grad[3*self.nbn[i]+j] += g_mm[k*3+j]
					k += 1