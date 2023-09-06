# gridvoting

This software began as a library module for our [research publication (open-access)](https://doi.org/10.1007/s11403-023-00387-8):
<pre>
  Brewer, P., Juybari, J. & Moberly, R. 
  A comparison of zero- and minimal-intelligence agendas in majority-rule voting models. 
  J Econ Interact Coord (2023). https://doi.org/10.1007/s11403-023-00387-8
</pre>

This software helps set up, calculate, and plot stationary probability distributions for
sequential voting simulations (with ZI or MI random challengers) that take place on a 2D grid of feasible outcomes.

In our paper, we used the simulations to show that adding intelligence to the agenda of a collection of voting bots does not necessarily
improve the fairness or reasonableness of outcomes.  We're not claiming adding intelligence is always bad, since one 
cannot deduce such generalities from a few simulations. But in some well-known scenarios, the simulations demonstrate cases where
adding intelligence to the voting agenda can increase the variance and decrease the equality of outcomes for equally situated agents.

## use of Google Colab

We used [Google Colab](https://colab.google), a cloud-based service that runs Python-based analyses on Google's servers and GPUs,
for conducting most of the research reported in the publication above.  When using Google Colab, the local computer does NOT need to have a GPU.

The software has also run (without Colab) on a local computer with a Nvidia gaming GPU, and remote computers with industrial Nvidia A100 GPUs.

## requirements
* For GPU machines, Nvidia CUDA drivers (except on Google Colab, where CUDA is pre-installed)
* Python 3 
* these Python-3 scientific computing modules (except on Google Colab, where these are all preinstalled):
  - numpy
  - pandas
  - matplotlib
  - scipy
  - cupy (preinstalled on Google Colab GPU machines; omitted when GPU is absent)
* familiarity with Python language / scientific computing / gpu Nvidia-CUDA setup

It will run faster with a GPU than on CPU alone, we saw a 10-30x speedup at times. In one case, an Nvidia A100-40GB GPU would 
run in 30 seconds what was taking 10 minutes on 12 CPU cores.

## installation

on Google Colab:
```
!pip install gridvoting
```
If you use a Google Colab runtime that includes a GPU, gridvoting should recognize it.
It will run, but slowly, on standard Colab machines that lack a GPU.

----

on windows, linux, or macos:

If you have a GPU, be sure to check/install Nvidia Cuda drivers and matching cupy python module.
To install the gridvoting module:
```
python3 -m pip install --user gridvoting
```

## tests

To run our automated tests and generate a test report, run the following commands:

on Google Colab:
```
!pip install gridvoting
!cd /usr/local/lib/python3.10/dist-packages/gridvoting && python3 -m pytest -sv .
```
Note that `/usr/local/lib/python3.10/dist-packages/gridvoting` is the usual installation location on Colab.
If gridvoting is installed elsewhere, you can find it in Colab with `!find / -name gridvoting`

on windows, linux, or macos, 
1. install pytest, cupy, and gridvoting as necessary
2. find where gridvoting is installed
3. cd to that directory
4. to run the test use this command:  `python3 -m pytest -sv .`


## License

The software is provided under the standard [MIT License](./LICENSE.md). 

You are welcome to try the software, read it, copy it, adapt it to your
needs, and redistribute your adaptations. If you change the software, be sure to change the module name somehow so that
others know it is not the original.  See the LICENSE file for more details.  

## Disclaimers

The software is provided in the hope that it may be useful to others, but it is not a full featured turnkey
system for conducting arbitrary voting simulations. Additional coding is required to define a specific simulation.

Beginning with version 0.50.0, automated tests exist on linux, windows. and macOS.  These tests ideally run on GitHub Actions each time
a change is made in the software. This cannot guarantee that the software is free of "bugs" or defects or that it will run on your computer
without adjustments.  

The [MIT License](./LICENSE.md) also includes this disclaimer: 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE
FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION 
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

## code and data for specific simulations

Code specific to the spatial voting and budget voting portions of our research publication above -- as well as output data -- 
is deposited at: [OSF Dataset for A comparison of zero and minimal Intelligence agendas in majority rule voting models](https://osf.io/k2phe/)
and is freely available.

## Random sequential voting simulations

This follows [section 2 of our research paper](https://link.springer.com/article/10.1007/s11403-023-00387-8#Sec4)

A simulation consists of a sequence of times: `t=0,1,2,3,...`
a finite feasible set of alternatives **F**, a set of voters who have preferences over the alternatives and vote truthfully,
a rule for voting and selecting challengers, and a mapping of the set of alternativies **F** into a 2D grid.  

The active or status quo alternative at time t is called `f[t]`.  

At each t, there is a majority-rule vote between alternative `f[t]` and a challenger
alternative `c[t]`.  The winner of that vote becomes the next status quo `f[t+1]`.  

Randomness enters the simulation through two possible rules for choosing the challenger
`c[t]`.  When `zi=True`, `c[t]` is chosen from the "Zero Intelligence" agenda which consists
of a uniform random distribution over **F**.  When `zi=False`, `c[t]` is chosen from the 
"Minimal Intelligence" agenda which is a uniform distribution over the status quo `f[t]` and the possible
winning alternatives given the status quo `f[t]`.

## Principles of Operation 
This section extends a higher, more mathematical description from [section 3 of our research paper](https://link.springer.com/article/10.1007/s11403-023-00387-8#Sec5).
with an overview of the code in the gridvoting module.

The gridvoting software module is designed to separate various concerns and manage the overlap of concepts.  

A primary concern is data transformation between different tasks.  The VotingModel and related Markov chain require a probabilistic vector space of dim number_of_alternatives.
Plotting occurs in a rectangular area.  The alternatives then also need to have coordinates within a rectangular area.  Utility functions for the 
alternatives might also depend on their coordinates.  If the alternatives' coordinates are not equivalent to a complete rectangular grid, then there needs to be
an embedding function from some smaller space into the rectangular area in order to communicate the results from the Markov chain calculation to the plotting routines
to the viewers' screen.  The Python3 `numpy` module creates arrays that are easy to reshape and manipulate, and is used intenally for many of the data transfomations.
Knowledge of how `numpy` can be used to manipulate data will be useful in writing additional code to further manipulate or analyze simulation data.
The `cupy` module is a drop-in replacement for `numpy` for accelerating data manipulation by using a hardware GPU.

The various concepts are coordinate grids, shapes within a grid, defining a voting simulation, and calculating the stationary distribution of the simulation
by a GPU-based MarkovChain calculation.  For example, one can have a voting simulation without a grid, or one can have a simulation where
the feasible alternatives are points within a triangle (from a budget constraint) itself embedded within a square grid for plotting purposes.

The `VotingModel` class manages simulations.  Each simulation is an instance of `VotingModel`.  The constructor
requires various properties of the simulation, such as the number of voters, number of alternatives, and voters' utility functions.
Utility functions are defined not as Python3 functions but as numeric arrays of dim `(number_of_voters, number_of_alternatives)` defining the 
utility of each voter for each outcome as a number where more is better. It is the ordering and not the values that are important.  
Besides plotting and answering simple questions about the alternatives, the class also provides code
for calculating the transition matrix and providing it as an input to the `MarkovChainGPU` class below.

The `Grid` class manages rectangular grids. An instance of `VotingModel` will usually specify
a Grid instance for defining utility functions and plotting/visualization purposes.  It is also possible to use `VotingModel`
without specifying any kind of grid or coordinate mapping, for an example see class `CondorcetCycle`.

The `MarkovChainGPU` class manages a Markov Chain calulation on a GPU.  This class is called 
internally from `VotingModel`.  The class contains two methods for calculating the 
stationary distribution of a Markov Chain: the power method (default), and an algebraic method
(optional).  

## Classes

### class Grid

#### constructor

`gridvoting.Grid(x0, x1, xstep=1, y0, y1, ystep=1)`

Constructs a 2D grid in x and y dimenstions and provides helpful methods for accessing the grid.

- `x0` the leftmost grid x-coordinate
- `x1` the rightmost grid x-coordinate
- `xstep=1` optional, default value 1.  grid spacing in x dimenstion
- `y0` the lowest grid y-coordinate
- `y1` the highest grid y-coordinate
- `ystep=1` optional, default value 1.  grid spacing in y dimension

Example:  

```
import gridvoting
grid = gridVoting.Grid(x0=-5,x1=5,y0=-7,y=7)
```

Defines a grid where `-5<=x<=5` and `-7<=y<=7` 

This grid will have `11*15 = 165` alternatives corresponding to integer points in the grid.

Instance Properties:
* parameters from the constructor call are available as instance properties
  - grid.x0
  - grid.x1
  - grid.xstep
  - grid.y0
  - grid.y1
  - grid.ystep
* calculated properties
  - grid.points -- 2D numpy array containing a list of grid points in typewriter order `[[x0,y1],[x0+1,y1],...,[x1,y0]]` 
  - grid.x -- 1D numpy array containing the x-coordinate of each grid point in typewriter order `[x0,...,x0+1,...,x1]`
  - grid.y -- 1D numpy array containing the y-coordinate of each grid point in [y1,...,y1-1,...,y0] typewriter order
  - grid.gshape -- natural shape (number_of_rows,number_of_cols) where rows represent y-axis and cols represent x-axis
  - grid.extent -- equal to the tuple (x0,x1,y0,y1) for use with matplotlib.pyplot.plt
  - grid.len -- equal to the number of points on the grid
  - grid.boundary -- a 1D numpy boolean array, equal to ((grid.x==x0) | (grid.x==x1) | (grid.y==y0) | (grid.y==y1))

#### methods

`grid.as_xy_vectors()`

returns a list of coordiantes `[...,[x,y],...]` for each points on the grid, in typewriter order.

**removed in version 0.60.0, use `grid.points` instead**

----
`grid.embedding(valid, fill=0.0)`

returns an embedding function efunc

efunc maps 1D arrays of size `valid.sum()`
to arrays of size `grid.len`

`valid` is a boolean array of length grid.len used to select the grid points 
associated with the embedded shape.  This can be constructed from conditions
on `grid.x`, `grid.y`, methods `grid.within_box`, `grid.within_disk`, `grid.within_triangle` (see below), 
and appropriate boolean operators.

`fill` is used to set the value in the region where `valid` is `False`.

`fill=np.nan` is useful when used with matplotlib contour plots, as it will cause
the undefined region to be ignored by the plotter rather than set to 0.

Example:

```
import gridvoting
grid = gridVoting.Grid(x0=-5,x1=5,y0=-7,y1=7)
# grid.len == 165
# a boolean array of size grid.len defines a subset of a grid
triangle = (grid.x>=0) & (grid.y>=0) & ((grid.x+grid.y)<=4)
print(triangle.reshape(grid.gshape))
[[False False False False False False False False False False False]
 [False False False False False False False False False False False]
 [False False False False False False False False False False False]
 [False False False False False  True False False False False False]
 [False False False False False  True  True False False False False]
 [False False False False False  True  True  True False False False]
 [False False False False False  True  True  True  True False False]
 [False False False False False  True  True  True  True  True False]
 [False False False False False False False False False False False]
 [False False False False False False False False False False False]
 [False False False False False False False False False False False]
 [False False False False False False False False False False False]
 [False False False False False False False False False False False]
 [False False False False False False False False False False False]
 [False False False False False False False False False False False]]
# you can see the triangle shape in the True's
# you can count the points with sum because False->0 and True->1
print(sum(triangle)) # 15 - the triangle has 15 points on the grid
# [triangle] can now be used as an index to restrict arrays of 165 entries
# down to arrays defined on the triangle with 15 entries
# we can use this to print the (x,y) coordinates for the triangle points
print(grid.points[triangle])
[[0 4]
 [0 3]
 [1 3]
 [0 2]
 [1 2]
 [2 2]
 [0 1]
 [1 1]
 [2 1]
 [3 1]
 [0 0]
 [1 0]
 [2 0]
 [3 0]
 [4 0]]
# grid.embedding creates a function from arrays of 15 entries to arrays of 165 entries
emfunc = grid.embedding(valid=triangle)
triangle_x = grid.x[triangle] # [0 0 1 0 1 2 0 1 2 3 0 1 2 3 4]
# embedding triangle_x into the grid will give a function that is 0 except in the triangle, where it is x
print(emfunc(triangle_x, fill=0.0).reshape(grid.gshape))
[[0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.]
 [0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.]
 [0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.]
 [0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.]
 [0. 0. 0. 0. 0. 0. 1. 0. 0. 0. 0.]
 [0. 0. 0. 0. 0. 0. 1. 2. 0. 0. 0.]
 [0. 0. 0. 0. 0. 0. 1. 2. 3. 0. 0.]
 [0. 0. 0. 0. 0. 0. 1. 2. 3. 4. 0.]
 [0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.]
 [0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.]
 [0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.]
 [0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.]
 [0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.]
 [0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.]
 [0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.]]
```

----
`grid.extremes(z,valid=valid)`

inputs:

`z` is a 1D numpy array of length `valid.sum()`

`valid` is a 1D numpy array of length grid.len indicating which grid points are valid. If `valid` is omitted, all grid points will be considered valid.
  
returns:

  `(min_z,min_z_points,max_z,max_z_points)`

  where `min_z` and `max_z` are the minimum and maximum values of z and

  `min_z_points` and `max_z_points` are arrays of `[x,y]` points where the min and max occur in z.

----
`grid.index(x,y)`

Locates the index in the grid's coordinate array for the point (x,y)

Example:

```
import gridvoting
grid = gridVoting.Grid(x0=-5,x1=5,y0=-7,y1=7)
idx = grid.index(x=-4,y=6)
print(idx)
```

`idx` will be 12, because `[-4,6]` is entry [12] of `grid.points`

----
`grid.plot(title=None, cmap=cm.gray_r, alpha=0.6, alpha_points=0.3, log=True, points=None, zoom=False, border=1, logbias=1e-100, figsize=(10, 10), dpi=72, fname=None)`

Creates a plot 

Explanation Generated by Github Copilot:

takes as input z (a numpy array of size n*m), and optionally a title, a colormap, a transparency, points to plot, whether to zoom, the border to add, the logbias, the figsize, the dpi and the fname, and plots the values z on the grid, optionally plots the points, and optionally zooms to fit the bounding box of the points

----
`grid.shape(x0=None, x1=None, xstep=None, y0=None, y1=None, ystep=None)`

returns a tuple(number_of_rows,number_of_cols) for the natural shape of the current grid, or a subset

----
`grid.spatial_utilities(voter_ideal_points, metric='sqeuclidean', scale=-1)`

returns utility function values for each voter at each grid point as a function of distance from an ideal point

`voter_ideal_points` an array of 2D coordinates [[xv1,yv1],[xv2,yv2],...]  for the ideal points of voters 1,2,...

`metric` the default `sqeuclidean` uses the squared euclidean distance.  `cityblock` uses the taxicab metric.
Internally, this method calls `scipy.spatial.distance.cdist` where the [metrics are listed and documented](https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.distance.cdist.html) 

----
`grid.within_box(x0=None, x1=None, y0=None, y1=None)`

 returns a 1D numpy boolean array, suitable as an index mask, for testing whether a grid point is also in the defined box
     |  

----
`grid.within_disk(x0, y0, r, metric='euclidean', **kwarg)`

 returns 1D numpy boolean array, suitable as an index mask, for testing whether a grid point is also in the defined disk

 ----

 `grid.within_triangle(points)`

`points` should have shape `(3,2)`

 returns 1D numpy boolean array, suitable as an index mask, for testing whether a grid point is also in the defined triangle

----

### class VotingModel
`gridvoting.VotingModel`

#### constructor

```
gridvoting.VotingModel(
        utility_functions,
        number_of_voters,
        number_of_feasible_alternatives,
        majority,
        zi)
```

#### methods

`analyze()`

`what_beats(index)`

`what_is_beaten_by(index)`

```
plots(
      grid,
        voter_ideal_points,
        diagnostics=False,
        log=True,
        embedding=lambda z: z,
        zoomborder=0,
        dpi=72,
        figsize=(10, 10),
        fprefix=None,
        title_core='Core (aborbing) points',
        title_sad='L1 norm of difference in two rows of P^power',
        title_diff1='L1 norm of change in corner row',
        title_diff2='L1 norm of change in center row',
        title_sum1minus1='Corner row sum minus 1.0',
        title_sum2minus1='Center row sum minus 1.0',
        title_unreachable_points='Dominated (unreachable) points',
        title_stationary_distribution_no_grid='Stationary Distribution',
        title_stationary_distribution='Stationary Distribution',
        title_stationary_distribution_zoom='Stationary Distribution (zoom)'
)
```

`_get_transition_matrix()`

### class MarkovChainGPU

#### constructor

`gridvoting.MarkovChainGPU(P, computeNow=True, tolerance=1e-10)`

`P` a valid transition matrix -- should be a square numpy array whose rows all sum to near 1.0 -- this is checked with assert statements

`computeNow=True` boolean - immediately compute Markov Chain properties 

`tolerance=1e-10` float - tolerance for checking rowsums of transition matrix

#### methods

`L1_norm_of_single_step_change(x)`

`solve_for_unit_eigenvector()`

`find_unique_stationary_distribution(tolerance,start_power=2)`




## Other Functions

`assert_valid_transition_matrix(P, *, decimal=10):` is a function definition with one required parameter `P` and one keyword-only parameter `decimal` with a default value of `10`. This function asserts that the matrix `P` is square and that each row sums to 1.0 with a default tolerance of 10 decimal places.

`assert_zero_diagonal_int_matrix(M):` asserts that numpy or cupy array M is square and the diagonal entries are all 0.0 """
