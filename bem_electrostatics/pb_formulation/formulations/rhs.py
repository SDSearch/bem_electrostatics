import numpy as np
import bempp.api
import os


def direct(dirichl_space, neumann_space, q, x_q, ep_in, rhs_constructor):
    if rhs_constructor == "fmm":
        @bempp.api.callable(vectorized=True)
        def fmm_green_func(x, n, domain_index, result):
            import exafmm.laplace as _laplace
            sources = _laplace.init_sources(x_q, q)
            targets = _laplace.init_targets(x.T)
            fmm = _laplace.LaplaceFmm(p=10, ncrit=500, filename='.rhs.tmp')
            tree = _laplace.setup(sources, targets, fmm)
            values = _laplace.evaluate(tree, fmm)
            os.remove('.rhs.tmp')
            result[:] = values[:, 0] / ep_in

        # @bempp.api.real_callable
        # def zero(x, n, domain_index, result):
        #     result[0] = 0

        coefs = np.zeros(neumann_space.global_dof_count)

        rhs_1 = bempp.api.GridFunction(dirichl_space, fun=fmm_green_func)
        # rhs_2 = bempp.api.GridFunction(neumann_space, fun=zero)
        rhs_2 = bempp.api.GridFunction(neumann_space, coefficients=coefs)

    else:
        @bempp.api.real_callable
        def charges_fun(x, n, domain_index, result):
            nrm = np.sqrt((x[0] - x_q[:, 0]) ** 2 + (x[1] - x_q[:, 1]) ** 2 + (x[2] - x_q[:, 2]) ** 2)
            aux = np.sum(q / nrm)
            result[0] = aux / (4 * np.pi * ep_in)

        @bempp.api.real_callable
        def zero(x, n, domain_index, result):
            result[0] = 0

        rhs_1 = bempp.api.GridFunction(dirichl_space, fun=charges_fun)
        rhs_2 = bempp.api.GridFunction(neumann_space, fun=zero)

    return rhs_1, rhs_2


def direct_external(dirichl_space, neumann_space, q, x_q, ep_in, rhs_constructor):
    if rhs_constructor == "fmm":
        @bempp.api.callable(vectorized=True)
        def fmm_green_func(x, n, domain_index, result):
            import exafmm.laplace as _laplace
            sources = _laplace.init_sources(x_q, q)
            targets = _laplace.init_targets(x.T)
            fmm = _laplace.LaplaceFmm(p=10, ncrit=500, filename='.rhs.tmp')
            tree = _laplace.setup(sources, targets, fmm)
            values = _laplace.evaluate(tree, fmm)
            os.remove('.rhs.tmp')
            result[:] = values[:, 0] / ep_in

        @bempp.api.real_callable
        def zero(x, n, domain_index, result):
            result[0] = 0

        rhs_1 = bempp.api.GridFunction(neumann_space, fun=zero)
        rhs_2 = bempp.api.GridFunction(dirichl_space, fun=fmm_green_func)

    else:
        @bempp.api.real_callable
        def charges_fun(x, n, domain_index, result):
            nrm = np.sqrt((x[0] - x_q[:, 0]) ** 2 + (x[1] - x_q[:, 1]) ** 2 + (x[2] - x_q[:, 2]) ** 2)
            aux = np.sum(q / nrm)
            result[0] = aux / (4 * np.pi * ep_in)

        @bempp.api.real_callable
        def zero(x, n, domain_index, result):
            result[0] = 0

        rhs_1 = bempp.api.GridFunction(neumann_space, fun=zero)
        rhs_2 = bempp.api.GridFunction(dirichl_space, fun=charges_fun)

    return rhs_1, rhs_2


def alpha_beta_type(dirichl_space, neumann_space, q, x_q, ep_in, rhs_constructor):
    if rhs_constructor == "fmm":
        @bempp.api.callable(vectorized=True)
        def fmm_green_func(x, n, domain_index, result):
            import exafmm.laplace as _laplace
            sources = _laplace.init_sources(x_q, q)
            targets = _laplace.init_targets(x.T)
            fmm = _laplace.LaplaceFmm(p=10, ncrit=500, filename='.rhs.tmp')
            tree = _laplace.setup(sources, targets, fmm)
            values = _laplace.evaluate(tree, fmm)
            os.remove('.rhs.tmp')
            result[:] = (-1.0)*values[:, 0] / ep_in

        @bempp.api.callable(vectorized=True)
        def fmm_d_green_func(x, n, domain_index, result):
            import exafmm.laplace as _laplace
            sources = _laplace.init_sources(x_q, q)
            targets = _laplace.init_targets(x.T)
            fmm = _laplace.LaplaceFmm(p=10, ncrit=500, filename='.rhs.tmp')
            tree = _laplace.setup(sources, targets, fmm)
            values = _laplace.evaluate(tree, fmm)
            os.remove('.rhs.tmp')
            result[:] = (-1.0)*np.sum(values[:, 1:] * n.T, axis=1) / ep_in

        rhs_1 = bempp.api.GridFunction(dirichl_space, fun=fmm_green_func)
        rhs_2 = bempp.api.GridFunction(dirichl_space, fun=fmm_d_green_func)

    else:
        @bempp.api.real_callable
        def d_green_func(x, n, domain_index, result):
            nrm = np.sqrt((x[0]-x_q[:, 0])**2 + (x[1]-x_q[:, 1])**2 + (x[2]-x_q[:, 2])**2)
            const = -1./(4.*np.pi*ep_in)
            result[:] = (-1.0)*const*np.sum(q*np.dot(x-x_q, n)/(nrm**3))

        @bempp.api.real_callable
        def green_func(x, n, domain_index, result):
            nrm = np.sqrt((x[0]-x_q[:, 0])**2 + (x[1]-x_q[:, 1])**2 + (x[2]-x_q[:, 2])**2)
            result[:] = (-1.0)*np.sum(q/nrm)/(4.*np.pi*ep_in)

        rhs_1 = bempp.api.GridFunction(dirichl_space, fun=green_func)
        rhs_2 = bempp.api.GridFunction(dirichl_space, fun=d_green_func)

    return rhs_1, rhs_2

def lu(dirichl_space, neumann_space, q, x_q, ep_ex, rhs_constructor):
    if rhs_constructor == "fmm":
        @bempp.api.callable(vectorized=True)
        def rhs1_fun(x, n, domain_index, result):
            import exafmm.laplace as _laplace
            sources = _laplace.init_sources(x_q, q)
            targets = _laplace.init_targets(x.T)
            fmm = _laplace.LaplaceFmm(p=10, ncrit=500, filename='.rhs.tmp')
            tree = _laplace.setup(sources, targets, fmm)
            values = _laplace.evaluate(tree, fmm)
            os.remove('.rhs.tmp')
            result[:] = values[:,0] / ep_ex

        @bempp.api.callable(vectorized=True)
        def rhs2_fun(x, n, domain_index, result):
            import exafmm.laplace as _laplace
            sources = _laplace.init_sources(x_q, q)
            targets = _laplace.init_targets(x.T)
            fmm = _laplace.LaplaceFmm(p=10, ncrit=500, filename='.rhs.tmp')
            tree = _laplace.setup(sources, targets, fmm)
            values = _laplace.evaluate(tree, fmm)
            os.remove('.rhs.tmp')
            result[:] = np.sum(values[:,1:] * n.T, axis=1) / ep_ex

        rhs_1 = bempp.api.GridFunction(dirichl_space, fun=rhs1_fun)
        rhs_2 = bempp.api.GridFunction(neumann_space, fun=rhs2_fun)

    else:
        @bempp.api.real_callable
        def d_green_func(x, n, domain_index, result):
            nrm = np.sqrt((x[0]-x_q[:, 0])**2 + (x[1]-x_q[:, 1])**2 + (x[2]-x_q[:, 2])**2)
            const = -1./(4.*np.pi*ep_ex)
            result[:] = const*np.sum(q*np.dot(x-x_q, n)/(nrm**3))

        @bempp.api.real_callable
        def green_func(x, n, domain_index, result):
            nrm = np.sqrt((x[0]-x_q[:, 0])**2 + (x[1]-x_q[:, 1])**2 + (x[2]-x_q[:, 2])**2)
            result[:] = np.sum(q/nrm)/(4.*np.pi*ep_ex)

        rhs_1 = bempp.api.GridFunction(dirichl_space, fun=green_func)
        rhs_2 = bempp.api.GridFunction(dirichl_space, fun=d_green_func)

    return rhs_1, rhs_2

def juffer(dirichl_space, neumann_space, q, x_q, ep_in, rhs_constructor):
    if rhs_constructor == "fmm":
        @bempp.api.callable(vectorized=True)
        def rhs1_fun(x, n, domain_index, result):
            import exafmm.laplace as _laplace
            sources = _laplace.init_sources(x_q, q)
            targets = _laplace.init_targets(x.T)
            fmm = _laplace.LaplaceFmm(p=10, ncrit=500, filename='.rhs.tmp')
            tree = _laplace.setup(sources, targets, fmm)
            values = _laplace.evaluate(tree, fmm)
            os.remove('.rhs.tmp')
            result[:] = values[:,0] / ep_in

        @bempp.api.callable(vectorized=True)
        def rhs2_fun(x, n, domain_index, result):
            import exafmm.laplace as _laplace
            sources = _laplace.init_sources(x_q, q)
            targets = _laplace.init_targets(x.T)
            fmm = _laplace.LaplaceFmm(p=10, ncrit=500, filename='.rhs.tmp')
            tree = _laplace.setup(sources, targets, fmm)
            values = _laplace.evaluate(tree, fmm)
            os.remove('.rhs.tmp')
            result[:] = np.sum(values[:,1:] * n.T, axis=1) / ep_in

        rhs_1 = bempp.api.GridFunction(dirichl_space, fun=rhs1_fun)
        rhs_2 = bempp.api.GridFunction(neumann_space, fun=rhs2_fun)

    else:
        @bempp.api.real_callable
        def d_green_func(x, n, domain_index, result):
            nrm = np.sqrt((x[0]-x_q[:, 0])**2 + (x[1]-x_q[:, 1])**2 + (x[2]-x_q[:, 2])**2)
            const = -1./(4.*np.pi*ep_in)
            result[:] = const*np.sum(q*np.dot(x-x_q, n)/(nrm**3))

        @bempp.api.real_callable
        def green_func(x, n, domain_index, result):
            nrm = np.sqrt((x[0]-x_q[:, 0])**2 + (x[1]-x_q[:, 1])**2 + (x[2]-x_q[:, 2])**2)
            result[:] = np.sum(q/nrm)/(4.*np.pi*ep_in)

        rhs_1 = bempp.api.GridFunction(dirichl_space, fun=green_func)
        rhs_2 = bempp.api.GridFunction(dirichl_space, fun=d_green_func)

    return rhs_1, rhs_2


def first_kind_internal(dirichl_space, neumann_space, q, x_q, ep_in, rhs_constructor):
    if rhs_constructor == "fmm":
        @bempp.api.callable(vectorized=True)
        def rhs1_fun(x, n, domain_index, result):
            import exafmm.laplace as _laplace
            sources = _laplace.init_sources(x_q, q)
            targets = _laplace.init_targets(x.T)
            fmm = _laplace.LaplaceFmm(p=10, ncrit=500, filename='.rhs.tmp')
            tree = _laplace.setup(sources, targets, fmm)
            values = _laplace.evaluate(tree, fmm)
            os.remove('.rhs.tmp')
            result[:] = (-1.0)*values[:, 0] / ep_in

        @bempp.api.callable(vectorized=True)
        def rhs2_fun(x, n, domain_index, result):
            import exafmm.laplace as _laplace
            sources = _laplace.init_sources(x_q, q)
            targets = _laplace.init_targets(x.T)
            fmm = _laplace.LaplaceFmm(p=10, ncrit=500, filename='.rhs.tmp')
            tree = _laplace.setup(sources, targets, fmm)
            values = _laplace.evaluate(tree, fmm)
            os.remove('.rhs.tmp')
            result[:] = (-1.0)*np.sum(values[:,1:] * n.T, axis=1) / ep_in

        rhs_1 = bempp.api.GridFunction(dirichl_space, fun=rhs1_fun)
        rhs_2 = bempp.api.GridFunction(neumann_space, fun=rhs2_fun)

    else:
        @bempp.api.real_callable
        def d_green_func(x, n, domain_index, result):
            nrm = np.sqrt((x[0]-x_q[:, 0])**2 + (x[1]-x_q[:, 1])**2 + (x[2]-x_q[:, 2])**2)
            const = -1./(4.*np.pi*ep_in)
            result[:] = -1.0 * const*np.sum(q*np.dot(x-x_q, n)/(nrm**3))

        @bempp.api.real_callable
        def green_func(x, n, domain_index, result):
            nrm = np.sqrt((x[0]-x_q[:, 0])**2 + (x[1]-x_q[:, 1])**2 + (x[2]-x_q[:, 2])**2)
            result[:] = -1.0 * np.sum(q/nrm)/(4.*np.pi*ep_in)

        rhs_1 = bempp.api.GridFunction(dirichl_space, fun=green_func)
        rhs_2 = bempp.api.GridFunction(dirichl_space, fun=d_green_func)

    return rhs_1, rhs_2


def first_kind_external(dirichl_space, neumann_space, q, x_q, ep_in, ep_ex, rhs_constructor):
    if rhs_constructor == "fmm":
        @bempp.api.callable(vectorized=True)
        def rhs1_fun(x, n, domain_index, result):
            import exafmm.laplace as _laplace
            sources = _laplace.init_sources(x_q, q)
            targets = _laplace.init_targets(x.T)
            fmm = _laplace.LaplaceFmm(p=10, ncrit=500, filename='.rhs.tmp')
            tree = _laplace.setup(sources, targets, fmm)
            values = _laplace.evaluate(tree, fmm)
            os.remove('.rhs.tmp')
            result[:] = (-1.0)*values[:, 0] / ep_in

        @bempp.api.callable(vectorized=True)
        def rhs2_fun(x, n, domain_index, result):
            import exafmm.laplace as _laplace
            sources = _laplace.init_sources(x_q, q)
            targets = _laplace.init_targets(x.T)
            fmm = _laplace.LaplaceFmm(p=10, ncrit=500, filename='.rhs.tmp')
            tree = _laplace.setup(sources, targets, fmm)
            values = _laplace.evaluate(tree, fmm)
            os.remove('.rhs.tmp')
            result[:] = (-1.0)*np.sum(values[:,1:] * n.T, axis=1) / ep_ex

        rhs_1 = bempp.api.GridFunction(dirichl_space, fun=rhs1_fun)
        rhs_2 = bempp.api.GridFunction(neumann_space, fun=rhs2_fun)

    else:
        @bempp.api.real_callable
        def d_green_func(x, n, domain_index, result):
            nrm = np.sqrt((x[0]-x_q[:, 0])**2 + (x[1]-x_q[:, 1])**2 + (x[2]-x_q[:, 2])**2)
            const = -1./(4.*np.pi*ep_in)
            result[:] = -1.0 * (ep_in/ep_ex) * const*np.sum(q*np.dot(x-x_q, n)/(nrm**3))

        @bempp.api.real_callable
        def green_func(x, n, domain_index, result):
            nrm = np.sqrt((x[0]-x_q[:, 0])**2 + (x[1]-x_q[:, 1])**2 + (x[2]-x_q[:, 2])**2)
            result[:] = -1.0 * np.sum(q/nrm)/(4.*np.pi*ep_in)

        rhs_1 = bempp.api.GridFunction(dirichl_space, fun=green_func)
        rhs_2 = bempp.api.GridFunction(neumann_space, fun=d_green_func)

    return rhs_1, rhs_2


def muller_internal(dirichl_space, neumann_space, q, x_q, ep_in, rhs_constructor):
    @bempp.api.real_callable
    def d_green_func(x, n, domain_index, result):
        nrm = np.sqrt((x[0]-x_q[:, 0])**2 + (x[1]-x_q[:, 1])**2 + (x[2]-x_q[:, 2])**2)
        const = -1./(4.*np.pi*ep_in)
        result[:] = const*np.sum(q*np.dot(x-x_q, n)/(nrm**3))

    @bempp.api.real_callable
    def green_func(x, n, domain_index, result):
        nrm = np.sqrt((x[0]-x_q[:, 0])**2 + (x[1]-x_q[:, 1])**2 + (x[2]-x_q[:, 2])**2)
        result[:] = np.sum(q/nrm)/(4.*np.pi*ep_in)

    rhs_1 = bempp.api.GridFunction(dirichl_space, fun=green_func)
    rhs_2 = bempp.api.GridFunction(dirichl_space, fun=d_green_func)

    return rhs_1, rhs_2


def muller_external(dirichl_space, neumann_space, q, x_q, ep_in, ep_ex, rhs_constructor):
    @bempp.api.real_callable
    def d_green_func(x, n, domain_index, result):
        nrm = np.sqrt((x[0]-x_q[:, 0])**2 + (x[1]-x_q[:, 1])**2 + (x[2]-x_q[:, 2])**2)
        const = -1./(4.*np.pi*ep_in)
        result[:] = (ep_in/ep_ex) * const*np.sum(q*np.dot(x-x_q, n)/(nrm**3))

    @bempp.api.real_callable
    def green_func(x, n, domain_index, result):
        nrm = np.sqrt((x[0]-x_q[:, 0])**2 + (x[1]-x_q[:, 1])**2 + (x[2]-x_q[:, 2])**2)
        result[:] = np.sum(q/nrm)/(4.*np.pi*ep_in)

    rhs_1 = bempp.api.GridFunction(dirichl_space, fun=green_func)
    rhs_2 = bempp.api.GridFunction(dirichl_space, fun=d_green_func)

    return rhs_1, rhs_2