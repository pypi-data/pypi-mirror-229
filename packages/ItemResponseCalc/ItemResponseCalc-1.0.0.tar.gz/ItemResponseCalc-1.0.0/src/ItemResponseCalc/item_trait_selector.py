"""Classes to handle mapping between questionnaire items and latent traits

*** Main Classes:
TraitSelector: Probability distribution of a one-of-D boolean switch array
TraitProb: Distribution of prior probability mass vector for any TraitSelector object

*** Version history:
* Version 0.6 - 1.0.0: no changes
"""
# *** join item_trait_sel and trait_prob into ONE class ? ***
import numpy as np
from scipy.special import gammaln, psi, softmax

# ----------------------------------------------------------
PRIOR_TRAIT_CONCENTRATION = 0.001
# = global_pop concentration parameters for TraitProb Dirichlet distribution


# ----------------------------------------------------------
class TraitSelector:
    """Probability distribution of a one-of-D boolean array
    z = (z_1, ..., z_D) with only ONE element z_d == True,
    indicating that responses to this item are determined by the d-th trait.
    """
    def __init__(self, weight):
        """
        :param weight: 1D array with un-normalized probability mass elements
        """
        weight = np.array(weight)
        self.prob = weight / np.sum(weight)

    @classmethod
    def initialize(cls, n_traits):
        return cls(np.ones(n_traits))

    @property
    def mean(self):
        return self.prob

    @property
    def bool(self):
        """
        :return: one-of-K boolean array
        """
        b = np.full(len(self.prob), False)
        b[np.argmax(self.prob)] = True
        return b

    def adapt(self, log_responsibility, prior):
        """Adapt self.prob for given trait responsibility
        :param log_responsibility: 1D array with sum logprob(responses) given each trait
        :param prior: single TraitProb object
        :return: - KLdiv(self || prior)
        """
        log_r = log_responsibility + prior.mean_log
        self.prob = softmax(log_r)  # r / np.sum(r); r = exp(log_r)
        return - self.relative_entropy_re_prior(prior)

    def relative_entropy_re_prior(self, prior):
        """KL div = E_{z, w}{ log q(z) / p(z | w) }
        :param prior: single TraitProb object
        :return: scalar KL-div

        Method:
        q(z) = prod_t r_t^{z_t};
        p(z | w) = prod_t w_t^{z_t}
        where r = self.prob; w = prior Dirichlet-distributed probability parameter
        """
        eps = np.finfo(float).tiny  # just to handle 0 * log(0.) -> 0
        return np.dot(self.prob, np.log(self.prob + eps) - prior.mean_log)

    def prune(self, keep):
        """Prune away un-necessary trait dimensions
        :param keep: 1D boolean array indicating traits to keep
        :return: None
        Result: self.prob reduced, and still normalized
        """
        w = self.prob[keep]
        self.prob = w / np.sum(w)


# ---------------------------------------------------------------------------
class TraitProb:
    """Distribution of hierarchical prior probability mass for all TraitSelector objects,
    modeled as a single Dirichlet distribution.
    """
    @classmethod
    def initialize(cls, n_traits):
        """Create prior trait probability distribution
        :param n_traits: scalar integer number of traits
        :return: single initialized TraitProb object
        """
        alpha = PRIOR_TRAIT_CONCENTRATION * np.ones(n_traits)
        # *** decreasing alpha by trait index ?
        # *** NO, initial PCA trait rotation is enough
        return cls(alpha)

    def __init__(self, alpha):
        self.alpha=np.array(alpha)

    def __repr__(self):
        return (self.__class__.__name__
                + '(' + f'alpha= ' + repr(self.alpha) + ')')

    @property
    def mean(self):
        return self.alpha / np.sum(self.alpha)

    @property
    def mean_log(self):
        """E{ log W } where W is random vector represented by self"""
        return psi(self.alpha) - psi(np.sum(self.alpha))

    def adapt(self, trait_sel):
        """Adapt from given trait-selector instances,
        by updating concentration parameters of Dirichlet distribution
        represented by self.
        :param trait_sel: array-like list of trait selector objects
        :return: - kl_div

        Method: doc sec:PosteriorZW eq:PosteriorW
            self is an updated
        """
        self.alpha = sum(s.mean for s in trait_sel) + self.initialize(len(self.alpha)).alpha
        return - self.relative_entropy_re_prior()

    def relative_entropy_re_prior(self):
        """KL_div = E{ log q(w) / p(w) }_{q(w}), where
        q(w) = self distribution; p(w) = self.initialize
        :return: scalar KL_div
        Method:
        q(w) = C(q_alpha) prod_t w_t^{q_alpha - 1}
        p(w) = C(p_alpha) prod_t w_t^{p_alpha - 1}
        C(alpha) = log(gamma(sum alpha)) - sum log(gamma(alpha))
        """
        p = self.initialize(len(self.alpha))
        # = global_pop
        kl_div = (np.dot(self.alpha - p.alpha, self.mean_log)
                  + gammaln(np.sum(self.alpha)) - gammaln(np.sum(p.alpha))
                  + np.sum(gammaln(p.alpha) - gammaln(self.alpha)))
        return kl_div

    def prune(self, keep):
        """Prune away un-necessary trait dimensions
        :param keep: 1D boolean array indicating traits to keep
        :return: None
        Result: self.trait_sel pruned
        """
        self.alpha = self.alpha[keep]
