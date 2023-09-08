"""Latin Hypercube Sampling"""

#                                                                       Modules
# =============================================================================

# Standard
from typing import Any

# Third-party
import numpy as np
from SALib.sample import latin

# Locals
from ..design.domain import Domain
from .sampler import Sampler

#                                                          Authorship & Credits
# =============================================================================
__author__ = 'Martin van der Schelling (M.P.vanderSchelling@tudelft.nl)'
__credits__ = ['Martin van der Schelling']
__status__ = 'Stable'
# =============================================================================
#
# =============================================================================


class LatinHypercube(Sampler):
    """Sampling via Latin Hypercube Sampling"""

    def sample_continuous(self, numsamples: int) -> np.ndarray:
        """Sample from continuous space

        Parameters
        ----------
        numsamples
            number of samples

        Returns
        -------
            samples
        """
        continuous = self.design.get_continuous_parameters()
        problem = {
            "num_vars": len(continuous),
            "names": list(continuous.keys()),
            "bounds": [[s.lower_bound, s.upper_bound] for s in continuous.values()],
        }

        samples = latin.sample(problem, N=numsamples, seed=self.seed)
        return samples
