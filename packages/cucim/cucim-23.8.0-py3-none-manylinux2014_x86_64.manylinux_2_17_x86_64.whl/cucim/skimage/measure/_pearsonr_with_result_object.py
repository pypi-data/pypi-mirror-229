"""Implementation of cupyx.scipy.stats.pearsonr (currently missing in CuPy)

Largely copy-paste of the implementation in scipy/stats/_stats_py.py, just
switching numpy->cupy.
"""
import sys as _sys
from collections import namedtuple
from keyword import iskeyword as _iskeyword

import cupy as cp
from cupyx.scipy import special


def _pearsonr_fisher_ci(r, n, confidence_level, alternative):
    """
    Compute the confidence interval for Pearson's R.

    Fisher's transformation is used to compute the confidence interval
    (https://en.wikipedia.org/wiki/Fisher_transformation).
    """
    if r == 1:
        zr = cp.inf
    elif r == -1:
        zr = -cp.inf
    else:
        zr = cp.arctanh(r)

    if n > 3:
        se = cp.sqrt(1 / (n - 3))
        if alternative == "two-sided":
            h = special.ndtri(0.5 + confidence_level/2)
            zlo = zr - h*se
            zhi = zr + h*se
            rlo = cp.tanh(zlo)
            rhi = cp.tanh(zhi)
        elif alternative == "less":
            h = special.ndtri(confidence_level)
            zhi = zr + h*se
            rhi = cp.tanh(zhi)
            rlo = -1.0
        else:
            # alternative == "greater":
            h = special.ndtri(confidence_level)
            zlo = zr - h*se
            rlo = cp.tanh(zlo)
            rhi = 1.0
    else:
        rlo, rhi = -1.0, 1.0

    return ConfidenceInterval(low=rlo, high=rhi)


def _validate_names(typename, field_names, extra_field_names):
    """
    Ensure that all the given names are valid Python identifiers that
    do not start with '_'.  Also check that there are no duplicates
    among field_names + extra_field_names.
    """
    for name in [typename] + field_names + extra_field_names:
        if type(name) is not str:
            raise TypeError('typename and all field names must be strings')
        if not name.isidentifier():
            raise ValueError('typename and all field names must be valid '
                             f'identifiers: {name!r}')
        if _iskeyword(name):
            raise ValueError('typename and all field names cannot be a '
                             f'keyword: {name!r}')

    seen = set()
    for name in field_names + extra_field_names:
        if name.startswith('_'):
            raise ValueError('Field names cannot start with an underscore: '
                             f'{name!r}')
        if name in seen:
            raise ValueError(f'Duplicate field name: {name!r}')
        seen.add(name)


# Note: This code is adapted from CPython:Lib/collections/__init__.py
#       This version was copied from scipy/_lib/_bunch.py
def _make_tuple_bunch(typename, field_names, extra_field_names=None,
                      module=None):
    """
    Create a namedtuple-like class with additional attributes.

    This function creates a subclass of tuple that acts like a namedtuple
    and that has additional attributes.

    The additional attributes are listed in `extra_field_names`.  The
    values assigned to these attributes are not part of the tuple.

    The reason this function exists is to allow functions in SciPy
    that currently return a tuple or a namedtuple to returned objects
    that have additional attributes, while maintaining backwards
    compatibility.

    This should only be used to enhance *existing* functions in SciPy.
    New functions are free to create objects as return values without
    having to maintain backwards compatibility with an old tuple or
    namedtuple return value.

    Parameters
    ----------
    typename : str
        The name of the type.
    field_names : list of str
        List of names of the values to be stored in the tuple. These names
        will also be attributes of instances, so the values in the tuple
        can be accessed by indexing or as attributes.  At least one name
        is required.  See the Notes for additional restrictions.
    extra_field_names : list of str, optional
        List of names of values that will be stored as attributes of the
        object.  See the notes for additional restrictions.

    Returns
    -------
    cls : type
        The new class.

    Notes
    -----
    There are restrictions on the names that may be used in `field_names`
    and `extra_field_names`:

    * The names must be unique--no duplicates allowed.
    * The names must be valid Python identifiers, and must not begin with
      an underscore.
    * The names must not be Python keywords (e.g. 'def', 'and', etc., are
      not allowed).

    Examples
    --------
    >>> from scipy._lib._bunch import _make_tuple_bunch

    Create a class that acts like a namedtuple with length 2 (with field
    names `x` and `y`) that will also have the attributes `w` and `beta`:

    >>> Result = _make_tuple_bunch('Result', ['x', 'y'], ['w', 'beta'])

    `Result` is the new class.  We call it with keyword arguments to create
    a new instance with given values.

    >>> result1 = Result(x=1, y=2, w=99, beta=0.5)
    >>> result1
    Result(x=1, y=2, w=99, beta=0.5)

    `result1` acts like a tuple of length 2:

    >>> len(result1)
    2
    >>> result1[:]
    (1, 2)

    The values assigned when the instance was created are available as
    attributes:

    >>> result1.y
    2
    >>> result1.beta
    0.5
    """
    if len(field_names) == 0:
        raise ValueError('field_names must contain at least one name')

    if extra_field_names is None:
        extra_field_names = []
    _validate_names(typename, field_names, extra_field_names)

    typename = _sys.intern(str(typename))
    field_names = tuple(map(_sys.intern, field_names))
    extra_field_names = tuple(map(_sys.intern, extra_field_names))

    all_names = field_names + extra_field_names
    arg_list = ', '.join(field_names)
    full_list = ', '.join(all_names)
    repr_fmt = ''.join(('(',
                        ', '.join(f'{name}=%({name})r' for name in all_names),
                        ')'))
    tuple_new = tuple.__new__
    _dict, _tuple, _zip = dict, tuple, zip

    # Create all the named tuple methods to be added to the class namespace

    s = f"""\
def __new__(_cls, {arg_list}, **extra_fields):
    return _tuple_new(_cls, ({arg_list},))

def __init__(self, {arg_list}, **extra_fields):
    for key in self._extra_fields:
        if key not in extra_fields:
            raise TypeError("missing keyword argument '%s'" % (key,))
    for key, val in extra_fields.items():
        if key not in self._extra_fields:
            raise TypeError("unexpected keyword argument '%s'" % (key,))
        self.__dict__[key] = val

def __setattr__(self, key, val):
    if key in {repr(field_names)}:
        raise AttributeError("can't set attribute %r of class %r"
                             % (key, self.__class__.__name__))
    else:
        self.__dict__[key] = val
"""
    del arg_list
    namespace = {'_tuple_new': tuple_new,
                 '__builtins__': dict(TypeError=TypeError,
                                      AttributeError=AttributeError),
                 '__name__': f'namedtuple_{typename}'}
    exec(s, namespace)
    __new__ = namespace['__new__']
    __new__.__doc__ = f'Create new instance of {typename}({full_list})'
    __init__ = namespace['__init__']
    __init__.__doc__ = f'Instantiate instance of {typename}({full_list})'
    __setattr__ = namespace['__setattr__']

    def __repr__(self):
        'Return a nicely formatted representation string'
        return self.__class__.__name__ + repr_fmt % self._asdict()

    def _asdict(self):
        'Return a new dict which maps field names to their values.'
        out = _dict(_zip(self._fields, self))
        out.update(self.__dict__)
        return out

    def __getnewargs_ex__(self):
        'Return self as a plain tuple.  Used by copy and pickle.'
        return _tuple(self), self.__dict__

    # Modify function metadata to help with introspection and debugging
    for method in (__new__, __repr__, _asdict, __getnewargs_ex__):
        method.__qualname__ = f'{typename}.{method.__name__}'

    # Build-up the class namespace dictionary
    # and use type() to build the result class
    class_namespace = {
        '__doc__': f'{typename}({full_list})',
        '_fields': field_names,
        '__new__': __new__,
        '__init__': __init__,
        '__repr__': __repr__,
        '__setattr__': __setattr__,
        '_asdict': _asdict,
        '_extra_fields': extra_field_names,
        '__getnewargs_ex__': __getnewargs_ex__,
    }
    for index, name in enumerate(field_names):

        def _get(self, index=index):
            return self[index]
        class_namespace[name] = property(_get)
    for name in extra_field_names:

        def _get(self, name=name):
            return self.__dict__[name]
        class_namespace[name] = property(_get)

    result = type(typename, (tuple,), class_namespace)

    # For pickling to work, the __module__ variable needs to be set to the
    # frame where the named tuple is created.  Bypass this step in environments
    # where sys._getframe is not defined (Jython for example) or sys._getframe
    # is not defined for arguments greater than 0 (IronPython), or where the
    # user has specified a particular module.
    if module is None:
        try:
            module = _sys._getframe(1).f_globals.get('__name__', '__main__')
        except (AttributeError, ValueError):
            pass
    if module is not None:
        result.__module__ = module
        __new__.__module__ = module

    return result


ConfidenceInterval = namedtuple('ConfidenceInterval', ['low', 'high'])

PearsonRResultBase = _make_tuple_bunch('PearsonRResultBase',
                                       ['statistic', 'pvalue'], [])


class PearsonRResult(PearsonRResultBase):
    """
    Result of `scipy.stats.pearsonr`

    Attributes
    ----------
    statistic : float
        Pearson product-moment correlation coefficent.
    pvalue : float
        The p-value associated with the chosen alternative.

    Methods
    -------
    confidence_interval
        Computes the confidence interval of the correlation
        coefficient `statistic` for the given confidence level.

    """
    def __init__(self, statistic, pvalue, alternative, n):
        super().__init__(statistic, pvalue)
        self._alternative = alternative
        self._n = n

    def confidence_interval(self, confidence_level=0.95):
        """
        The confidence interval for the correlation coefficient.

        Compute the confidence interval for the correlation coefficient
        ``statistic`` with the given confidence level.

        The confidence interval is computed using the Fisher transformation
        F(r) = arctanh(r) [1]_.  When the sample pairs are drawn from a
        bivariate normal distribution, F(r) approximately follows a normal
        distribution with standard error ``1/sqrt(n - 3)``, where ``n`` is the
        length of the original samples along the calculation axis. When
        ``n <= 3``, this approximation does not yield a finite, real standard
        error, so we define the confidence interval to be -1 to 1.

        Parameters
        ----------
        confidence_level : float
            The confidence level for the calculation of the correlation
            coefficient confidence interval. Default is 0.95.

        Returns
        -------
        ci : namedtuple
            The confidence interval is returned in a ``namedtuple`` with
            fields `low` and `high`.

        References
        ----------
        .. [1] "Pearson correlation coefficient", Wikipedia,
               https://en.wikipedia.org/wiki/Pearson_correlation_coefficient
        """
        return _pearsonr_fisher_ci(self.statistic, self._n, confidence_level,
                                   self._alternative)


class PearsonRConstantInputWarning(RuntimeWarning):
    """Warning generated by `pearsonr` when an input is constant."""

    def __init__(self, msg=None):
        if msg is None:
            msg = ("An input array is constant; the correlation coefficient "
                   "is not defined.")
        self.args = (msg,)


class PearsonRNearConstantInputWarning(RuntimeWarning):
    """Warning generated by `pearsonr` when an input is nearly constant."""

    def __init__(self, msg=None):
        if msg is None:
            msg = ("An input array is nearly constant; the computed "
                   "correlation coefficient may be inaccurate.")
        self.args = (msg,)


# Note: this is scipy.stats._stats_py.pearsonr
def pearsonr(x, y, *, alternative='two-sided'):
    r"""
    Pearson correlation coefficient and p-value for testing non-correlation.

    The Pearson correlation coefficient [1]_ measures the linear relationship
    between two datasets. Like other correlation
    coefficients, this one varies between -1 and +1 with 0 implying no
    correlation. Correlations of -1 or +1 imply an exact linear relationship.
    Positive correlations imply that as x increases, so does y. Negative
    correlations imply that as x increases, y decreases.

    This function also performs a test of the null hypothesis that the
    distributions underlying the samples are uncorrelated and normally
    distributed. (See Kowalski [3]_
    for a discussion of the effects of non-normality of the input on the
    distribution of the correlation coefficient.)
    The p-value roughly indicates the probability of an uncorrelated system
    producing datasets that have a Pearson correlation at least as extreme
    as the one computed from these datasets.

    Parameters
    ----------
    x : (N,) array_like
        Input array.
    y : (N,) array_like
        Input array.
    alternative : {'two-sided', 'greater', 'less'}, optional
        Defines the alternative hypothesis. Default is 'two-sided'.
        The following options are available:

        * 'two-sided': the correlation is nonzero
        * 'less': the correlation is negative (less than zero)
        * 'greater':  the correlation is positive (greater than zero)

        .. versionadded:: 1.9.0

    Returns
    -------
    result : `~scipy.stats._result_classes.PearsonRResult`
        An object with the following attributes:

        statistic : float
            Pearson product-moment correlation coefficent.
        pvalue : float
            The p-value associated with the chosen alternative.

        The object has the following method:

        confidence_interval(confidence_level=0.95)
            This method computes the confidence interval of the correlation
            coefficient `statistic` for the given confidence level.
            The confidence interval is returned in a ``namedtuple`` with
            fields `low` and `high`.  See the Notes for more details.

    Warns
    -----
    PearsonRConstantInputWarning
        Raised if an input is a constant array.  The correlation coefficient
        is not defined in this case, so ``cp.nan`` is returned.

    PearsonRNearConstantInputWarning
        Raised if an input is "nearly" constant.  The array ``x`` is considered
        nearly constant if ``norm(x - mean(x)) < 1e-13 * abs(mean(x))``.
        Numerical errors in the calculation ``x - mean(x)`` in this case might
        result in an inaccurate calculation of r.

    See Also
    --------
    spearmanr : Spearman rank-order correlation coefficient.
    kendalltau : Kendall's tau, a correlation measure for ordinal data.

    Notes
    -----
    The correlation coefficient is calculated as follows:

    .. math::

        r = \frac{\sum (x - m_x) (y - m_y)}
                 {\sqrt{\sum (x - m_x)^2 \sum (y - m_y)^2}}

    where :math:`m_x` is the mean of the vector x and :math:`m_y` is
    the mean of the vector y.

    Under the assumption that x and y are drawn from
    independent normal distributions (so the population correlation coefficient
    is 0), the probability density function of the sample correlation
    coefficient r is ([1]_, [2]_):

    .. math::
        f(r) = \frac{{(1-r^2)}^{n/2-2}}{\mathrm{B}(\frac{1}{2},\frac{n}{2}-1)}

    where n is the number of samples, and B is the beta function.  This
    is sometimes referred to as the exact distribution of r.  This is
    the distribution that is used in `pearsonr` to compute the p-value.
    The distribution is a beta distribution on the interval [-1, 1],
    with equal shape parameters a = b = n/2 - 1.  In terms of SciPy's
    implementation of the beta distribution, the distribution of r is::

        dist = scipy.stats.beta(n/2 - 1, n/2 - 1, loc=-1, scale=2)

    The default p-value returned by `pearsonr` is a two-sided p-value. For a
    given sample with correlation coefficient r, the p-value is
    the probability that abs(r') of a random sample x' and y' drawn from
    the population with zero correlation would be greater than or equal
    to abs(r). In terms of the object ``dist`` shown above, the p-value
    for a given r and length n can be computed as::

        p = 2*dist.cdf(-abs(r))

    When n is 2, the above continuous distribution is not well-defined.
    One can interpret the limit of the beta distribution as the shape
    parameters a and b approach a = b = 0 as a discrete distribution with
    equal probability masses at r = 1 and r = -1.  More directly, one
    can observe that, given the data x = [x1, x2] and y = [y1, y2], and
    assuming x1 != x2 and y1 != y2, the only possible values for r are 1
    and -1.  Because abs(r') for any sample x' and y' with length 2 will
    be 1, the two-sided p-value for a sample of length 2 is always 1.

    For backwards compatibility, the object that is returned also behaves
    like a tuple of length two that holds the statistic and the p-value.

    References
    ----------
    .. [1] "Pearson correlation coefficient", Wikipedia,
           https://en.wikipedia.org/wiki/Pearson_correlation_coefficient
    .. [2] Student, "Probable error of a correlation coefficient",
           Biometrika, Volume 6, Issue 2-3, 1 September 1908, pp. 302-310.
    .. [3] C. J. Kowalski, "On the Effects of Non-Normality on the Distribution
           of the Sample Product-Moment Correlation Coefficient"
           Journal of the Royal Statistical Society. Series C (Applied
           Statistics), Vol. 21, No. 1 (1972), pp. 1-12.

    Examples
    --------
    >>> from scipy import stats
    >>> res = stats.pearsonr([1, 2, 3, 4, 5], [10, 9, 2.5, 6, 4])
    >>> res
    PearsonRResult(statistic=-0.7426106572325056, pvalue=0.15055580885344558)
    >>> res.confidence_interval()
    ConfidenceInterval(low=-0.9816918044786463, high=0.40501116769030976)

    There is a linear dependence between x and y if y = a + b*x + e, where
    a,b are constants and e is a random error term, assumed to be independent
    of x. For simplicity, assume that x is standard normal, a=0, b=1 and let
    e follow a normal distribution with mean zero and standard deviation s>0.

    >>> rng = cp.random.default_rng()
    >>> s = 0.5
    >>> x = stats.norm.rvs(size=500, random_state=rng)
    >>> e = stats.norm.rvs(scale=s, size=500, random_state=rng)
    >>> y = x + e
    >>> stats.pearsonr(x, y).statistic
    0.9001942438244763

    This should be close to the exact value given by

    >>> 1/cp.sqrt(1 + s**2)
    0.8944271909999159

    For s=0.5, we observe a high level of correlation. In general, a large
    variance of the noise reduces the correlation, while the correlation
    approaches one as the variance of the error goes to zero.

    It is important to keep in mind that no correlation does not imply
    independence unless (x, y) is jointly normal. Correlation can even be zero
    when there is a very simple dependence structure: if X follows a
    standard normal distribution, let y = abs(x). Note that the correlation
    between x and y is zero. Indeed, since the expectation of x is zero,
    cov(x, y) = E[x*y]. By definition, this equals E[x*abs(x)] which is zero
    by symmetry. The following lines of code illustrate this observation:

    >>> y = cp.abs(x)
    >>> stats.pearsonr(x, y)
    PearsonRResult(statistic=-0.05444919272687482, pvalue=0.22422294836207743)

    A non-zero correlation coefficient can be misleading. For example, if X has
    a standard normal distribution, define y = x if x < 0 and y = 0 otherwise.
    A simple calculation shows that corr(x, y) = sqrt(2/Pi) = 0.797...,
    implying a high level of correlation:

    >>> y = cp.where(x < 0, x, 0)
    >>> stats.pearsonr(x, y)
    PearsonRResult(statistic=0.861985781588, pvalue=4.813432002751103e-149)

    This is unintuitive since there is no dependence of x and y if x is larger
    than zero which happens in about half of the cases if we sample x and y.

    """
    # inputs must be 1D
    n = len(x)
    if n != len(y):
        raise ValueError('x and y must have the same length.')

    if n < 2:
        raise ValueError('x and y must have length at least 2.')

    # If an input is constant, the correlation coefficient is not defined.
    if (x == x[0]).all() or (y == y[0]).all():
        warnings.warn(PearsonRConstantInputWarning())
        result = PearsonRResult(statistic=cp.nan, pvalue=cp.nan, n=n,
                                alternative=alternative)
        return result

    # dtype is the data type for the calculations.  This expression ensures
    # that the data type is at least 64 bit floating point.  It might have
    # more precision if the input is, for example, cp.longdouble.
    dtype = cp.result_type(x.dtype, y.dtype, float)

    if n == 2:
        r = float(dtype(cp.sign(x[1] - x[0])*cp.sign(y[1] - y[0])))
        result = PearsonRResult(statistic=r, pvalue=1.0, n=n,
                                alternative=alternative)
        return result

    xmean = x.mean(dtype=dtype)
    ymean = y.mean(dtype=dtype)

    # By using `astype(dtype)`, we ensure that the intermediate calculations
    # use at least 64 bit floating point.
    xm = x.astype(dtype) - xmean
    ym = y.astype(dtype) - ymean

    if False:
        # TODO: need cupyx.scipy.linalg.norm in CuPy
        # Unlike cp.linalg.norm or the expression sqrt((xm*xm).sum()),
        # scipy.linalg.norm(xm) does not overflow if xm is, for example,
        # [-5e210, 5e210, 3e200, -3e200]
        normxm = linalg.norm(xm)
        normym = linalg.norm(ym)
    else:
        normxm = cp.linalg.norm(xm)
        normym = cp.linalg.norm(ym)

    threshold = 1e-13
    if normxm < threshold*abs(xmean) or normym < threshold*abs(ymean):
        # If all the values in x (likewise y) are very close to the mean,
        # the loss of precision that occurs in the subtraction xm = x - xmean
        # might result in large errors in r.
        warnings.warn(PearsonRNearConstantInputWarning())

    r = cp.dot(xm/normxm, ym/normym)

    # Presumably, if abs(r) > 1, then it is only some small artifact of
    # floating point arithmetic.
    r = max(min(r, 1.0), -1.0)

    # As explained in the docstring, the p-value can be computed as
    #     p = 2*dist.cdf(-abs(r))
    # where dist is the beta distribution on [-1, 1] with shape parameters
    # a = b = n/2 - 1.  `special.btdtr` is the CDF for the beta distribution
    # on [0, 1].  To use it, we make the transformation  x = (r + 1)/2; the
    # shape parameters do not change.  Then -abs(r) used in `cdf(-abs(r))`
    # becomes x = (-abs(r) + 1)/2 = 0.5*(1 - abs(r)).  (r is cast to float64
    # to avoid a TypeError raised by btdtr when r is higher precision.)
    ab = n/2 - 1
    if alternative == 'two-sided':
        prob = 2*special.btdtr(ab, ab, 0.5*(1 - abs(cp.float64(r))))
    elif alternative == 'less':
        prob = 1 - special.btdtr(ab, ab, 0.5*(1 - abs(cp.float64(r))))
    elif alternative == 'greater':
        prob = special.btdtr(ab, ab, 0.5*(1 - abs(cp.float64(r))))
    else:
        raise ValueError('alternative must be one of '
                         '["two-sided", "less", "greater"]')

    return PearsonRResult(statistic=float(r), pvalue=float(prob), n=n,
                          alternative=alternative)
