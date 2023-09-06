import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from scipy.spatial.distance import cdist
from warnings import warn

use_cupy = False

try:
    import cupy as cp
    use_cupy = True
    xp = cp
except ImportError as err:
    xp = np
    xp.asnumpy = lambda x: x
    warn("cupy is NOT installed. GPU-accelerated computation will not occur. ")
    warn(str(err))
    pass


class Grid:
    def __init__(self, *, x0, x1, xstep=1, y0, y1, ystep=1):
        """initializes 2D grid with x0<=x<=x1 and y0<=y<=y1;
        Creates a 1D numpy array of grid coordinates in self.x and self.y"""
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.xstep = xstep
        self.ystep = ystep
        xvals = np.arange(x0, x1 + xstep, xstep)
        yvals = np.arange(y1, y0 - ystep, -ystep)
        xgrid, ygrid = np.meshgrid(xvals, yvals)
        self.x = np.ravel(xgrid)
        self.y = np.ravel(ygrid)
        self.points = np.column_stack((self.x,self.y))
        # extent should match extent=(x0,x1,y0,y1) for compatibility with matplotlib.pyplot.contour
        # see https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.contour.html
        self.extent = (self.x0, self.x1, self.y0, self.y1)
        self.gshape = self.shape()
        self.boundary = ((self.x==x0) | (self.x==x1) | (self.y==y0) | (self.y==y1))
        self.len = self.gshape[0] * self.gshape[1]
        assert self.x.shape == (self.len,)
        assert self.y.shape == (self.len,)
        assert self.points.shape == (self.len,2)

    def shape(self, *, x0=None, x1=None, xstep=None, y0=None, y1=None, ystep=None):
        """returns a tuple(number_of_rows,number_of_cols) for the natural shape of the current grid, or a subset"""
        x0 = self.x0 if x0 is None else x0
        x1 = self.x1 if x1 is None else x1
        y0 = self.y0 if y0 is None else y0
        y1 = self.y1 if y1 is None else y1
        xstep = self.xstep if xstep is None else xstep
        ystep = self.ystep if ystep is None else ystep
        if x1 < x0:
            raise ValueError
        if y1 < y0:
            raise ValueError
        if xstep <= 0:
            raise ValueError
        if ystep <= 0:
            raise ValueError
        number_of_rows = 1 + int((y1 - y0) / ystep)
        number_of_cols = 1 + int((x1 - x0) / xstep)
        return (number_of_rows, number_of_cols)

    def within_box(self, *, x0=None, x1=None, y0=None, y1=None):
        """returns a 1D numpy boolean array, suitable as an index mask, for testing whether a grid point is also in the defined box"""
        x0 = self.x0 if x0 is None else x0
        x1 = self.x1 if x1 is None else x1
        y0 = self.y0 if y0 is None else y0
        y1 = self.y1 if y1 is None else y1
        return (self.x >= x0) & (self.x <= x1) & (self.y >= y0) & (self.y <= y1)

    def within_disk(self, *, x0, y0, r, metric="euclidean", **kwargs):
        """returns 1D numpy boolean array, suitable as an index mask, for testing whether a grid point is also in the defined disk"""
        mask = (
            cdist([[x0, y0]], self.points, metric=metric, **kwargs) <= r
        ).flatten()
        assert mask.shape == (self.len,)
        return mask
    
    def within_triangle(self,*,points):
        """returns 1D numpy boolean array, suitable as an index mask, for testing whether a grid point is also in the defined triangle"""
        points = np.asarray(points)
        assert points.shape == (3,2)
        barycentric_to_cartesian_matrix = np.row_stack((points[:,0],points[:,1],np.ones(points.shape[0])))
        assert barycentric_to_cartesian_matrix.shape == (3,3)
        cartesian_to_barycentrix_matrix = np.linalg.inv(barycentric_to_cartesian_matrix)
        mask = np.logical_not(
            np.any(
                np.dot(
                    cartesian_to_barycentrix_matrix,
                    np.row_stack(
                        (
                        self.x,
                        self.y,
                        np.ones(self.len)
                        )
                    )
                ) < (-1e-10),
            axis=0)
        )
        assert mask.shape == (self.len,)
        return mask 

    def index(self, *, x, y):
        """returns the unique 1D array index for grid point (x,y)"""
        isSelectedPoint = (self.x == x) & (self.y == y)
        indexes = np.flatnonzero((isSelectedPoint))
        assert len(indexes) == 1
        return indexes[0]

    def embedding(self, *, valid):
        """
        returns an embedding function efunc(z,fill=0.0) from 1D arrays z of size sum(valid)
        to arrays of size self.len

        valid is a np.array of type boolean, of size self.len

        fill is the value for indices outside the embedding. The default
        is zero (0.0).  Setting fill=np.nan can be useful for
        plotting purposes as matplotlib will omit np.nan values from various
        kinds of plots.
        """

        assert self.len == len(valid)
        correct_z_len = valid.sum()

        def efunc(z, fill=0.0):
            assert len(z) == correct_z_len
            v = np.full(self.len, fill)
            v[valid] = z
            return v

        return efunc

    def extremes(self, z, *, valid=None):
        # missing valid defaults to all True array for grid
        valid = np.full((self.len,), True) if valid is None else valid
        assert valid.shape == (self.len,)
        assert z.shape == (valid.sum(),)
        min_z = z.min()
        min_z_mask = np.abs(z-min_z)<1e-10
        max_z = z.max()
        max_z_mask = np.abs(z-max_z)<1e-10
        return (min_z,self.points[valid][min_z_mask],max_z,self.points[valid][max_z_mask])
        
    
    def spatial_utilities(
        self, *, voter_ideal_points, metric="sqeuclidean", scale=-1, **kwargs
    ):
        """returns utility function values for each voter at each grid point"""
        return scale * cdist(
            np.asarray(voter_ideal_points), self.points, metric=metric, **kwargs
        )

    def plot(
        self,
        z,
        *,
        title=None,
        cmap=cm.gray_r,
        alpha=0.6,
        alpha_points=0.3,
        log=True,
        points=None,
        zoom=False,
        border=1,
        logbias=1e-100,
        figsize=(10, 10),
        dpi=72,
        fname=None
    ):
        """plots values z defined on the grid;
        optionally plots additional 2D points
         and zooms to fit the bounding box of the points"""
        plt.figure(figsize=figsize, dpi=dpi)
        plt.rcParams["font.size"] = "24"
        fmt = "%1.2f" if log else "%.2e"
        if zoom:
            assert points.shape[0] > 2
            assert points.shape[1] == 2
            [min_x, min_y] = np.min(points, axis=0) - border
            [max_x, max_y] = np.max(points, axis=0) + border
            box = {"x0": min_x, "x1": max_x, "y0": min_y, "y1": max_y}
            inZoom = self.within_box(**box)
            zshape = self.shape(**box)
            extent = (min_x, max_x, min_y, max_y)
            zraw = np.copy(z[inZoom]).reshape(zshape)
            x = np.copy(self.x[inZoom]).reshape(zshape)
            y = np.copy(self.y[inZoom]).reshape(zshape)
        else:
            zshape = self.gshape
            extent = self.extent
            zraw = z.reshape(zshape)
            x = self.x.reshape(zshape)
            y = self.y.reshape(zshape)
        zplot = np.log10(logbias + zraw) if log else zraw
        contours = plt.contour(x, y, zplot, extent=extent, cmap=cmap)
        plt.clabel(contours, inline=True, fontsize=12, fmt=fmt)
        plt.imshow(zplot, extent=extent, cmap=cmap, alpha=alpha)
        if points is not None:
            plt.scatter(points[:, 0], points[:, 1], alpha=alpha_points, color="black")
        if title is not None:
            plt.title(title)
        if fname is None:
            plt.show()
        else:
            plt.savefig(fname)


def assert_valid_transition_matrix(P, *, decimal=10):
    """asserts that numpy or cupy array is square and that each row sums to 1.0
    with default tolerance of 10 decimal places"""
    rows, cols = P.shape
    assert rows == cols
    xp.testing.assert_array_almost_equal(P.sum(axis=1), xp.ones(shape=(rows)), decimal)


def assert_zero_diagonal_int_matrix(M):
    """asserts that numpy or cupy array is square and the diagonal is 0.0"""
    rows, cols = M.shape
    assert rows == cols
    xp.testing.assert_array_equal(xp.diagonal(M), xp.zeros(shape=(rows), dtype=int))

class MarkovChainCPUGPU:
    def __init__(self, *, P, computeNow=True, tolerance=1e-10):
        """initializes a MarkovChainCPUGPU instance by copying in the transition
        matrix P and calculating chain properties"""
        self.P = xp.asarray(P)  # copy transition matrix to cudapy as necessary
        assert_valid_transition_matrix(P)
        diagP = xp.diagonal(self.P)
        self.absorbing_points = xp.equal(diagP, 1.0)
        self.unreachable_points = xp.equal(xp.sum(self.P, axis=0), diagP)
        self.has_unique_stationary_distibution = not xp.any(self.absorbing_points)
        if computeNow and self.has_unique_stationary_distibution:
            self.find_unique_stationary_distribution(tolerance=tolerance)

    def L1_norm_of_single_step_change(self, x):
        """returns float(L1(xP-x))"""
        return float(xp.linalg.norm(xp.dot(x, self.P) - x, ord=1))

    def solve_for_unit_eigenvector(self):
        """This is another way to potentially find the stationary distribution,
        but can suffer from numerical irregularities like negative entries.
        Assumes eigenvalue of 1.0 exists and solves for the eigenvector by
        considering a related matrix equation Q v = b, where:
        Q is P transpose minus the identity matrix I, with the first row
        replaced by all ones for the vector scaling requirement;
        v is the eigenvector of eigenvalue 1 to be found; and
        b is the first basis vector, where b[0]=1 and 0 elsewhere."""
        n = self.P.shape[0]
        Q = xp.transpose(self.P) - xp.eye(n)
        Q[0] = xp.ones(n)
        b = xp.zeros(n)
        b[0] = 1.0
        error_unable_msg = "unable to find unique unit eigenvector "
        try:
            self.unit_eigenvector = xp.linalg.solve(Q, b)
        except Exception as err:
            warn(str(err)) # print the original exception lest it be lost for debugging purposes
            raise RuntimeError(error_unable_msg+"(solver)")
        if xp.isnan(self.unit_eigenvector.sum()):
            raise RuntimeError(error_unable_msg+"(nan)")
        if xp.any(self.unit_eigenvector<0.0):
            raise RuntimeError(error_unable_msg+"(negative components)")
        return self.unit_eigenvector

    def find_unique_stationary_distribution(self, *, tolerance, start_power=2, stop_power=65536):
        """finds the stationary distribution for a Markov Chain by
        taking a sufficiently high power of the transition matrix"""
        if xp.any(self.absorbing_points):
            self.stationary_distribution = None
            return None
        unconverged = True
        power = start_power
        P_power = xp.linalg.matrix_power(self.P, start_power)
        diags = {
            "power": [],
            "sum_min_minus_1": [],
            "sum_max_minus_1": [],
            "sad": [],
            "averaged": None,
            "first_index_at_max_prob": None,
            "zeroes_on_max_prob_row": None,
            "zeroed_check_norm_improvement": None
        }
        while unconverged:
            if power>=stop_power:
                del P_power
                raise(RuntimeError("Unable to find unique stationary distribution with power method; power="+str(power)))
            P_power = xp.linalg.matrix_power(P_power, 2)
            power = power * 2
            p_min = P_power.min(axis=0)
            p_max = P_power.max(axis=0)
            # cast to float is required because cp.sum yields a cp.cparray
            # with zero dimensions instead of a scalar
            #
            sum_absolute_diff = float(xp.linalg.norm(p_max - p_min, ord=1))
            # sum_min = sum of minimum probs, which should be below 1.0
            sum_min = float(p_min.sum())
            # sum_max = sum max probs, which could be above or below 1.0
            sum_max = float(p_max.sum())
            diags["sad"].append(sum_absolute_diff)
            diags["power"].append(power)
            diags["sum_max_minus_1"].append(sum_max-1.0)
            diags["sum_min_minus_1"].append(sum_min-1.0)
            unconverged = sum_absolute_diff > tolerance
            if not unconverged:
                # these extra steps are taken when there is a possible solution
                # use an average over all the rows to collapse P_power
                self.stationary_distribution = xp.average(P_power, axis=0)
                diags["averaged"] = True
                # double check the solution via an L1 norm
                self.check_norm = self.L1_norm_of_single_step_change(
                    self.stationary_distribution
                )
                unconverged = self.check_norm > tolerance
        # if we have a candidate, check the element that has the maximum probability
        # and see if the corresponding row of P^power has zeroes.  These are unreached alternatives
        # then check to see which distribution has a better L1 norm of single step change
        first_index_at_max_prob = int(xp.argmax(self.stationary_distribution))
        diags["first_index_at_max_prob"] = first_index_at_max_prob
        mle_row = xp.copy(P_power[first_index_at_max_prob,:])
        diags["zeroes_on_max_prob_row"] = int((mle_row==0.).sum())
        elements_to_zero = (mle_row==0.) & (self.stationary_distribution < tolerance)
        if (xp.any(elements_to_zero)):
            zeroed_stationary_distribution = mle_row
            zeroed_check_norm = self.L1_norm_of_single_step_change(
                zeroed_stationary_distribution
            )
            diags["zeroed_check_norm_improvement"] = self.check_norm-zeroed_check_norm
            # PB 09.04.2023 One goal of this code is to identify top cycles if they exist...
            # so if the check norm of the stationary distribution with zeroes is OK, use it
            # don't require that it is better than the check norm of the averaged distribution
            if (zeroed_check_norm <= tolerance):
                diags["averaged"] = False
                self.stationary_distribution = zeroed_stationary_distribution
                self.check_norm = zeroed_check_norm
        self.power = power
        self.power_method_diagnostics = diags
        del P_power
        return self.stationary_distribution

    def L1_norm_comparing_stationary_distributions(self,*,other):
        """returns L1 norm ||𝝿_power_method-𝝿_other|| """
        assert self.stationary_distribution.shape == other.shape
        return float(  # cast to float to avoid single-element array
          xp.linalg.norm(self.stationary_distribution-other, ord=1)
        )

    def diagnostic_metrics(self,*,danger=False):
        """ return Markov chain approximation metrics in mathematician-friendly format """
        metrics = {
            '||F||': self.P.shape[0],
            'power': self.power,
            '(𝝨𝝿)-1':  float(self.stationary_distribution.sum())-1.0, # cast to float to avoid cupy array singleton
            '||𝝿P-𝝿||_L1_norm': self.L1_norm_of_single_step_change(
                              self.stationary_distribution
                          )
        }
        # the following can crash (memory). Explicitly request with danger=True
        if danger:
            metrics['||𝝿_power-𝝿_algebraic||_L1_norm'] = \
                self.L1_norm_comparing_stationary_distributions(
                    other=self.solve_for_unit_eigenvector()
                )
        return metrics

class VotingModel:
    def __init__(
        self,
        *,
        utility_functions,
        number_of_voters,
        number_of_feasible_alternatives,
        majority,
        zi
    ):
        """initializes a VotingModel with utility_functions for each voter,
        the number_of_voters,
        the number_of_feasible_alternatives,
        the majority size, and whether to use zi fully random agenda or
        intelligent challengers random over winning set+status quo"""
        assert utility_functions.shape == (
            number_of_voters,
            number_of_feasible_alternatives,
        )
        self.utility_functions = utility_functions
        self.number_of_voters = number_of_voters
        self.number_of_feasible_alternatives = number_of_feasible_alternatives
        self.majority = majority
        self.zi = zi
        self.analyzed = False

    def E_𝝿(self,z):
        """returns mean, i.e., expected value of z under the stationary distribution"""
        return np.dot(self.stationary_distribution,z)

    def analyze(self):
        self.MarkovChain = MarkovChainCPUGPU(P=self._get_transition_matrix())
        self.core_points = xp.asnumpy(self.MarkovChain.absorbing_points)
        self.core_exists = np.any(self.core_points)
        if not self.core_exists:
            self.stationary_distribution = xp.asnumpy(
                self.MarkovChain.stationary_distribution
            )
        self.analyzed = True

    def what_beats(self, *, index):
        """returns array of size number_of_feasible_alternatives
        with value 1 where alternative beats current index by some majority"""
        assert self.analyzed
        points = xp.asnumpy(self.MarkovChain.P[index, :] > 0).astype("int")
        points[index] = 0
        return points

    def what_is_beaten_by(self, *, index):
        """returns array of size number_of_feasible_alternatives
        with value 1 where current index beats alternative by some majority"""
        assert self.analyzed
        points = xp.asnumpy(self.MarkovChain.P[:, index] > 0).astype("int")
        points[index] = 0
        return points
        
    def summarize_in_context(self,*,grid,valid=None):
        """calculate summary statistics for stationary distribution using grid's coordinates and optional subset valid"""
        # missing valid defaults to all True array for grid
        valid = np.full((grid.len,), True) if valid is None else valid
        # check valid array shape 
        assert valid.shape == (grid.len,)
        # get X and Y coordinates for valid grid points
        validX = grid.x[valid]
        validY = grid.y[valid]
        valid_points = grid.points[valid]
        if self.core_exists:
            return {
                'core_exists': self.core_exists,
                'core_points': valid_points[self.core_points]
            }
        # core does not exist, so evaulate mean, cov, min, max of stationary distribution
        # first check that the number of valid points matches the dimensionality of the stationary distribution
        assert (valid.sum(),) == self.stationary_distribution.shape
        point_mean = self.E_𝝿(valid_points) 
        cov = np.cov(valid_points,rowvar=False,ddof=0,aweights=self.stationary_distribution)
        (prob_min,prob_min_points,prob_max,prob_max_points) = \
            grid.extremes(self.stationary_distribution,valid=valid)
        _nonzero_statd = self.stationary_distribution[self.stationary_distribution>0]
        entropy_bits = -_nonzero_statd.dot(np.log2(_nonzero_statd))
        return {
            'core_exists': self.core_exists,
            'point_mean': point_mean,
            'point_cov': cov,
            'prob_min': prob_min,
            'prob_min_points': prob_min_points,
            'prob_max': prob_max,
            'prob_max_points': prob_max_points,
            'entropy_bits': entropy_bits 
        }

    def plots(
        self,
        *,
        grid,
        voter_ideal_points,
        diagnostics=False,
        log=True,
        embedding=lambda z, fill: z,
        zoomborder=0,
        dpi=72,
        figsize=(10, 10),
        fprefix=None,
        title_core="Core (aborbing) points",
        title_sad="L1 norm of difference in two rows of P^power",
        title_diff1="L1 norm of change in corner row",
        title_diff2="L1 norm of change in center row",
        title_sum1minus1="Corner row sum minus 1.0",
        title_sum2minus1="Center row sum minus 1.0",
        title_unreachable_points="Dominated (unreachable) points",
        title_stationary_distribution_no_grid="Stationary Distribution",
        title_stationary_distribution="Stationary Distribution",
        title_stationary_distribution_zoom="Stationary Distribution (zoom)"
    ):
        def _fn(name):
            return None if fprefix is None else fprefix + name

        def _save(fname):
            if fprefix is not None:
                plt.savefig(fprefix + fname)

        if self.core_exists:
            grid.plot(
                embedding(self.core_points.astype("int"), fill=np.nan),
                log=log,
                points=voter_ideal_points,
                zoom=True,
                title=title_core,
                dpi=dpi,
                figsize=figsize,
                fname=_fn("core.png"),
            )
            return None  # when core exists abort as additional plots undefined
        if diagnostics:
            df = pd.DataFrame(self.MarkovChain.power_method_diagnostics)
            df.plot.scatter(
                "power", "sad", loglog=True, title=title_sad, figsize=figsize
            )
            _save("diagnostic_sad.png")
            df.plot.scatter(
                "power", "diff1", loglog=True, title=title_diff1, figsize=figsize
            )
            _save("diagnostic_diff1.png")
            df.plot.scatter(
                "power", "diff2", loglog=True, title=title_diff2, figsize=figsize
            )
            _save("diagnostic_diff2.png")
            df.plot.scatter(
                "power",
                "sum1minus1",
                logx=True,
                title=title_sum1minus1,
                figsize=figsize,
            )
            _save("diagnostic_sum1minus1.png")
            df.plot.scatter(
                "power",
                "sum2minus1",
                logx=True,
                title=title_sum2minus1,
                figsize=figsize,
            )
            _save("diagnostic_sum2minus1.png")
            if grid is not None:
                grid.plot(
                    embedding(
                        xp.asnumpy(self.MarkovChain.unreachable_points).astype("int"),
                        fill=np.nan
                    ),
                    log=log,
                    title=title_unreachable_points,
                    dpi=dpi,
                    figsize=figsize,
                    fname=_fn("unreachable.png"),
                )
        z = self.stationary_distribution
        if grid is None:
            pd.Series(z).plot(
                title=title_stationary_distribution_no_grid, figsize=figsize
            )
            _save("stationary_distribubtion_no_grid.png")
        else:
            grid.plot(
                embedding(z, fill=np.nan),
                log=log,
                points=voter_ideal_points,
                title=title_stationary_distribution,
                figsize=figsize,
                dpi=dpi,
                fname=_fn("stationary_distribution.png"),
            )
            if voter_ideal_points is not None:
                grid.plot(
                    embedding(z, fill=np.nan),
                    log=log,
                    points=voter_ideal_points,
                    zoom=True,
                    border=zoomborder,
                    title=title_stationary_distribution_zoom,
                    figsize=figsize,
                    dpi=dpi,
                    fname=_fn("stationary_distribution_zoom.png"),
                )

    def _get_transition_matrix(self):
        utility_functions = self.utility_functions
        majority = self.majority
        zi = self.zi
        nfa = self.number_of_feasible_alternatives
        cV = xp.zeros(shape=(nfa, nfa), dtype=int)
        cU = xp.asarray(utility_functions)
        for a in range(nfa):
            total_votes_for_challenger_when_status_quo_is_a = (
                xp.greater(cU, cU[:, a, xp.newaxis]).astype("int").sum(axis=0)
            )
            total_votes_shape = total_votes_for_challenger_when_status_quo_is_a.shape
            assert total_votes_shape == (nfa,)
            cV[a] = xp.greater_equal(
                total_votes_for_challenger_when_status_quo_is_a, majority
            ).astype("int")
        assert_zero_diagonal_int_matrix(cV)
        cV_sum_of_row = cV.sum(axis=1)  # sum up all col for each row
        # set up the ZI and MI transiation matrices
        if zi:
            cP = xp.divide(xp.add(cV, xp.diag(xp.subtract(nfa, cV_sum_of_row))), nfa)
        else:
            cP = xp.divide(xp.add(cV, xp.eye(nfa)), (1 + cV_sum_of_row)[:, xp.newaxis])
        assert_valid_transition_matrix(cP)
        return cP


class CondorcetCycle(VotingModel):
    def __init__(self, *, zi):
        # docs suggest to call superclass directly
        # instead of using super()
        # https://docs.python.org/3/tutorial/classes.html#inheritance
        VotingModel.__init__(
            self,
            zi=zi,
            number_of_voters=3,
            majority=2,
            number_of_feasible_alternatives=3,
            utility_functions=np.array(
                [
                    [3, 2, 1],  # first agent prefers A>B>C
                    [1, 3, 2],  # second agent prefers B>C>A
                    [2, 1, 3],  # third agents prefers C>A>B
                ]
            ),
        )
