from __future__ import print_function, absolute_import
from builtins import map, filter, range
from .sortedDict import SortedDict
import numpy as np 
import matplotlib.pyplot as plt

__all__ = ['STELLout', 'OMFITascii']

class OMFITascii(object):
    """
    OMFIT class used to interface with ASCII files

    :param filename: filename passed to OMFITobject class

    :param fromString: string that is written to file

    :param \**kw: keyword dictionary passed to OMFITobject class
    """
    def __init__(self, filename, **kw):
        fromString = kw.pop('fromString', None)
        self.filename = filename
        if fromString is not None:
            with open(self.filename, 'wb') as f:
                f.write(fromString.encode('utf-8'))

    def read(self):
        '''
        Read ASCII file and return content

        :return: string
        '''
        return open(self.filename, 'r').read()

    def write(self, value):
        '''
        Write string value to ASCII file

        :param value: string to be written to file

        :return: string
        '''
        open(self.filename, 'w').write(value)
        return value

    def append(self, value):
        '''
        Append string value to ASCII file

        :param value: string to be written to file

        :return: string
        '''
        open(self.filename, 'a').write(value)
        return self.read()

class STELLout(SortedDict, OMFITascii):
    """
    OMFITobject used to interface with stellopt.* file in STELLOPT outputs.

    :param filename: filename passed to OMFITascii class

    All additional key word arguments passed to OMFITascii

    """

    def __init__(self, filename, **kwargs):
        SortedDict.__init__(self)
        OMFITascii.__init__(self, filename, **kwargs)
        self.dynaLoad = True

    def load(self):
        """Load the file and parse it into a sorted dictionary"""
        file_handle = open(self.filename,'r')
        niter = 0
        for line in file_handle:
            if 'ITER' in line:
                niter=niter+1
            if 'MIN' in line:
                niter=niter-1
        self['ITER'] = np.ndarray((niter,1));
        file_handle.seek(0)
        line = file_handle.readline()
        ttype,wh=line.split()
        self[ttype] = float(wh)

        # Enter Loop
        citer = -1
        while True:
            line = file_handle.readline()
            if line == '':
                break
            ttype,hw = line.split(' ',1)
            if ttype == 'ITER':
                if 'MIN' in hw:
                    break
                citer = citer+1
                self[ttype][citer] = int(hw)
                continue
            else:
                h,w = hw.split()
                h = int(h)
                w = int(w)
                line = file_handle.readline()
            if ttype not in self:
                self[ttype]=np.ndarray((niter,h,w))
            for i in range(h):
                line = file_handle.readline()
                val = np.fromstring(line,sep=' ')
                self[ttype][citer,i,:] = val       
        file_handle.close()
        for item in list(self):
            # print(item)
            if 'VERSION' == item:
                continue
            elif 'ITER' == item:
                continue
            elif item in ['ASPECT','ASPECT_MAX','BETA','CURTOR','PHIEDGE', \
                        'VOLUME','WP','RBTOR','R0','Z0','BETATOR','BETAPOL']:
                self[item+'_target'] = np.squeeze(self[item][:,:,0])
                self[item+'_sigma'] = np.squeeze(self[item][:,:,1])
                self[item+'_equil'] = np.squeeze(self[item][:,:,2])
                self[item+'_chisq'] = ((self[item+'_target'] - self[item+'_equil'])/self[item+'_sigma'])**2
            elif item == 'BALLOON':
                self[item+'_target'] = np.squeeze(self[item][:,:,0])
                self[item+'_sigma'] = np.squeeze(self[item][:,:,1])
                self[item+'_equil'] = np.squeeze(self[item][:,:,2])
                self[item+'_chisq'] = ((self[item+'_target'] - self[item+'_equil'])/self[item+'_sigma'])**2
                self[item+'_grate'] = np.squeeze(self[item][:,:,3])
                self[item+'_theta'] = np.squeeze(self[item][:,:,4])
                self[item+'_zeta'] = np.squeeze(self[item][:,:,5])
                self[item+'_k'] = np.squeeze(self[item][:,:,6])
            elif item == 'B_PROBES':
                self[item+'_target'] = np.squeeze(self[item][:,:,4])
                self[item+'_sigma'] = np.squeeze(self[item][:,:,5])
                self[item+'_equil'] = np.squeeze(self[item][:,:,6])
                self[item+'_chisq'] = ((self[item+'_target'] - self[item+'_equil'])/self[item+'_sigma'])**2
                self[item+'_X'] = np.squeeze(self[item][:,:,0])
                self[item+'_Y'] = np.squeeze(self[item][:,:,1])
                self[item+'_Z'] = np.squeeze(self[item][:,:,2])
                self[item+'_MODB'] = np.squeeze(self[item][:,:,3])
            elif item in ['FLUXLOOPS','SEGROG']:
                self[item+'_target'] = np.squeeze(self[item][:,:,0])
                self[item+'_sigma'] = np.squeeze(self[item][:,:,1])
                self[item+'_equil'] = np.squeeze(self[item][:,:,2])
                self[item+'_chisq'] = ((self[item+'_target'] - self[item+'_equil'])/self[item+'_sigma'])**2
            elif item == 'EXTCUR':
                self[item+'_target'] = np.squeeze(self[item][:,:,0])
                self[item+'_sigma'] = np.squeeze(self[item][:,:,1])
                self[item+'_equil'] = np.squeeze(self[item][:,:,2])
                self[item+'_chisq'] = ((self[item+'_target'] - self[item+'_equil'])/self[item+'_sigma'])**2
                self[item+'_dex'] = np.squeeze(self[item][:,:,3])
            elif item in ['SEPARATRIX','LIMITER']:
                self[item+'_target'] = np.squeeze(self[item][:,:,0])
                self[item+'_sigma'] = np.squeeze(self[item][:,:,1])
                self[item+'_equil'] = np.squeeze(self[item][:,:,2])
                self[item+'_chisq'] = ((self[item+'_target'] - self[item+'_equil'])/self[item+'_sigma'])**2
                self[item+'_R'] = np.squeeze(self[item][:,:,4])
                self[item+'_PHI'] = np.squeeze(self[item][:,:,5])
                self[item+'_Z'] = np.squeeze(self[item][:,:,6])
            elif item in ['TI','TE','IOTA','VPHI','PRESS','NE']:
                self[item+'_target'] = np.squeeze(self[item][:,:,4])
                self[item+'_sigma'] = np.squeeze(self[item][:,:,5])
                self[item+'_equil'] = np.squeeze(self[item][:,:,6])
                self[item+'_chisq'] = ((self[item+'_target'] - self[item+'_equil'])/self[item+'_sigma'])**2
                self[item+'_R'] = np.squeeze(self[item][:,:,0])
                self[item+'_PHI'] = np.squeeze(self[item][:,:,1])
                self[item+'_Z'] = np.squeeze(self[item][:,:,2])
                self[item+'_S'] = np.squeeze(self[item][:,:,3])
            elif item in ['NELINE','FARADAY','SXR']:
                self[item+'_target'] = np.squeeze(self[item][:,:,0])
                self[item+'_sigma'] = np.squeeze(self[item][:,:,1])
                self[item+'_equil'] = np.squeeze(self[item][:,:,2])
                self[item+'_chisq'] = ((self[item+'_target'] - self[item+'_equil'])/self[item+'_sigma'])**2
                self[item+'_R0'] = np.squeeze(self[item][:,:,3])
                self[item+'_PHI0'] = np.squeeze(self[item][:,:,4])
                self[item+'_Z0'] = np.squeeze(self[item][:,:,5])
                self[item+'_R1'] = np.squeeze(self[item][:,:,6])
                self[item+'_PHI1'] = np.squeeze(self[item][:,:,7])
                self[item+'_Z1'] = np.squeeze(self[item][:,:,8])
            elif item == 'MSE':
                self[item+'_target'] = np.squeeze(self[item][:,:,4])
                self[item+'_sigma'] = np.squeeze(self[item][:,:,5])
                self[item+'_equil'] = np.squeeze(self[item][:,:,8])
                self[item+'_chisq'] = ((self[item+'_target'] - self[item+'_equil'])/self[item+'_sigma'])**2
                self[item+'_R'] = np.squeeze(self[item][:,:,0])
                self[item+'_PHI'] = np.squeeze(self[item][:,:,1])
                self[item+'_Z'] = np.squeeze(self[item][:,:,2])
                self[item+'_S'] = np.squeeze(self[item][:,:,3])
                self[item+'_ER'] = np.squeeze(self[item][:,:,6])
                self[item+'_EZ'] = np.squeeze(self[item][:,:,7])
            elif item == 'BOOTSTRAP':
                self[item+'_target'] = np.squeeze(self[item][:,:,0])
                self[item+'_sigma'] = np.squeeze(self[item][:,:,1])
                self[item+'_equil'] = np.squeeze(self[item][:,:,2])
                self[item+'_chisq'] = ((self[item+'_target'] - self[item+'_equil'])/self[item+'_sigma'])**2
                self[item+'_S'] = np.squeeze(self[item][:,:,3])
                self[item+'_avg_jdotb'] = np.squeeze(self[item][:,:,4])
                self[item+'_beam_jdotb'] = np.squeeze(self[item][:,:,5])
                self[item+'_boot_jdotb'] = np.squeeze(self[item][:,:,6])
                self[item+'_jBbs'] = np.squeeze(self[item][:,:,7])
                self[item+'_facnu'] = np.squeeze(self[item][:,:,8])
                self[item+'_bsnorm'] = np.squeeze(self[item][:,:,9])
            elif item == 'HELICITY':
                self[item+'_target'] = np.squeeze(self[item][:,:,0])
                self[item+'_sigma'] = np.squeeze(self[item][:,:,1])
                self[item+'_equil'] = np.squeeze(self[item][:,:,2])
                self[item+'_chisq'] = ((self[item+'_target'] - self[item+'_equil'])/self[item+'_sigma'])**2
                self[item+'_bnorm'] = np.squeeze(self[item][:,:,3])
                self[item+'_m'] = np.squeeze(self[item][:,:,4])
                self[item+'_n'] = np.squeeze(self[item][:,:,5])
            elif item ==  'HELICITY_FULL':
                self[item+'_target'] = np.squeeze(self[item][:,:,0])
                self[item+'_sigma'] = np.squeeze(self[item][:,:,1])
                self[item+'_equil'] = np.squeeze(self[item][:,:,2])
                self[item+'_chisq'] = ((self[item+'_target'] - self[item+'_equil'])/self[item+'_sigma'])**2
                self[item+'_bnorm'] = np.squeeze(self[item][:,:,3])
                self[item+'_k'] = np.squeeze(self[item][:,:,4])
                self[item+'_m'] = np.squeeze(self[item][:,:,5])
                self[item+'_n'] = np.squeeze(self[item][:,:,6])               
            elif item == 'TXPORT':
                self[item+'_target'] = np.squeeze(self[item][:,:,0])
                self[item+'_sigma'] = np.squeeze(self[item][:,:,1])
                self[item+'_equil'] = np.squeeze(self[item][:,:,2])
                self[item+'_chisq'] = ((self[item+'_target'] - self[item+'_equil'])/self[item+'_sigma'])**2
                self[item+'_S'] = np.squeeze(self[item][:,:,3])
            elif item == 'COIL_BNORM':
                self[item+'_target'] = np.squeeze(self[item][:,:,0])
                self[item+'_sigma'] = np.squeeze(self[item][:,:,1])
                self[item+'_equil'] = np.squeeze(self[item][:,:,2])
                self[item+'_chisq'] = ((self[item+'_target'] - self[item+'_equil'])/self[item+'_sigma'])**2
                self[item+'_U'] = np.squeeze(self[item][:,:,3])
                self[item+'_V'] = np.squeeze(self[item][:,:,4])
                self[item+'_BNEQ'] = np.squeeze(self[item][:,:,5])
                self[item+'_BNF'] = np.squeeze(self[item][:,:,6])
            elif item == 'ORBIT':
                self[item+'_target'] = np.squeeze(self[item][:,:,0])
                self[item+'_sigma'] = np.squeeze(self[item][:,:,1])
                self[item+'_equil'] = np.squeeze(self[item][:,:,2])
                self[item+'_chisq'] = ((self[item+'_target'] - self[item+'_equil'])/self[item+'_sigma'])**2
                self[item+'_S'] = np.squeeze(self[item][:,:,3])
            elif item == 'J_STAR':
                self[item+'_target'] = np.squeeze(self[item][:,:,0])
                self[item+'_sigma'] = np.squeeze(self[item][:,:,1])
                self[item+'_equil'] = np.squeeze(self[item][:,:,2])
                self[item+'_chisq'] = ((self[item+'_target'] - self[item+'_equil'])/self[item+'_sigma'])**2
                self[item+'_AVGJSTAR'] = np.squeeze(self[item][:,:,3])
                self[item+'_TRAPSJSTAR'] = np.squeeze(self[item][:,:,4])
                self[item+'_UJSTAR'] = np.squeeze(self[item][:,:,5])
                self[item+'_K'] = np.squeeze(self[item][:,:,6])
                self[item+'_IJSTAR'] = np.squeeze(self[item][:,:,7])
            elif item == 'NEO':
                self[item+'_target'] = np.squeeze(self[item][:,:,0])
                self[item+'_sigma'] = np.squeeze(self[item][:,:,1])
                self[item+'_equil'] = np.squeeze(self[item][:,:,2])
                self[item+'_chisq'] = ((self[item+'_target'] - self[item+'_equil'])/self[item+'_sigma'])**2
                self[item+'_K'] = np.squeeze(self[item][:,:,3])
            elif item == 'JDOTB':
                self[item+'_target'] = np.squeeze(self[item][:,:,0])
                self[item+'_sigma'] = np.squeeze(self[item][:,:,1])
                self[item+'_equil'] = np.squeeze(self[item][:,:,2])
                self[item+'_chisq'] = ((self[item+'_target'] - self[item+'_equil'])/self[item+'_sigma'])**2
                self[item+'_S'] = np.squeeze(self[item][:,:,3])
            elif item == 'JTOR':
                self[item+'_target'] = np.squeeze(self[item][:,:,0])
                self[item+'_sigma'] = np.squeeze(self[item][:,:,1])
                self[item+'_equil'] = np.squeeze(self[item][:,:,2])
                self[item+'_chisq'] = ((self[item+'_target'] - self[item+'_equil'])/self[item+'_sigma'])**2
                self[item+'_S'] = np.squeeze(self[item][:,:,3])
            elif item == 'DKES':
                self[item+'_target'] = np.squeeze(self[item][:,:,0])
                self[item+'_sigma'] = np.squeeze(self[item][:,:,1])
                self[item+'_equil'] = np.squeeze(self[item][:,:,2])
                self[item+'_chisq'] = ((self[item+'_target'] - self[item+'_equil'])/self[item+'_sigma'])**2
                self[item+'_S'] = np.squeeze(self[item][:,:,3])
                self[item+'_NU'] = np.squeeze(self[item][:,:,4])
                self[item+'_ER'] = np.squeeze(self[item][:,:,5])
                self[item+'_L11P'] = np.squeeze(self[item][:,:,6])
                self[item+'_L11M'] = np.squeeze(self[item][:,:,7])
                self[item+'_L33P'] = np.squeeze(self[item][:,:,8])
                self[item+'_L33M'] = np.squeeze(self[item][:,:,9])
                self[item+'_L31P'] = np.squeeze(self[item][:,:,10])
                self[item+'_L31M'] = np.squeeze(self[item][:,:,11])
                self[item+'_SCAL11'] = np.squeeze(self[item][:,:,12])
                self[item+'_SCAL33'] = np.squeeze(self[item][:,:,13])
                self[item+'_SCAL31'] = np.squeeze(self[item][:,:,14])
        return

    def plot_helicity(self, it=-1, ordering=0, mn=(None, None), ax=None, **kwargs):     
        """Plot |B| components in Boozer coordinates from BOOZ_XFORM

        Args:
            it (int, optional): Iteration index to be plotted. Defaults to -1.
            ordering (integer, optional): Plot the leading Nordering asymmetric modes. Defaults to 0.
            mn (tuple, optional): Plot the particular (m,n) mode. Defaults to (None, None).
            ax (Matplotlib axis, optional): Matplotlib axis to be plotted on. Defaults to None.
            kwargs (dict): Keyword arguments for matplotlib.pyplot.plot. Defaults to {}.
        
        Returns:
            ax (Matplotlib axis): Matplotlib axis plotted on.
        """ 
        from .booz_xform import BOOZ_XFORM    
        xs = self['HELICITY_FULL_k']
        xs = np.array(np.unique(xs), dtype=int)
        ns = len(xs)
        xx = (xs-1)/np.max(xs) # max(xs) might be different from NS
        vals = np.reshape(self['HELICITY_FULL_equil'][it], (ns, -1))
        xm = np.reshape(np.array(self['HELICITY_FULL_m'][it], dtype=int), (ns, -1))
        xn = np.reshape(np.array(self['HELICITY_FULL_n'][it], dtype=int), (ns, -1))
        return BOOZ_XFORM.plot_helicity(vals, xm[0,:], xn[0,:], xx, ordering, mn, ax, **kwargs)
