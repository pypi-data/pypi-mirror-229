# Copyright 2016 Enzo Busseti, Stephen Boyd, Steven Diamond, BlackRock Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""This module implements realistic constraints to be used with
SinglePeriodOptimization and MultiPeriodOptimization policies,
or other Cvxpy-based policies.
"""


import cvxpy as cp
import numpy as np

from .estimator import CvxpyExpressionEstimator, DataEstimator
from .forecast import HistoricalFactorizedCovariance

__all__ = [
    "LongOnly",
    "LeverageLimit",
    "LongCash",
    "DollarNeutral",
    "ParticipationRateLimit",
    "MaxWeights",
    "MinWeights",
    "NoTrade",
    "FactorMaxLimit",
    "FactorMinLimit",
    "FixedFactorLoading",
    "MarketNeutral",
    "MinWeightsAtTimes",
    "MaxWeightsAtTimes",
    "TurnoverLimit",
    "MinCashBalance"
]


class BaseConstraint(CvxpyExpressionEstimator):
    """Base cvxpy constraint class."""


class BaseTradeConstraint(BaseConstraint):
    """Base class for constraints that operate on trades."""

    pass


class EqualityConstraint(BaseConstraint):
    """Base class for equality constraints.

    This class is not exposed to the user, each equality
    constraint inherits from this and overrides the 
    :func:`InequalityConstraint._compile_constr_to_cvxpy` and 
    :func:`InequalityConstraint._rhs` methods.

    We factor this code in order to streamline the
    design of :class:`SoftConstraint` costs.
    """

    def _compile_to_cvxpy(self, w_plus, z, w_plus_minus_w_bm):
        "Compile constraint to cvxpy."
        return self._compile_constr_to_cvxpy(w_plus, z, w_plus_minus_w_bm) == \
            self._rhs()

    def _compile_constr_to_cvxpy(self, w_plus, z, w_plus_minus_w_bm):
        """Cvxpy expression of the left-hand side of the constraint.        
        """
        raise NotImplementedError

    def _rhs(self):
        """Cvxpy expression of the right-hand side of the constraint.        
        """
        raise NotImplementedError


class InequalityConstraint(BaseConstraint):
    """Base class for inequality constraints.

    This class is not exposed to the user, each inequality
    constraint inherits from this and overrides the 
    :func:`InequalityConstraint._compile_constr_to_cvxpy` and 
    :func:`InequalityConstraint._rhs` methods.

    We factor this code in order to streamline the
    design of :class:`SoftConstraint` costs.
    """

    def _compile_to_cvxpy(self, w_plus, z, w_plus_minus_w_bm):
        "Compile constraint to cvxpy."
        return self._compile_constr_to_cvxpy(w_plus, z, w_plus_minus_w_bm) <= \
            self._rhs()

    def _compile_constr_to_cvxpy(self, w_plus, z, w_plus_minus_w_bm):
        """Cvxpy expression of the left-hand side of the constraint.        
        """
        raise NotImplementedError

    def _rhs(self):
        """Cvxpy expression of the right-hand side of the constraint.        
        """
        raise NotImplementedError


class CostInequalityConstraint(InequalityConstraint):
    """Linear inequality constraint applied to a cost term.

    The user does not interact with this class directly,
    it is returned by an expression such as `cost <= value`
    where `cost` is a :class:`BaseCost` instance and `value`
    is a scalar.
    """

    def __init__(self, cost, value):
        self.cost = cost
        self.value = DataEstimator(value, compile_parameter=True)

    def _compile_constr_to_cvxpy(self, w_plus, z, w_plus_minus_w_bm):
        "Compile constraint to cvxpy."
        return self.cost._compile_to_cvxpy(w_plus, z, w_plus_minus_w_bm)

    def _rhs(self):
        return self.value.parameter

    def __repr__(self):
        return self.cost.__repr__() + ' <= ' + self.value.__repr__()


class BaseWeightConstraint(BaseConstraint):
    """Base class for constraints that operate on weights.

    Here we can implement a method to pass benchmark weights
    and make the constraint relative to it rather than to the null
    portfolio.
    """


class MarketNeutral(BaseWeightConstraint, EqualityConstraint):
    """Initial implementation of market neutrality.

    The benchmark portfolio weights are computed here
    (weighting by rolling averages of the market volumes)
    but instead should be their own class (used as well
    by risk models, ...).
    """

    def __init__(self):
        self.covarianceforecaster = HistoricalFactorizedCovariance()

    def _pre_evaluation(self, universe, backtest_times):
        self.market_vector = cp.Parameter(len(universe)-1)

    def _values_in_time(self, t, past_volumes, past_returns, **kwargs):
        tmp = past_volumes.iloc[-250:].mean()
        tmp /= sum(tmp)

        tmp2 = self.covarianceforecaster.current_value @ (
            self.covarianceforecaster.current_value.T @ tmp)
        # print(tmp2)
        self.market_vector.value = np.array(tmp2)

    def _compile_constr_to_cvxpy(self, w_plus, z, w_plus_minus_w_bm):
        "Compile left hand side of the constraint expression."
        return w_plus[:-1].T @ self.market_vector

    def _rhs(self):
        "Compile right hand side of the constraint expression."
        return 0


class TurnoverLimit(BaseTradeConstraint, InequalityConstraint):
    """Turnover limit as a fraction of the portfolio value.

    See page 37 of the book.

    :param delta: constant or changing in time turnover limit
    :type delta: float or pd.Series
    """

    def __init__(self, delta):
        self.delta = DataEstimator(delta, compile_parameter=True)

    def _compile_constr_to_cvxpy(self, w_plus, z, w_plus_minus_w_bm):
        "Compile left hand side of the constraint expression."
        return .5 * cp.norm1(z[:-1])

    def _rhs(self):
        "Compile right hand side of the constraint expression."
        return self.delta.parameter


class ParticipationRateLimit(BaseTradeConstraint, InequalityConstraint):
    """A limit on maximum trades size as a fraction of market volumes.


    :param volumes: per-stock and per-day market volume estimates, or constant
        in time
    :type volumes: pd.Series or pd.DataFrame
    :param max_fraction_of_volumes: max fraction of market volumes that we're
        allowed to trade
    :type max_fraction_of_volumes: float, pd.Series, pd.DataFrame
    """

    def __init__(self, volumes, max_fraction_of_volumes=0.05):
        self.volumes = DataEstimator(volumes, compile_parameter=True)
        self.max_participation_rate = DataEstimator(
            max_fraction_of_volumes, compile_parameter=True)
        self.portfolio_value = cp.Parameter(nonneg=True)

    def _values_in_time(self, current_portfolio_value, **kwargs):
        self.portfolio_value.value = current_portfolio_value

    def _compile_constr_to_cvxpy(self, w_plus, z, w_plus_minus_w_bm):
        "Compile left hand side of the constraint expression."
        return cp.multiply(cp.abs(z[:-1]), self.portfolio_value)

    def _rhs(self):
        "Compile right hand side of the constraint expression."
        return cp.multiply(self.volumes.parameter, self.max_participation_rate.parameter)


class LongOnly(BaseWeightConstraint, InequalityConstraint):
    """A long only constraint.

    Imposes that at each point in time the post-trade
    weights are non-negative.

    """

    def _compile_constr_to_cvxpy(self, w_plus, z, w_plus_minus_w_bm):
        """Return a Cvxpy constraint."""
        return -w_plus[:-1]

    def _rhs(self):
        "Compile right hand side of the constraint expression."
        return 0


class NoTrade(BaseTradeConstraint):
    """No-trade condition on name on periods(s)."""

    def __init__(self, asset, periods):
        self.asset = asset
        self.periods = periods

    def _pre_evaluation(self, universe, backtest_times):
        self.index = (universe.get_loc if hasattr(
            universe, 'get_loc') else universe.index)(self.asset)
        self.low = cp.Parameter()
        self.high = cp.Parameter()

    def _values_in_time(self, t, **kwargs):
        if t in self.periods:
            self.low.value = 0.
            self.high.value = 0.
        else:
            self.low.value = -100.
            self.high.value = +100.

    def _compile_to_cvxpy(self, w_plus, z, w_plus_minus_w_bm):
        return [z[self.index] >= self.low,
                z[self.index] <= self.high]


class LeverageLimit(BaseWeightConstraint, InequalityConstraint):
    """A limit on leverage.

    Leverage is defined as the :math:`\ell_1` norm of non-cash
    post-trade weights. Here we require that it is smaller than
    a given value.

    :param limit: constant or varying in time leverage limit
    :type limit: float or pd.Series
    """

    def __init__(self, limit):
        self.limit = DataEstimator(limit, compile_parameter=True)

    def _compile_constr_to_cvxpy(self, w_plus, z, w_plus_minus_w_bm):
        "Compile left hand side of the constraint expression."
        return cp.norm(w_plus[:-1], 1)

    def _rhs(self):
        "Compile right hand side of the constraint expression."
        return self.limit.parameter


class MinCashBalance(BaseWeightConstraint):
    """Requires that the cash account is larger than c_min dollars.

    This uses logic to subtract cash used as margin for the short
    positions that is not documented in the book but is
    equivalent to the book definition's for long-only stock positions.
    """

    def __init__(self, c_min):
        self.c_min = DataEstimator(c_min)
        self.rhs = cp.Parameter()

    def _values_in_time(self, current_portfolio_value, **kwargs):
        self.rhs.value = self.c_min.current_value/current_portfolio_value

    def _compile_to_cvxpy(self, w_plus, z, w_plus_minus_w_bm):
        """Return a Cvxpy constraint."""
        # TODO clarify this
        realcash = (w_plus[-1] - 2 * cp.sum(cp.neg(w_plus[:-1])))
        return realcash >= self.rhs


class LongCash(MinCashBalance):
    """Requires that cash be non-negative."""

    def __init__(self):
        super().__init__(0.)


class DollarNeutral(BaseWeightConstraint, EqualityConstraint):
    """Long-short dollar neutral strategy."""

    def _compile_constr_to_cvxpy(self, w_plus, z, w_plus_minus_w_bm):
        "Compile left hand side of the constraint expression."
        return w_plus[-1]

    def _rhs(self):
        "Compile right hand side of the constraint expression."
        return 1


class MaxWeights(BaseWeightConstraint, InequalityConstraint):
    """A max limit on weights.

    Attributes:
      limit: A series or number giving the weights limit.
    """

    def __init__(self, limit):
        self.limit = DataEstimator(limit, compile_parameter=True)

    def _compile_constr_to_cvxpy(self, w_plus, z, w_plus_minus_w_bm):
        "Compile left hand side of the constraint expression."
        return w_plus[:-1]

    def _rhs(self):
        "Compile right hand side of the constraint expression."
        return self.limit.parameter


class MinWeights(BaseWeightConstraint, InequalityConstraint):
    """A min limit on weights.

    Attributes:
      limit: A series or number giving the weights limit.
    """

    def __init__(self, limit):
        self.limit = DataEstimator(limit, compile_parameter=True)

    def _compile_constr_to_cvxpy(self, w_plus, z, w_plus_minus_w_bm):
        "Compile left hand side of the constraint expression."
        return -w_plus[:-1]

    def _rhs(self):
        "Compile right hand side of the constraint expression."
        return -self.limit.parameter


class MinMaxWeightsAtTimes(BaseWeightConstraint):

    def __init__(self, limit, times):
        self.base_limit = limit
        self.times = times

    def _pre_evaluation(self, universe, backtest_times):
        self.backtest_times = backtest_times
        self.limit = cp.Parameter()

    def _values_in_time(self, t, mpo_step, **kwargs):
        tidx = self.backtest_times.get_loc(t)
        nowtidx = tidx + mpo_step
        if (nowtidx < len(self.backtest_times)) and \
                (self.backtest_times[nowtidx] in self.times):
            self.limit.value = self.base_limit
        else:
            self.limit.value = 100 * self.sign


class MinWeightsAtTimes(MinMaxWeightsAtTimes, InequalityConstraint):

    sign = -1.  # used in _values_in_time of parent class

    def _compile_constr_to_cvxpy(self, w_plus, z, w_plus_minus_w_bm):
        "Compile left hand side of the constraint expression."
        return -w_plus[:-1]

    def _rhs(self):
        "Compile right hand side of the constraint expression."
        return -self.limit


class MaxWeightsAtTimes(MinMaxWeightsAtTimes, InequalityConstraint):

    sign = 1.  # used in _values_in_time of parent class

    def _compile_constr_to_cvxpy(self, w_plus, z, w_plus_minus_w_bm):
        "Compile left hand side of the constraint expression."
        return w_plus[:-1]

    def _rhs(self):
        "Compile right hand side of the constraint expression."
        return self.limit


class FactorMaxLimit(BaseWeightConstraint, InequalityConstraint):
    """A max limit on portfolio-wide factor (e.g. beta) exposure.

    :param factor_exposure: Series or DataFrame giving the factor exposure.
        If Series it is indexed by assets' names and represents factor
        exposures constant in time. If DataFrame it is indexed by time 
        and has the assets names as columns, and it represents factor 
        exposures that change in time. In the latter case an observation
        must be present for every point in time of a backtest.
        If you want you can also pass multiple factor exposures at once:
        as a dataframe indexed by assets' names and whose columns are the
        factors (if constant in time), or a dataframe with multiindex: 
        first level is time, second level are assets' names (if changing 
        in time). However this latter usecase is probably better served
        by making multiple instances of this constraint, one for each 
        factor.
    :type factor_exposure: pd.Series or pd.DataFrame
    :param limit: Factor limit, either constant or varying in time. Use
        a DataFrame if you pass multiple factors as once.
    :type limit: float or pd.Series or pd.DataFrame
    """

    def __init__(self, factor_exposure, limit):
        self.factor_exposure = DataEstimator(
            factor_exposure, compile_parameter=True)
        self.limit = DataEstimator(limit, compile_parameter=True, 
            ignore_shape_check=True)

    def _compile_constr_to_cvxpy(self, w_plus, z, w_plus_minus_w_bm):
        "Compile left hand side of the constraint expression."
        return self.factor_exposure.parameter.T @ w_plus[:-1]

    def _rhs(self):
        "Compile right hand side of the constraint expression."
        return self.limit.parameter


class FactorMinLimit(BaseWeightConstraint, InequalityConstraint):
    """A min limit on portfolio-wide factor (e.g. beta) exposure.

    :param factor_exposure: Series or DataFrame giving the factor exposure.
        If Series it is indexed by assets' names and represents factor
        exposures constant in time. If DataFrame it is indexed by time 
        and has the assets names as columns, and it represents factor 
        exposures that change in time. In the latter case an observation
        must be present for every point in time of a backtest.
        If you want you can also pass multiple factor exposures at once:
        as a dataframe indexed by assets' names and whose columns are the
        factors (if constant in time), or a dataframe with multiindex: 
        first level is time, second level are assets' names (if changing 
        in time). However this latter usecase is probably better served
        by making multiple instances of this constraint, one for each 
        factor.
    :type factor_exposure: pd.Series or pd.DataFrame
    :param limit: Factor limit, either constant or varying in time. Use
        a DataFrame if you pass multiple factors as once.
    :type limit: float or pd.Series or pd.DataFrame
    """

    def __init__(self, factor_exposure, limit):
        self.factor_exposure = DataEstimator(
            factor_exposure, compile_parameter=True)
        self.limit = DataEstimator(limit, compile_parameter=True,
            ignore_shape_check=True)

    def _compile_constr_to_cvxpy(self, w_plus, z, w_plus_minus_w_bm):
        "Compile left hand side of the constraint expression."
        return -self.factor_exposure.parameter.T @ w_plus[:-1]

    def _rhs(self):
        "Compile right hand side of the constraint expression."
        return -self.limit.parameter


class FixedFactorLoading(BaseWeightConstraint, EqualityConstraint):
    """A constraint to fix portfolio loadings to a set of factors.

    This can be used to impose market neutrality, 
    a certain portfolio-wide alpha, ....

    :param factor_exposure: Series or DataFrame giving the factor exposure.
        If Series it is indexed by assets' names and represents factor
        exposures constant in time. If DataFrame it is indexed by time 
        and has the assets names as columns, and it represents factor 
        exposures that change in time. In the latter case an observation
        must be present for every point in time of a backtest.
        If you want you can also pass multiple factor exposures at once:
        as a dataframe indexed by assets' names and whose columns are the
        factors (if constant in time), or a dataframe with multiindex: 
        first level is time, second level are assets' names (if changing 
        in time). However this latter usecase is probably better served
        by making multiple instances of this constraint, one for each 
        factor.
    :type factor_exposure: pd.Series or pd.DataFrame
    :param target: Target portfolio factor exposures, 
        either constant or varying in time. Use
        a DataFrame if you pass multiple factors as once.
    :type target: float or pd.Series or pd.DataFrame
    """

    def __init__(self, factor_exposure, target):
        self.factor_exposure = DataEstimator(
            factor_exposure, compile_parameter=True)
        self.target = DataEstimator(target, compile_parameter=True)

    def _compile_constr_to_cvxpy(self, w_plus, z, w_plus_minus_w_bm):
        "Compile left hand side of the constraint expression."
        return self.factor_exposure.parameter.T @ w_plus[:-1]

    def _rhs(self):
        "Compile right hand side of the constraint expression."
        return self.target.parameter
