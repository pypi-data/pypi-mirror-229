import pytest
def test_gridvoting_topcycle():
  import gridvoting as gv
  from itertools import permutations
  np = gv.np
  xp = gv.xp
  for perm in permutations(np.arange(6)):
    aperm = np.array(perm)
    u = np.array([
      [1000,900,800,20,10,1],
      [800,1000,900,1,20,10],
      [900,800,1000,10,1,20]
    ])[:,aperm]
    correct_stationary_distribution = np.array([1/3,1/3,1/3,0.,0.,0.])[aperm]
    vm = gv.VotingModel(utility_functions=u,number_of_feasible_alternatives=6,number_of_voters=3,majority=2,zi=False)
    vm.analyze()
    xp.testing.assert_array_almost_equal(
      vm.stationary_distribution,
      correct_stationary_distribution,
      1e-9
    )
    zero_mask = correct_stationary_distribution==0.0
    if vm.stationary_distribution[zero_mask].sum()>0.0:
      raise RuntimeError("lower cycle still positive: "+str(vm.MarkovChain.power_method_diagnostics))
