# -*- coding: iso-8859-1 -*-

from __future__ import print_function, division
import sys
if( sys.version_info[0] == 2 ):
    range = xrange
import math
import qm3.fio
import qm3.maths.matrix


#
# J. Comput. Chem. v35, p1672 (2014) [10.1002/jcc.23673]
# J. Phys. Chem. A v121, p9764 (2017) [10.1021/acs.jpca.7b10842]
# WIREs Comput. Mol. Sci. v8 (2018) [10.1002/wcms.1329]
#


class colvar_s( object ):

    def __init__( self, kumb, xref, conf, str_crd, str_met, molec ):
        """
------------------------------------------------------------------------
ncrd      nwin
dist      atom_i    atom_j
...
dist      atom_i    atom_j
------------------------------------------------------------------------
"""
        self.xref = xref
        self.kumb = kumb
        f = qm3.fio.open_r( conf )
        t = f.readline().strip().split()
        self.ncrd = int( t[0] )
        self.nwin = int( t[1] )
        self.jidx = {}
        self.func = []
        self.atom = []
        for i in range( self.ncrd ):
            t = f.readline().strip().split()
            if( t[0][0:4] == "dist" and len( t ) == 3 ):
                self.func.append( self.distance )
                a_i = int( t[1] )
                a_j = int( t[2] )
                self.atom.append( ( a_i, a_j ) )
                self.jidx[a_i] = True
                self.jidx[a_j] = True
        qm3.fio.close( f, conf )
        self.jidx = { jj: ii for ii,jj in zip( range( len( self.jidx ) ), sorted( self.jidx ) ) }
        self.idxj = { self.jidx[ii]: ii for ii in iter( self.jidx ) }
        self.jcol = 3 * len( self.jidx )
## -- constant metrics...
##        self.mass = []
##        for i in range( len( self.jidx ) ):
##            for j in [0, 1, 2]:
##                self.mass.append( 1.0 / molec.mass[self.idxj[i]] )
## ------------------------------------------------------------------
        # load (previous) equi-destributed string
        f = qm3.fio.open_r( str_crd )
        self.rcrd = [ float( i ) for i in f.read().split() ]
        qm3.fio.close( f, conf )
        # load (previous) string metrics
        f = qm3.fio.open_r( str_met )
        self.rmet = [ float( i ) for i in f.read().split() ]
        qm3.fio.close( f, conf )
        nc2 = self.ncrd * self.ncrd
        # get the arc length of the current string...
        arc = []
        for i in range( 1, self.nwin ):
            tmp = [ self.rcrd[i*self.ncrd+j] - self.rcrd[(i-1)*self.ncrd+j] for j in range( self.ncrd ) ]
            mat = qm3.maths.matrix.inverse( [ 0.5 * ( self.rmet[i*nc2+j] + self.rmet[(i-1)*nc2+j] ) for j in range( nc2 ) ], self.ncrd, self.ncrd )
            mat = qm3.maths.matrix.mult( mat, self.ncrd, self.ncrd, tmp, self.ncrd, 1 )
            arc.append( math.sqrt( sum( [ tmp[j] * mat[j] for j in range( self.ncrd ) ] ) ) )
        self.delz = sum( arc ) / float( self.nwin - 1.0 )
        print( "Colective variable s range: [%.3lf, %.3lf]"%( 0.0, sum( arc ) ) )
        # store inverse metrics from references...
        tmp = []
        for i in range( self.nwin ):
            tmp += qm3.maths.matrix.inverse( self.rmet[i*nc2:(i+1)*nc2], self.ncrd, self.ncrd )
        self.rmet = tmp[:]


    def get_func( self, molec ):
        ccrd = []
        jaco = [ 0.0 for i in range( self.ncrd * self.jcol ) ]
        for i in range( self.ncrd ):
            ccrd.append( self.func[i]( i, molec, jaco ) )
## -- constant metrics...
##        cmet = [ 0.0 for i in range( self.ncrd * self.ncrd ) ]
##        for i in range( self.ncrd ):
##            for j in range( i, self.ncrd ):
##                cmet[i*self.ncrd+j] = sum( [ jaco[i*self.jcol+k] * self.mass[k] * jaco[j*self.jcol+k] for k in range( self.jcol ) ] )
##                cmet[j*self.ncrd+i] = cmet[i*self.ncrd+j]
## ------------------------------------------------------------------
        nc2  = self.ncrd * self.ncrd
        cdst = []
        for i in range( self.nwin ):
            vec = [ ccrd[j] - self.rcrd[i*self.ncrd+j] for j in range( self.ncrd ) ]
## -- constant metrics...
##            mat = qm3.maths.matrix.inverse( [ 0.5 * ( cmet[j] + self.rmet[i*nc2+j] ) for j in range( nc2 ) ], self.ncrd, self.ncrd )
##            mat = qm3.maths.matrix.mult( mat, self.ncrd, self.ncrd, vec, self.ncrd, 1 )
## ------------------------------------------------------------------
            mat = qm3.maths.matrix.mult( self.rmet[i*nc2:(i+1)*nc2], self.ncrd, self.ncrd, vec, self.ncrd, 1 )
            cdst.append( math.sqrt( sum( [ vec[j] * mat[j] for j in range( self.ncrd ) ] ) ) )
        cexp = [ math.exp( - cdst[i] / self.delz ) for i in range( self.nwin ) ]
        cval = sum( [ i * self.delz * cexp[i] for i in range( self.nwin ) ] ) / sum( cexp )
        molec.func += 0.5 * self.kumb * math.pow( cval - self.xref, 2.0 )
        return( cval )


    def get_grad( self, molec ):
        ccrd = []
        jaco = [ 0.0 for i in range( self.ncrd * self.jcol ) ]
        for i in range( self.ncrd ):
            ccrd.append( self.func[i]( i, molec, jaco ) )
        nc2  = self.ncrd * self.ncrd
        cdst = []
        jder = []
        for i in range( self.nwin ):
            vec = [ ccrd[j] - self.rcrd[i*self.ncrd+j] for j in range( self.ncrd ) ]
            mat = qm3.maths.matrix.mult( self.rmet[i*nc2:(i+1)*nc2], self.ncrd, self.ncrd, vec, self.ncrd, 1 )
            cdst.append( math.sqrt( sum( [ vec[j] * mat[j] for j in range( self.ncrd ) ] ) ) )
            sd1 = qm3.maths.matrix.mult( mat, 1, self.ncrd, jaco, self.ncrd, self.jcol )
            sd2 = qm3.maths.matrix.mult( self.rmet[i*nc2:(i+1)*nc2], self.ncrd, self.ncrd, jaco, self.ncrd, self.jcol )
            sd3 = qm3.maths.matrix.mult( vec, 1, self.ncrd, sd2, self.ncrd, self.jcol )
            jder.append( [ 0.5 * ( sd1[j] + sd3[j] ) / cdst[-1] for j in range( self.jcol ) ] )
        cexp = [ math.exp( - cdst[i] / self.delz ) for i in range( self.nwin ) ]
        sumn = sum( [ i * self.delz * cexp[i] for i in range( self.nwin ) ] )
        sumd = sum( cexp )
        cval = sumn / sumd
        diff = self.kumb * ( cval - self.xref )
        molec.func += 0.5 * diff * ( cval - self.xref )
        sder = [ 0.0 for i in range( self.jcol ) ]
        for i in range( self.jcol ):
            for j in range( self.nwin ):
                sder[i] += diff * jder[j][i] * ( cval / self.delz - j ) * cexp[j] / sumd
        for i in range( len( self.jidx ) ):
            i3 = i * 3
            for j in [0, 1, 2]:
                molec.grad[3*self.idxj[i]+j] += sder[i3+j]
        return( cval )


    def distance( self, icrd, molec, jacob ):
        ai = self.atom[icrd][0]
        aj = self.atom[icrd][1]
        dd = [ (jj-ii) for ii,jj in zip( molec.coor[3*ai:3*ai+3], molec.coor[3*aj:3*aj+3] ) ]
        vv = math.sqrt( sum( [ ii*ii for ii in dd ] ) )
        for k in [0, 1, 2]:
            jacob[icrd*self.jcol+3*self.jidx[ai]+k] -= dd[k] / vv
            jacob[icrd*self.jcol+3*self.jidx[aj]+k] += dd[k] / vv
        return( vv )
