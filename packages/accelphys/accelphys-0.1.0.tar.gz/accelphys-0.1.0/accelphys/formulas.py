from typing import Union
import numpy as np
from scipy.constants import c


class Relativistic:
    @classmethod
    def gamma(
        cls,
        v: Union[float, np.ndarray] = None,
        beta: Union[float, np.ndarray] = None,
        q: float = None,
        p: float = None,
        e_0: float = None,
    ) -> Union[float, np.ndarray]:
        """
        The combinations of inputs that can be provided are:
        - v
        - beta
        - q, p, e_0

        :param v: velocity in m/s
        :param beta: relativistic beta. Velocity divided by speed of light.
        :param q: charge in elementary charge
        :param p: momentum in GeV/c
        :param e_0: rest energy in GeV
        """
        if v is not None:
            return 1 / np.sqrt(1 - (v**2 / c**2))
        elif beta is not None:
            return 1 / np.sqrt(1 - beta**2)
        elif (q and p and e_0) is not None:
            return np.sqrt(((p * q) / e_0) ** 2 + 1)
        else:
            raise ValueError(
                "You have not provided enough information to calculate beta."
            )

    @classmethod
    def beta(
        cls,
        v: Union[float, np.ndarray] = None,
        gamma: Union[float, np.ndarray] = None,
        b_rho: Union[float, np.ndarray] = None,
        m: float = None,
        q: float = None,
    ) -> Union[float, np.ndarray]:
        """
        The combinations of inputs that can be provided are:
        - v
        - gamma
        - b_rho, m, q

        :param v: velocity in m/s
        :param gamma: Lorentz factor
        :param b_rho: magnetic rigidity in Tm
        :param m: atomic mass in atomic mass unit
        :param q: charge in elementary charge
        """
        if v is not None:
            return v / c
        elif gamma is not None:
            return np.sqrt(1 - 1 / gamma**2)
        elif (b_rho and q and m) is not None:
            amu = 0.931493614838934  # GeV/c^2
            p = b_rho * 0.33
            e_0 = m * amu  # GeV
            return np.sqrt(1 - 1 / cls.gamma(p=p, q=q, e_0=e_0) ** 2)
        else:
            raise ValueError(
                "You have not provided enough information to calculate beta."
            )

    @staticmethod
    def b_rho(
        p: Union[float, np.ndarray] = None,
        q: float = None,
        m: float = None,
        gamma: Union[float, np.ndarray] = None,
    ) -> Union[float, np.ndarray]:
        return p / q

    @staticmethod
    def p_momentum(
        e_tot: Union[float, np.ndarray] = None,
        e_0: float = None,
        q: float = None,
        b_rho: Union[float, np.ndarray] = None,
    ) -> Union[float, np.ndarray]:
        if (e_0 and e_tot) is not None:
            return np.sqrt(e_tot**2 - e_0**2) / c
        elif (b_rho and q) is not None:
            return b_rho * q
