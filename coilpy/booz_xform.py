import numpy as np 
import matplotlib.pyplot as plt
from .sortedDict import SortedDict

__all__ = ['BOOZ_XFORM']

class BOOZ_XFORM(SortedDict):
    def __init__(self, filename, **kwargs):
        import xarray
        SortedDict.__init__(self)
        self.output = xarray.open_dataset(filename)
        self.ns = int(self.output['ns_b'].values)
        self.nfp = int(self.output['nfp_b'].values)
        self.xm = self.output['ixm_b'].values
        self.xn = self.output['ixn_b'].values / self.nfp
        self.jlist = self.output['jlist'].values
        self.bmnc = self.output['bmnc_b'].values
        return
    
    @staticmethod
    def write_input(extension, mbooz, nbooz, surfaces):
        """Write a BOO_XFORM input file

        Args:
            extension (str): VMEC output extension.
            mbooz (int): Maximum poloidal mode. 
            nbooz (int): Maximum toroidal mode 
            surfaces (list): List of flux surfaces.
        """        
        template = """{mbooz:d}  {nbooz:d}
'{extension:s}'
{surfaces:s}
        """
        assert mbooz>0, "mbooz should be >0."
        assert nbooz>0, "nbooz should be >0."
        surfaces = ['{:} '.format(i) for i in surfaces]
        surfaces = ''.join(surfaces)
        with open('inbooz.'+extension, 'w') as f:
            f.write(template.format(mbooz=mbooz,
                                    nbooz=nbooz,
                                    extension=extension,
                                    surfaces=surfaces))
        return

    @staticmethod
    def from_vmec(wout, mbooz=0, nbooz=0, surfaces=[]):
        """Prepare BOOZ_XFORM input file from VMEC wout file

        Args:
            wout (str): VMEC wout filename.
            mbooz (int, optional): Maximum poloildal mode number. Defaults to 0 (4*Mpol).
            nbooz (int, optional): Maximum toroidal mode number. Defaults to 0 (4*Ntor).
            surfaces (list, optional): Flux surfaces list. Defaults to [] (1:NS).

        """        
        import xarray
        vmec = xarray.open_dataset(wout, 'r')
        ind = wout.index('wout_') + 5
        end = wout.index('.nc')
        extension = wout[ind:end]
        if mbooz == 0:
            mbooz = 4*int(vmec['mpol'].values) + 1
        if nbooz == 0:
            nbooz = 4*int(vmec['ntor'].values)
        if len(surfaces) == 0:
            ns = int(vmec['ns'].values)
            surfaces = 1 + np.arange(ns)
        vmec.close()
        return BOOZ_XFORM.write_input(extension, mbooz, nbooz, surfaces)
    
    def plot(self, ordering=0, mn=(None, None), ax=None, **kwargs):
        """Plot |B| components 1D profile

        Args:
            ordering (integer, optional): Plot the leading Nordering asymmetric modes. Defaults to 0.
            mn (tuple, optional): Plot the particular (m,n) mode. Defaults to (None, None).
            ax (Matplotlib axis, optional): Matplotlib axis to be plotted on. Defaults to None.
            kwargs (dict): Keyword arguments for matplotlib.pyplot.plot. Defaults to {}.
        
        Returns:
            ax (Matplotlib axis): Matplotlib axis plotted on.
        """ 
        xx = self.jlist / self.ns
        return self.plot_helicity(self.bmnc, self.xm, self.xn, xx, ordering, mn, ax, **kwargs)

    @staticmethod
    def plot_helicity(*args, **kwargs):
        vals, xm, xn, xx, ordering, mn, ax = args
        # get figure and ax data
        if ax is None:
            fig, ax = plt.subplots()
        plt.sca(ax)
        # select the top ordering asymmetric terms
        if ordering:
            assert ordering >= 1
            data = np.linalg.norm(vals, axis=0)
            ind_arg = np.argsort(data)
            for i in range(ordering):
                ind = ind_arg[-1-i] # index of the i-th largest term
                m = xm[ind]
                n = xn[ind]
                kwargs['label'] = 'm={:}, n={:}'.format(m,n)
                ax.plot(xx, vals[:, ind], **kwargs)
            ylabel = r'$\frac{B_{m,n}}{ \Vert B_{n=0} \Vert }$'
        else:
            # determine filter condition
            if mn[0] is not None:
                mfilter = (xm == mn[0])
                m = 'm={:}'.format(mn[0])
            else:
                mfilter = np.full(np.shape(xm), True)
                m = 'm'
            if mn[1] is not None:
                nfilter = (xn == mn[1])
                n = 'n={:}'.format(mn[1])
            else:
                nfilter = (xn != 0)
                n = r'n \neq 0'
            cond = np.logical_and(mfilter, nfilter)
            #data = np.reshape(vals[:, cond], (ns, -1))
            data = vals[:, cond]
            line = ax.plot(xx, np.linalg.norm(data, axis=1), **kwargs)
            ylabel = r'$ \frac{{ \Vert B_{{ {:},{:} }} \Vert }}{{ \Vert B_{{n=0}} \Vert }} $'.format(m, n)
        plt.xlabel('normalized flux (s)', fontsize=16)
        plt.ylabel(ylabel, fontsize=16)
        plt.xticks(fontsize=15)
        plt.yticks(fontsize=15)
        return ax

    def to_FOCUS(self, ns=-1, focus_file='plasma.boundary', tol=1.0E-8):
        """Write a FOCUS plasma boundary file in Boozer coordinates

        Args:
            ns (int, optional): Flux surface label to be exported. Defaults to -1.
            focus_file (str, optional): FOCUS plasma boundary file name. Defaults to 'plasma.boundary'.
            tol (float, optional): Truncated tolerance. Defaults to 1.0E-8.
        """        
        mn = int(self.output['mnboz_b'].values)
        rbc = np.array(self.output['rmnc_b'][ns,:])
        #rbs = np.zeros(mn)
        zbs = np.array(self.output['zmns_b'][ns,:])
        #zbc = np.zeros(mn)
        pmns = np.array(self.output['pmns_b'][ns,:])
        #pmnc = np.zeros(mn)
        Nbnf = 0
        # count non-zero terms
        amn = 0
        for imn in range(mn):
            if (abs(rbc[imn])+abs(zbs[imn]+abs(pmns[imn]))) > tol :
                amn += 1 # number of nonzero coef.
        # write FOCUS plasma boundary file
        with open(focus_file, 'w') as fofile:
            fofile.write('# bmn   bNfp   nbf '+'\n')
            fofile.write("{:d} \t {:d} \t {:d} \n".format(amn, self.nfp, Nbnf))
            fofile.write('#plasma boundary'+'\n')
            fofile.write('# n m Rbc Rbs Zbc Zbs Pmnc Pmns'+'\n')
            for imn in range(mn):
                if (abs(rbc[imn])+abs(zbs[imn]+abs(pmns[imn]))) > tol :
                    fofile.write("{:4d}  {:4d} \t {:23.15E}  {:12.5E}  {:12.5E} {:23.15E} {:12.5E}  {:23.15E} \n"
                                .format(self.xn[imn], self.xm[imn], rbc[imn], 0.0, 0.0, zbs[imn], 0.0, pmns[imn]))
            fofile.write("#Bn harmonics \n")
            fofile.write('# n m bnc bns'+'\n')          
        return
