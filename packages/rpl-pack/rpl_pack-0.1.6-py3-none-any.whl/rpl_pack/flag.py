"""
FLAG program interfaces.

"""

import sys
import pathlib

from json import JSONDecodeError

from typing import Any

import numpy as np
import matplotlib.pyplot as plt

from rpl_pack.rpl import _RPLBase
from rpl_pack.utils import encode_arrays, decode_arrays
from rpl_pack.rpl_exceptions import RPLUserCredentialsDeniedException, RPLServerException


class _FLAGBase(_RPLBase):
    """Base class that all classes within flag inherit from.
    
    Docs go here.
    """
    def __init__(self, username: str, password: str) -> None:
        super().__init__(username, password)
        self._base_url += 'flag/'

    def __str__(self):
        return "Base class for all FLAG classes."


class FLAG(_FLAGBase):
    """Connection to FLAG api is through this class.

    Docs go here.
    """
    def __init__(self, username: str, password: str) -> None:
        super().__init__(username, password)


class Brine(FLAG):
    """Returns Brine application object upon authentication of 'username' and
    'password' inputs through which all brine/water property calculations are
    performed, otherwise RPLUserCredentialsDeniedException is raised.

    As long as the Brine application object exists it can be used to call functions
    on the RPL server, checking authentication and permissions to each function
    called.

    :param username: RPL server login username.
    :type username: str
    :param password: RPL server login password.
    :type password: str
    :raise rpl_exceptions.RPLUserCredentialsDeniedException: If either username/password is invalid.
    :return: Brine application instance.
    :rtype: object

    """
    def __init__(self, username: str, password: str) -> None:
        super().__init__(username, password)
        self._base_url += 'brine/'
        # self.calculated_properties = None

    def velocity_water(self, temperature: float, pressure: float) -> float:
        """Calculate velcity of pure water at given temperature (C) and pressure (MPa).
        
        :param temperature: Temperature of water in C.
        :type temperature: float
        :param pressure: Pressure of water in MPa.
        :type pressure: float
        :return: Velocity of pure water at given temperature and pressure.
        :rtype: float
        """
        self.props = {"temperature": temperature, "pressure": pressure}
        enc_arr = encode_arrays(["temperature", "pressure"], [temperature, pressure])
        resp = self._post("velocity_water/", data=enc_arr)
        if not self._is_authentic(resp):
            raise RPLUserCredentialsDeniedException("User credentials were denied by the server.")

        try:
            dec_arr = decode_arrays(resp.json())['vel_w']
            return dec_arr
        except JSONDecodeError:
            raise RPLServerException(f"The server denied your request:\n\t{resp.text}")

    def density_water(self, temperature: float, pressure: float) -> float:
        """Calculate density of pure water at given temperature (C) and pressure (MPa).
        
        :param temperature: Temperature of water in C.
        :type temperature: float
        :param pressure: Pressure of water in MPa.
        :type pressure: float
        :return: Density of pure water at given temperature and pressure.
        :rtype: float
        """
        self.props = {"temperature": temperature, "pressure": pressure}
        enc_arr = encode_arrays(["temperature", "pressure"], [temperature, pressure])
        resp = self._post("density_water/", data=enc_arr)
        if not self._is_authentic(resp):
            raise RPLUserCredentialsDeniedException("User credentials were denied by the server.")

        try:
            dec_arr = decode_arrays(resp.json())['rho_w']
            return dec_arr
        except JSONDecodeError:
            raise RPLServerException(f"The server denied your request:\n\t{resp.text}")

    def modulus_water(self, temperature: float, pressure: float) -> float:
        """Calculate modulus of pure water at given temperature (C) and pressure (MPa).
        
        :param temperature: Temperature of water in C.
        :type temperature: float
        :param pressure: Pressure of water in MPa.
        :type pressure: float
        :return: Modulus of pure water at given temperature and pressure.
        :rtype: float
        """
        self.props = {"temperature": temperature, "pressure": pressure}
        enc_arr = encode_arrays(["temperature", "pressure"], [temperature, pressure])
        resp = self._post("modulus_water/", data=enc_arr)
        if not self._is_authentic(resp):
            raise RPLUserCredentialsDeniedException("User credentials were denied by the server.")

        try:
            dec_arr = decode_arrays(resp.json())['mod_w']
            return dec_arr
        except JSONDecodeError:
            raise RPLServerException(f"The server denied your request:\n\t{resp.text}")

    def velocity_brine(self, temperature: float, pressure: float, salinity: float,
                       NaCl: float, KCl: float, CaCl2: float) -> float:
        """Calculate velocity of brine at given temperature (C),
        pressure (MPa), salinity (ppm), NaCl (weight %), KCl (weight %),
        and CaCl2 (weight %).
        
        :param temperature: Temperature of brine in C.
        :type temperature: float
        :param pressure: Pressure of brine in MPa.
        :type pressure: float
        :param salinity: Salinity of brine (weight %).
        :type salinity: float
        :param NaCl: Weight % of NaCl in brine.
        :type NaCl: float
        :param KCl: Weight % of KCl in brine.
        :type KCl: float
        :param CaCl2: Weight % of CaCl2 in brine.
        :type CaCl2: float
        :return: Velocity of brine at given temperature and pressure.
        :rtype: float
        """
        self.props = {"temperature": temperature, "pressure": pressure,
                      "salinity": salinity, "NaCl": NaCl, "KCl": KCl,
                      "CaCl2": CaCl2}
        enc_arr = encode_arrays(["temperature", "pressure", "salinity", "NaCl", "KCl", "CaCl2"],
                                [temperature, pressure, salinity, NaCl, KCl, CaCl2])
        resp = self._post("velocity_brine/", data=enc_arr)
        if not self._is_authentic(resp):
            raise RPLUserCredentialsDeniedException("User credentials were denied by the server.")

        try:
            dec_arr = decode_arrays(resp.json())['vel_b']
            return dec_arr
        except JSONDecodeError:
            raise RPLServerException(f"The server denied your request:\n\t{resp.text}")
    
    def density_brine(self, temperature: float, pressure: float, salinity: float,
                      NaCl: float, KCl: float, CaCl2: float) -> float:
        """Calculate density of brine at given temperature (C),
        pressure (MPa), salinity (ppm), NaCl (weight %), KCl (weight %),
        and CaCl2 (weight %).
        
        :param temperature: Temperature of brine in C.
        :type temperature: float
        :param pressure: Pressure of brine in MPa.
        :type pressure: float
        :param salinity: Salinity of brine (weight %).
        :type salinity: float
        :param NaCl: Weight % of NaCl in brine.
        :type NaCl: float
        :param KCl: Weight % of KCl in brine.
        :type KCl: float
        :param CaCl2: Weight % of CaCl2 in brine.
        :type CaCl2: float
        :return: Density of brine at given temperature and pressure.
        :rtype: float
        """
        self.props = {"temperature": temperature, "pressure": pressure,
                      "salinity": salinity, "NaCl": NaCl, "KCl": KCl,
                      "CaCl2": CaCl2}
        enc_arr = encode_arrays(["temperature", "pressure", "salinity", "NaCl", "KCl", "CaCl2"],
                                [temperature, pressure, salinity, NaCl, KCl, CaCl2])
        resp = self._post("density_brine/", data=enc_arr)
        if not self._is_authentic(resp):
            raise RPLUserCredentialsDeniedException("User credentials were denied by the server.")

        try:
            dec_arr = decode_arrays(resp.json())['rho_b']
            return dec_arr
        except JSONDecodeError:
            raise RPLServerException(f"The server denied your request:\n\t{resp.text}")

    def modulus_brine(self, temperature: float, pressure: float, salinity: float,
                      NaCl: float, KCl: float, CaCl2: float) -> float:
        """Calculate modulus of brine at given temperature (C),
        pressure (MPa), salinity (ppm), NaCl (weight %), KCl (weight %),
        and CaCl2 (weight %).
        
        :param temperature: Temperature of brine in C.
        :type temperature: float
        :param pressure: Pressure of brine in MPa.
        :type pressure: float
        :param salinity: Salinity of brine (weight %).
        :type salinity: float
        :param NaCl: Weight % of NaCl in brine.
        :type NaCl: float
        :param KCl: Weight % of KCl in brine.
        :type KCl: float
        :param CaCl2: Weight % of CaCl2 in brine.
        :type CaCl2: float
        :return: Modulus of brine at given temperature and pressure, salinity,
                 NaCl, KCl, CaCl2.
        :rtype: float
        """
        self.props = {"temperature": temperature, "pressure": pressure,
                      "salinity": salinity, "NaCl": NaCl, "KCl": KCl,
                      "CaCl2": CaCl2}
        enc_arr = encode_arrays(["temperature", "pressure", "salinity", "NaCl", "KCl", "CaCl2"],
                                [temperature, pressure, salinity, NaCl, KCl, CaCl2])
        resp = self._post("modulus_brine/", data=enc_arr)
        if not self._is_authentic(resp):
            raise RPLUserCredentialsDeniedException("User credentials were denied by the server.")

        try:
            dec_arr = decode_arrays(resp.json())['mod_b']
            return dec_arr
        except JSONDecodeError:
            raise RPLServerException(f"The server denied your request:\n\t{resp.text}")

    def velocity_water_CO2(self, temperature: float, pressure: float, gwr: float) -> float:
        """Calculate velocity of water+CO2 at given temperature (C), pressure (MPa), gwr (L/L).
        
        :param temperature: Temperature of brine in C.
        :type temperature: float
        :param pressure: Pressure of brine in MPa.
        :type pressure: float
        :param gwr: Gas water ratio of CO2 to water.
        :type gwr: float
        :return: Velocity of water+CO2 at given temperature and pressure and gwr.
        :rtype: float
        """
        self.props = {"temperature": temperature, "pressure": pressure, "gwr": gwr}
        enc_arr = encode_arrays(["temperature", "pressure", "gwr"], [temperature, pressure, gwr])
        resp = self._post("velocity_water_CO2/", data=enc_arr)
        if not self._is_authentic(resp):
            raise RPLUserCredentialsDeniedException("User credentials were denied by the server.")

        try:
            dec_arr = decode_arrays(resp.json())['vel_wCO2']
            return dec_arr
        except JSONDecodeError:
            raise RPLServerException(f"The server denied your request:\n\t{resp.text}")

    def density_water_CO2(self, temperature: float, pressure: float, gwr: float) -> float:
        """Calculate density of water+CO2 at given temperature (C), pressure (MPa), gwr (L/L).
        
        :param temperature: Temperature of brine in C.
        :type temperature: float
        :param pressure: Pressure of brine in MPa.
        :type pressure: float
        :param gwr: Gas water ratio of CO2 to water.
        :type gwr: float
        :return: Density of water+CO2 at given temperature and pressure and gwr.
        :rtype: float
        """
        self.props = {"temperature": temperature, "pressure": pressure, "gwr": gwr}
        enc_arr = encode_arrays(["temperature", "pressure", "gwr"], [temperature, pressure, gwr])
        resp = self._post("density_water_CO2/", data=enc_arr)
        if not self._is_authentic(resp):
            raise RPLUserCredentialsDeniedException("User credentials were denied by the server.")

        try:
            dec_arr = decode_arrays(resp.json())['rho_wCO2']
            return dec_arr
        except JSONDecodeError:
            raise RPLServerException(f"The server denied your request:\n\t{resp.text}")

    def viscosity_water(self, temperature: float) -> float:
        """Calculate viscosity of water at given temperature (C).
        
        :param temperature: Temperature of water in C.
        :type temperature: float
        :return: Viscosity of water at given temperature.
        :rtype: float
        """
        self.props = {"temperature": temperature}
        enc_arr = encode_arrays(["temperature"], [temperature])
        resp = self._post("viscosity_water/", data=enc_arr)
        if not self._is_authentic(resp):
            raise RPLUserCredentialsDeniedException("User credentials were denied by the server.")

        try:
            dec_arr = decode_arrays(resp.json())['visc_w']
            return dec_arr
        except JSONDecodeError:
            raise RPLServerException(f"The server denied your request:\n\t{resp.text}")

    def viscosity_brine(self, temperature: float, salinity: float) -> float:
        """Calculate viscosity of brine at given temperature (C) and salinity (ppm).
        
        :param temperature: Temperature of brine in C.
        :type temperature: float
        :param salinity: Salinity of brine in ppm.
        :type temperature: float
        :return: Viscosity of brine at given temperature and salinity.
        :rtype: float
        """
        self.props = {"temperature": temperature}
        enc_arr = encode_arrays(["temperature", "salinity"], [temperature, salinity])
        resp = self._post("viscosity_brine/", data=enc_arr)
        if not self._is_authentic(resp):
            raise RPLUserCredentialsDeniedException("User credentials were denied by the server.")

        try:
            dec_arr = decode_arrays(resp.json())['visc_b']
            return dec_arr
        except JSONDecodeError:
            raise RPLServerException(f"The server denied your request:\n\t{resp.text}")

    def solubility_gas_water(self, temperature: float, pressure: float) -> float:
        """Calculate solubility of gas in pure water (gwr) at given temperature (C)
        and pressure (MPa).
        
        :param temperature: Temperature of water in C.
        :type temperature: float
        :param pressure: Pressure of water in MPa.
        :type temperature: float
        :return: Solubility of gas in pure water (gwr) at given temperature and pressure.
        :rtype: float
        """
        self.props = {"temperature": temperature, "pressure": pressure}
        enc_arr = encode_arrays(["temperature", "pressure"], [temperature, pressure])
        resp = self._post("solubility_gas_water/", data=enc_arr)
        if not self._is_authentic(resp):
            raise RPLUserCredentialsDeniedException("User credentials were denied by the server.")

        try:
            dec_arr = decode_arrays(resp.json())['sol_w']
            return dec_arr
        except JSONDecodeError:
            raise RPLServerException(f"The server denied your request:\n\t{resp.text}")

    def solubility_gas_brine(self, temperature: float, pressure: float, salinity: float) -> float:
        """Calculate solubility of gas in brine (gwr) at given temperature (C),
        pressure (ppm), and salinity (ppm).
        
        :param temperature: Temperature of brine in C.
        :type temperature: float
        :param pressure: Pressure of brine in MPa.
        :type temperature: float
        :param salinity: Salinity of brine in ppm.
        :type salinity: float
        :return: Solubility of gas in brine (gwr) at given temperature, pressure,
                 and salinity.
        :rtype: float
        """
        self.props = {"temperature": temperature, "pressure": pressure, "salinity": salinity}
        enc_arr = encode_arrays(["temperature", "pressure", "salinity"], [temperature, pressure, salinity])
        resp = self._post("solubility_gas_brine/", data=enc_arr)
        if not self._is_authentic(resp):
            raise RPLUserCredentialsDeniedException("User credentials were denied by the server.")

        try:
            dec_arr = decode_arrays(resp.json())['sol_b']
            return dec_arr
        except JSONDecodeError:
            raise RPLServerException(f"The server denied your request:\n\t{resp.text}")

    def resistivity_brine(self, temperature: float, salinity: float) -> float:
        """Calculate resistivity of brine at given temperature (C) and
        salinity (ppm).
        
        :param temperature: Temperature of brine in C.
        :type temperature: float
        :param salinity: Salinity of brine in ppm.
        :type salinity: float
        :return: Resistivity of brine at given temperature and salinity.
        :rtype: float
        """
        self.props = {"temperature": temperature, "salinity": salinity}
        enc_arr = encode_arrays(["temperature", "salinity"], [temperature, salinity])
        resp = self._post("resistivity_brine/", data=enc_arr)
        if not self._is_authentic(resp):
            raise RPLUserCredentialsDeniedException("User credentials were denied by the server.")

        try:
            dec_arr = decode_arrays(resp.json())['res_b']
            return dec_arr
        except JSONDecodeError:
            raise RPLServerException(f"The server denied your request:\n\t{resp.text}")

    def saturated_vapor_pressure(self, temperature: float) -> float:
        """Calculate saturated vapor pressure of brine at given temperature (C).
        
        :param temperature: Temperature of brine in C.
        :type temperature: float
        :return: Saturated vapor pressure of brine at given temperature.
        :rtype: float
        """
        self.props = {"temperature": temperature}
        enc_arr = encode_arrays(["temperature"], [temperature])
        resp = self._post("saturated_vapor_pressure/", data=enc_arr)
        if not self._is_authentic(resp):
            raise RPLUserCredentialsDeniedException("User credentials were denied by the server.")

        try:
            dec_arr = decode_arrays(resp.json())['svp']
            return dec_arr
        except JSONDecodeError:
            raise RPLServerException(f"The server denied your request:\n\t{resp.text}")

    def saturated_vapor_temperature(self, pressure: float) -> float:
        """Calculate saturated vapor temperature of brine at given pressure (MPa).
        
        :param pressure: Pressure of brine in MPa.
        :type pressure: float
        :return: Saturated vapor temperature of brine at given pressure.
        :rtype: float
        """
        self.props = {"pressure": pressure}
        enc_arr = encode_arrays(["pressure"], [pressure])
        resp = self._post("saturated_vapor_temperature/", data=enc_arr)
        if not self._is_authentic(resp):
            raise RPLUserCredentialsDeniedException("User credentials were denied by the server.")

        try:
            dec_arr = decode_arrays(resp.json())['svt']
            return dec_arr
        except JSONDecodeError:
            raise RPLServerException(f"The server denied your request:\n\t{resp.text}")

    
    def solubility_co2_water(self, temperature: float, pressure: float, other: float) -> float:
        """Calculate solubility of CO2 in H20 at a given temperature (C)
        and Pressure (MPa).
        
        :param temperature: Temperature of water in C.
        :type temperature: float
        :return: CO2 solubility in H20 at given temperature.
        :rtype: float
        """   
        self.props = {"temperature": temperature, "pressure": pressure}
        enc_arr = encode_arrays(["temperature", "pressure"], [temperature, pressure])
        resp = self._post("solubility_co2_water/", data=enc_arr)
        if not self._is_authentic(resp):
            raise RPLUserCredentialsDeniedException("User credentials were denied by the server.")

        try:
            dec_arr = decode_arrays(resp.json())['sol_CO2w']
            return dec_arr
        except JSONDecodeError:
            raise RPLServerException(f"The server denied your request:\n\t{resp.text}")


    # def calculate_properties(self, salinity: float = 50000., NaCl: float = 100.,
    #                          KCl: float = 0., CaCl2: float = 0., temp: float = 15.6,
    #                          pres: float = 30., props: list = []) -> Any:
    #     """Calculate velocity, density, modulus and resistivity for brine.

    #     :param salinity: Salinity of the brine/water in ppm.
    #     :type salinity: float
    #     :param NaCl: Percentage of NaCl in brine/water.
    #     :type NaCl: float
    #     :param KCl: Percentage of NaCl in brine/water.
    #     :type KCl: float
    #     :param CaCl2: Percentage of CaCl2 in brine/water.
    #     :type CaCl2: float
    #     :param temp: Temperature of brine/water.
    #     :type temp: float
    #     :param pres: Pressure in brine/water.
    #     :type pres: float
    #     :param props: List of brine/water properties to calculate and return.
    #     :type props: list[str]
    #     :return: Dictionary of calculated brine/water properties.
    #     :rtype: dict
    #     
    #     """
    #     self.props = {
    #         'salinity': salinity,
    #         'NaCl'    : NaCl,
    #         'KCl'     : KCl,
    #         'CaCl2'   : CaCl2,
    #         'temp'    : temp,
    #         'pres'    : pres,
    #         'props'   : props
    #     }
    #     enc_arr = encode_arrays(['salinity', 'NaCl', 'KCl', 'CaCl2', 'temp', 'pres', 'props'],
    #                             [salinity, NaCl, KCl, CaCl2, temp, pres, props])
    #     resp = self._post('calculate_properties/', data=enc_arr)
    #     if not self._is_authentic(resp):
    #         raise RPLUserCredentialsDeniedException('User credentials were denied by the server.')
    #     self.calculated_properties = decode_arrays(resp.json())
    #     return self.calculated_properties

    # def velocity_density_H2O_CO2(self, temp: float = 60., pres: float = 100., gwr: float = 0.5):
    #     self.props = {
    #         'temp': temp,
    #         'pres': pres,
    #         'gwr' : gwr
    #     }
    #     enc_arr = encode_arrays(['temp', 'pres', 'gwr'], [temp, pres, gwr])
    #     resp = self._post('velocity_density_H2O_CO2/', data=enc_arr)
    #     if not self._is_authentic(resp):
    #         raise RPLUserCredentialsDeniedException('User credentials were denied by the server.')
    #     self.calculated_properties = decode_arrays(resp.json())
    #     return self.calculated_properties

    # def viscosity(self, salinity: float = 50000., temp: float = 60.):
    #     self.props = {
    #         'salinity': salinity,
    #         'temp': temp
    #     }
    #     enc_arr = encode_arrays(['salinity', 'temp'], [salinity, temp])
    #     resp = self._post('viscosity/', data=enc_arr)
    #     if not self._is_authentic:
    #         raise RPLUserCredentialsDeniedException('User credentials were denied by the server.')
    #     self.calculate_properties = decode_arrays(resp.json())
    #     return self.calculate_properties

    # def solubility_gwr(self, salinity: float = 50000., temp: float = 60., pres: float = 100.):
    #     self.props = {
    #         'salinity': salinity,
    #         'temp': temp,
    #         'pres': pres
    #     }
    #     enc_arr = encode_arrays(['salinity', 'temp', 'pres'], [salinity, temp, pres])
    #     resp = self._post('solubility_gwr/', data=enc_arr)
    #     if not self._is_authentic:
    #         raise RPLUserCredentialsDeniedException('User credentials were denied by the server.')
    #     self.calculate_properties = decode_arrays(resp.json())
    #     return self.calculate_properties

    # def resistivity(self, salinity: float = 50000., temp: float = 60.):
    #     self.props = {
    #         'salinity': salinity,
    #         'temp': temp
    #     }
    #     enc_arr = encode_arrays(['salinity', 'temp'], [salinity, temp])
    #     resp = self._post('resistivity/', data=enc_arr)
    #     if not self._is_authentic(resp):
    #         raise RPLUserCredentialsDeniedException('User credentials were denied by the server.')
    #     self.calculated_properties = decode_arrays(resp.json())
    #     return self.calculated_properties

    # def saturated_vapor_pres_temp(self, temp: float = 15.6, pres: float = 39.0):
    #     self.props = {
    #         'temp': temp,
    #         'pres': pres,
    #     }
    #     enc_arr = encode_arrays(['temp', 'pres'], [temp, pres])
    #     resp = self._post('saturated_vapor_pres_temp/', data=enc_arr)
    #     if not self._is_authentic(resp):
    #         raise RPLUserCredentialsDeniedException('User credentials were denied by the server.')
    #     self.calculated_properties = decode_arrays(resp.json())
    #     return self.calculated_properties

    # def plot(self, plot_type='basic', xvar: str = 'temp', yvars: list = ['Vw', 'rho_w', 'Kw'],
    #          xlabel: str = '', ylabels: list = [], titles: list = [], suptitle: str = '',
    #          colors: list = ['b', 'r', 'g'], show: bool = False) -> None:
    #     """Brine method to quickly visualize calculated brine/water properties.
    #     
    #     :param plot_type: Optional
    #     :type plot_type: str

    #     """
    #     plt.style.use('seaborn')
    #     if self.calculated_properties is not None:
    #         if plot_type == 'basic':
    #             fig, axs = plt.subplots(len(yvars), 1, sharex=True)
    #             for i, y in enumerate(yvars):
    #                 axs[i].plot(self.props[xvar], self.calculated_properties[y], color=colors[i])
    #                 if ylabels:
    #                     axs[i].set_ylabel(ylabels[i], color=colors[i])
    #                 else:
    #                     axs[i].set_ylabel(y, color=colors[i])
    #                 axs[i].grid(True)
    #                 if i+1 == len(yvars):
    #                     if xlabel:
    #                         axs[i].set_xlabel(xlabel)
    #                     else:
    #                         axs[i].set_xlabel(xvar)
    #                 if titles:
    #                     axs[i].set_title(titles[i])
    #             if suptitle:
    #                 fig.suptitle(suptitle, y=0.99, fontsize='x-large')
    #             if show:
    #                 plt.show()
    #     else:
    #         print('No properties have been calculated. '
    #               'Try calling Brine.calculate_properties() before plotting.')

    #     return None