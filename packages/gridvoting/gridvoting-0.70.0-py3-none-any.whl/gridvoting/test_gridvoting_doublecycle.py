import pytest


@pytest.fixture
def double_cycle_mc():
  import gridvoting as gv
  xp = gv.xp
  double_cycle_P = xp.array([
    [1/2,1/2,0,0,0,0],
    [0,1/2,1/2,0,0,0],
    [1/2,0,1/2,0,0,0],
    [0,0,0,1/2,1/2,0],
    [0,0,0,0,1/2,1/2],
    [0,0,0,1/2,0,1/2]
  ])
  mc = gv.MarkovChainCPUGPU(P=double_cycle_P,computeNow=False)
  return mc
  
def test_gridvoting_doublecycle_power(double_cycle_mc):
  with pytest.raises(RuntimeError) as e_info:
    double_cycle_mc.find_unique_stationary_distribution(tolerance=1e-10)

def test_gridvoting_doublecycle_algebra(double_cycle_mc):
  with pytest.raises(RuntimeError) as e_info:
    double_cycle_mc.solve_for_unit_eigenvector()
      
