import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from diversity_facets import (
    coverage_density,
    g_function,
    l2_normalize,
    mmd2_rbf,
    participation_ratio,
    vendi_scores,
    wasserstein_ot,
)


class DiversityFacetToyTests(unittest.TestCase):
    def test_clustered_cloud_has_lower_richness_and_dimensionality(self):
        rng = np.random.default_rng(7)
        spread = l2_normalize(rng.normal(size=(24, 32)))
        centers = l2_normalize(rng.normal(size=(3, 32)))
        clustered = np.vstack([centers[i % 3] + 0.02 * rng.normal(size=32) for i in range(24)])
        clustered = l2_normalize(clustered)

        self.assertGreater(vendi_scores(spread, (1,))[1], vendi_scores(clustered, (1,))[1])
        self.assertGreater(participation_ratio(spread), participation_ratio(clustered))

    def test_clustered_cloud_shifts_g_function_left(self):
        rng = np.random.default_rng(11)
        spread = l2_normalize(rng.normal(size=(24, 24)))
        center = l2_normalize(rng.normal(size=(1, 24)))
        clustered = l2_normalize(center + 0.03 * rng.normal(size=(24, 24)))
        radii = np.linspace(0.01, 0.4, 12)

        self.assertGreater(g_function(clustered, radii).mean(), g_function(spread, radii).mean())

    def test_coverage_and_displacement_are_bounded_or_nonnegative(self):
        rng = np.random.default_rng(13)
        ref = l2_normalize(rng.normal(size=(20, 16)))
        gen = l2_normalize(ref[:20] + 0.05 * rng.normal(size=(20, 16)))
        cov = coverage_density(ref, gen, k=3)

        self.assertGreaterEqual(cov["coverage"], 0.0)
        self.assertLessEqual(cov["coverage"], 1.0)
        self.assertGreaterEqual(cov["density"], 0.0)
        self.assertGreaterEqual(mmd2_rbf(ref, gen), -1e-9)
        self.assertGreaterEqual(wasserstein_ot(ref, gen), 0.0)


if __name__ == "__main__":
    unittest.main()
