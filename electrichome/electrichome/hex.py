import pprint
from dataclasses import dataclass
from enum import Enum
import calendar
import math
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pvlib
import pytz
from pathlib import Path
from typing import NamedTuple

from .credentials import NREL_API_KEY, NREL_API_EMAIL

# Define a few permanent constants
JOULES_PER_KWH = 3.6e+6
JOULES_PER_MEGAJOULE = 1e6
SECONDS_PER_HOUR = 3600
AIR_VOLUMETRIC_HEAT_CAPACITY = 1200  # Energy in joules per cubic meter of air per degree K. (J/m3/K)

SIMULATION_YEAR = "tmy"

heating_types = {
    "natural_gas": {
        "value": "natural_gas",
        "label": "Natural Gas",
        "efficiency": 0.8,
        "cost_per_kwh": lambda kwh : (kwh/29.3) * 1.0092,
        "co2_per_kwh": lambda kwh : (kwh/29.3) * 0.0053
    },
    "heat_pump": {
        "value": "heat_pump",
        "label": "Heat Pump",
        "efficiency": 4,
        "cost_per_kwh": lambda kwh : kwh * 0.1921,
        "co2_per_kwh": lambda kwh : kwh * 0.000305
    }
}

@dataclass
class HomeCharacteristics:
    latitude: float
    longitude: float
    heating_setpoint_c: int
    cooling_setpoint_c: int
    hvac_capacity_w: int
    conditioned_floor_area_sq_m: int
    ceiling_height_m: int
    wall_insulation_r_value_imperial: int
    ach50: int
    south_facing_window_size_sq_m: int
    window_solar_heat_gain_coefficient: int
    heating_type: int

    @property
    def building_volume_cu_m(self) -> int:
        return self.conditioned_floor_area_sq_m * self.ceiling_height_m

    @property
    def building_perimeter_m(self) -> float:
        # Assume the building is a 1-story square
        return math.sqrt(self.conditioned_floor_area_sq_m) * 4

    @property
    def surface_area_to_area_sq_m(self) -> float:
        # Surface area exposed to air = wall area + roof area (~= floor area, for 1-story building)
        return self.building_perimeter_m * self.ceiling_height_m + self.conditioned_floor_area_sq_m

    @property
    def ach_natural(self) -> float:
        # "Natural" air changes per hour can be roughly estimated from ACH50 with an "LBL_FACTOR"
        # https://building-performance.org/bpa-journal/ach50-achnat/
        LBL_FACTOR = 17
        return self.ach50 / LBL_FACTOR

    @property
    def wall_insulation_r_value_si(self) -> float:
        # The R-values you typically see on products in the US will be in imperial units (ft^2 °F/Btu)
        # But our calculations need SI units (m^2 °K/W)
        return self.wall_insulation_r_value_imperial / 5.67  # SI units: m^2 °K/W

    @property
    def building_heat_capacity(self) -> int:
        # Building heat capacity
        # How much energy (in kJ) do you have to put into the building to change the indoor temperature by 1 degree?
        # Heat capacity unit: Joules per Kelvin degree (kJ/K)
        # A proper treatment of these factors would include multiple thermal mass components,
        # because the walls, air, furniture, foundation, etc. all store heat differently.
        # More info: https://www.greenspec.co.uk/building-design/thermal-mass/
        HEAT_CAPACITY_FUDGE_FACTOR = 1e5
        return self.building_volume_cu_m * HEAT_CAPACITY_FUDGE_FACTOR


def get_solar_timeseries(home):

    solar_weather_timeseries, solar_weather_metadata = pvlib.iotools.get_psm3(
        latitude=home.latitude,
        longitude=home.longitude,
        names=SIMULATION_YEAR,
        api_key=NREL_API_KEY,
        email=NREL_API_EMAIL,
        map_variables=True,
        leap_day=True,
    )

    solar_position_timeseries = pvlib.solarposition.get_solarposition(
        time=solar_weather_timeseries.index,
        latitude=home.latitude,
        longitude=home.longitude,
        altitude=100, # Assume close to sea level, this doesn't matter much
        temperature=solar_weather_timeseries["temp_air"],
    )

    window_irradiance = pvlib.irradiance.get_total_irradiance(
        90, # Window tilt (90 = vertical)
        180, # Window compass orientation (180 = south-facing)
        solar_position_timeseries.apparent_zenith,
        solar_position_timeseries.azimuth,
        solar_weather_timeseries.dni,
        solar_weather_timeseries.ghi,
        solar_weather_timeseries.dhi,
    )

    return solar_weather_timeseries, window_irradiance

# We're modeling the effect of three external sources of energy that can affect the temperature of the home:
#  1. Conductive heat gain or loss through contact with the walls and roof (we ignore the floor), given outdoor temperature
#  2. Air change heat gain or loss through air changes between air in the house and outside, given outdoor temperature
#  3. Radiant heat gain from sun coming in south-facing windows

# We then model our HVAC system as heating/cooling/off depending on whether the temperature is above or below desired setpoints

def calculate_next_timestep(
    timestamp,
    indoor_temperature_c,
    outdoor_temperature_c,
    irradiance,
    home: HomeCharacteristics,
    dt=pd.Timedelta(minutes=10) # Defaulting to a timestep of 10 minute increments
):
    '''
    This function calculates the ΔT (the change in indoor temperature) during a single timestep given:
      1. Previous indoor temperature
      2. Current outdoor temperature (from historical weather data)
      3. Current solar irradiance through south-facing windows (from historical weather data)
      4. Home and HVAC characteristics
    '''

    temperature_difference_c = outdoor_temperature_c - indoor_temperature_c

    # Calculate energy in to building

    # 1. Energy conducted through walls & roof (in Joules, J)
    # Conduction
    # Q = U.A.dT, where U = 1/R
    # Convection:
    # Q = m_dot . Cp * dT <=> Q = V_dot * Cv * dT (Cv = Rho * Cp)

    power_in_through_surface_w = (
        temperature_difference_c * home.surface_area_to_area_sq_m / home.wall_insulation_r_value_si
    )
    energy_from_conduction_j = power_in_through_surface_w * dt.seconds

    # 2. Energy exchanged through air changes with the outside air (in Joules, J)
    air_change_volume = (
        dt.seconds * home.building_volume_cu_m * home.ach_natural / SECONDS_PER_HOUR
    )
    energy_from_air_change_j = (
        temperature_difference_c * air_change_volume * AIR_VOLUMETRIC_HEAT_CAPACITY
    )

    # 3. Energy radiating from the sun in through south-facing windows (in Joules, J)
    energy_from_sun_j = (
        home.south_facing_window_size_sq_m
        * home.window_solar_heat_gain_coefficient
        * irradiance
        * dt.seconds
    )

    # 4. Energy added or removed by the HVAC system (in Joules, J)
    # HVAC systems are either "on" or "off", so the energy they add or remove at any one time equals their total capacity
    if indoor_temperature_c < home.heating_setpoint_c:
        hvac_mode = "heating"
        energy_from_hvac_j = home.hvac_capacity_w * dt.seconds
    elif indoor_temperature_c > home.cooling_setpoint_c:
        hvac_mode = "cooling"
        energy_from_hvac_j = -home.hvac_capacity_w * dt.seconds
    else:
        hvac_mode = "off"
        energy_from_hvac_j = 0

    total_energy_in_j = (
        energy_from_conduction_j
        + energy_from_air_change_j
        + energy_from_sun_j
        + energy_from_hvac_j
    )

    # ΔT is the change in indoor temperature during this timestep resulting from the total energy input
    delta_t = total_energy_in_j / home.building_heat_capacity

    hvac_overall_system_efficiency = home.heating_type["efficiency"]

    return pd.Series(
        {
            "timestamp": timestamp,
            "temperature_difference_c": temperature_difference_c,
            "Conductive energy (J)": energy_from_conduction_j,
            "Air change energy (J)": energy_from_air_change_j,
            "Radiant energy (J)": energy_from_sun_j,
            "HVAC energy (J)": energy_from_hvac_j,
            "hvac_mode": hvac_mode,
            "Net energy xfer": total_energy_in_j,
            "ΔT": delta_t,
            "Outdoor Temperature (C)": outdoor_temperature_c,
            "Indoor Temperature (C)": indoor_temperature_c + delta_t,
            # Actual energy consumption from the HVAC system:
            "HVAC energy use (kWh)": abs(energy_from_hvac_j) / (JOULES_PER_KWH * hvac_overall_system_efficiency)
        }
    )

def get_monthly_energy_balance(home, solar_weather_timeseries, window_irradiance):
    # Since we're starting in January, let's assume our starting temperature is the heating setpoint
    previous_indoor_temperature_c = home.heating_setpoint_c

    timesteps = []
    for timestamp in solar_weather_timeseries.index:
        new_timestep = calculate_next_timestep(
            timestamp=timestamp,
            indoor_temperature_c=previous_indoor_temperature_c,
            outdoor_temperature_c=solar_weather_timeseries.loc[timestamp].temp_air,
            irradiance=window_irradiance.loc[timestamp].poa_direct,
            home=home,
        )
        timesteps.append(new_timestep)
        previous_indoor_temperature_c = new_timestep["Indoor Temperature (C)"]


    baby_energy_model = pd.DataFrame(timesteps)
    # baby_energy_model

    # For each month, let's look at the overall energy balance:
    # Where is the thermal energy in the house coming from, and where is it going to?
   # energy_transfer_columns = [col for col in baby_energy_model.columns if col.endswith("(J)")]
    get_month=lambda idx: baby_energy_model.loc[idx]['timestamp'].month
   # monthly_energy_balance_mj = baby_energy_model.groupby(by=get_month)[energy_transfer_columns].sum() / JOULES_PER_MEGAJOULE

   # monthly_energy_balance_mj['month'] = monthly_energy_balance_mj.index.map(lambda month_idx: f'{month_idx:0=2} - {calendar.month_name[month_idx]}')

    monthly_energy_use_kwh = baby_energy_model.groupby(by=get_month)["HVAC energy use (kWh)"].sum() 
  #  monthly_energy_balance_tidy = monthly_energy_use_kwh.melt(id_vars='month')

    # print("------------------ baby_energy_model - %s" % type(baby_energy_model))
    # print(baby_energy_model)
    # print("------------------ monthly_energy_balance_mj - %s" % type(monthly_energy_balance_mj))
    # print(monthly_energy_balance_mj)
    # # print("------------------ monthly")
    # # print(monthly_energy_balance_mj['month'])
    # print("------------------ monthly_energy_balance_tidy - %s" % type(monthly_energy_balance_tidy))
    # print(monthly_energy_balance_tidy)
    # print("------------------")

    return monthly_energy_use_kwh.to_dict()
    #return monthly_energy_balance_tidy.to_dict()

def get_yearly_energy_usage(monthly_energy_balance):
    energy_usage_list = []
    for key in monthly_energy_balance["variable"]:
        value = monthly_energy_balance["variable"][key]
        if ( value == "HVAC energy (kWh)"):
            energy_usage_list.append(monthly_energy_balance["value"][key])
    
    yearly_energy_usage = sum(energy_usage_list)

    return yearly_energy_usage