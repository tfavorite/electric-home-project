from django.shortcuts import render
from django import forms

from .location import get_lat_long
from .hex import HomeCharacteristics, get_solar_timeseries, get_monthly_energy_balance, get_yearly_energy_usage, heating_types
from . import conversions


class MyForm(forms.Form):
    zip_code = forms.Field(label='What is your zip code?', initial="10001")
    square_footage = forms.DecimalField(label='What is the square footage of your conditioned home?', initial=2000)
    ceiling_height = forms.DecimalField(label='How high are your ceilings (in feet), on average?', initial=9)

   # air_change_rate = forms.DecimalField(label='What is the Air Change Rate per hour?', initial=16)
   # wall_insulation_rvalue = forms.DecimalField(label='What is your wall insulation R-Value?', initial=10)

    heat_temperature = forms.DecimalField(label='What is your thermostat to in the winter? (in F)')
    cool_temperature = forms.DecimalField(label='What is your thermostat to in the summer? (F)')
   # home_heat_capacity = forms.DecimalField(label='How much energy (in kJ) do you have to put into the building to change the indoor temperature by 1 degree?', initial=10000)
   # heating_type = forms.ChoiceField(choices=[('electric_radiator', 'Electric Radiator'), ('high_efficiency_heat_pump', 'High Efficiency Heat Pump')], initial='electric_radiator', label='Heating Type')
    south_facing_window_size = forms.DecimalField(label='How many square feet total are the south-facing windows?', initial=100)
   # window_solar_heat_gain_coefficient = forms.DecimalField(label='Window Solar Heat Gain Coefficient', initial=0.5)

def my_view(request):
    submitted_data = None
    calculated_data = None

    if request.method == 'POST':
        form = MyForm(request.POST)
        if form.is_valid():
            # Handle form submission logic here
            submitted_data = {
                'square_footage': conversions.squareft_to_squaremeter(form.cleaned_data['square_footage']),
                'ceiling_height': conversions.feet_to_meters(form.cleaned_data['ceiling_height']),
                'heat_temperature': conversions.fahrenheit_to_celsius(form.cleaned_data['heat_temperature']),
                'cool_temperature': conversions.fahrenheit_to_celsius(form.cleaned_data['cool_temperature']),
                'zip_code': form.cleaned_data['zip_code'],
                # 'air_change_rate': float(form.cleaned_data['air_change_rate']),
                # 'wall_insulation_rvalue': float(form.cleaned_data['wall_insulation_rvalue']),
                # 'home_heat_capacity': float(form.cleaned_data['home_heat_capacity']),
                # 'heating_type': form.cleaned_data['heating_type'],
                'south_facing_window_size': conversions.squareft_to_squaremeter(form.cleaned_data['south_facing_window_size']),
          #      'window_solar_heat_gain_coefficient': float(form.cleaned_data['window_solar_heat_gain_coefficient']),
            }
            calculated_data = _do_the_thing(submitted_data)
       #     print(calculated_data)
    else:
        form = MyForm()

    return render(request, 'base_form.html', {
        'form': form,
        'submitted_data': submitted_data,
        'calculated_data': calculated_data
    })

AIR_CHANGE_RATE_BEFORE = 17
AIR_CHANGE_RATE_AFTER = 10

WINDOW_SOLAR_HEAT_GAIN_COEFFICIENT = 0.5
WALL_INSULATION_RVALUE = 10
HOME_HEAT_CAPACITY = 10000


def _do_the_thing(submitted_data):
    zip_code = submitted_data['zip_code']
    lat, long = get_lat_long(zip_code)

    home_before = HomeCharacteristics(latitude=float(lat),
                        longitude=float(long),
                        heating_setpoint_c=submitted_data['heat_temperature'],
                        cooling_setpoint_c=submitted_data['cool_temperature'],
                        hvac_capacity_w=HOME_HEAT_CAPACITY,
                        conditioned_floor_area_sq_m=submitted_data['square_footage'],
                        ceiling_height_m=conversions.feet_to_meters(submitted_data['ceiling_height']),
                        wall_insulation_r_value_imperial=WALL_INSULATION_RVALUE,
                        ach50=AIR_CHANGE_RATE_BEFORE,
                        south_facing_window_size_sq_m=submitted_data['south_facing_window_size'],
                        window_solar_heat_gain_coefficient=WINDOW_SOLAR_HEAT_GAIN_COEFFICIENT,
                        heating_type=heating_types["natural_gas"]
    )

    home_after = HomeCharacteristics(latitude=float(lat),
                        longitude=float(long),
                        heating_setpoint_c=submitted_data['heat_temperature'],
                        cooling_setpoint_c=submitted_data['cool_temperature'],
                        hvac_capacity_w=HOME_HEAT_CAPACITY,
                        conditioned_floor_area_sq_m=submitted_data['square_footage'],
                        ceiling_height_m=conversions.feet_to_meters(submitted_data['ceiling_height']),
                        wall_insulation_r_value_imperial=WALL_INSULATION_RVALUE,
                        ach50=AIR_CHANGE_RATE_AFTER,
                        south_facing_window_size_sq_m=submitted_data['south_facing_window_size'],
                        window_solar_heat_gain_coefficient=WINDOW_SOLAR_HEAT_GAIN_COEFFICIENT,
                        heating_type=heating_types["heat_pump"]
    )

    energy_usages = {}

    for home in [home_before, home_after]:
        solar_timeseries, window_irradiance = get_solar_timeseries(home)

        yearly_energy_usage = sum(get_monthly_energy_balance(home, solar_timeseries, window_irradiance).values())

        energy_usages[home.heating_type["value"]] = {
            "yearly_kwh" : yearly_energy_usage,
            "yearly_cost" : home.heating_type["cost_per_kwh"](yearly_energy_usage),
            "yearly_co2" : home.heating_type["co2_per_kwh"](yearly_energy_usage)
        }

    natural_gas = energy_usages[heating_types["natural_gas"]["value"]]
    heat_pump = energy_usages[heating_types["heat_pump"]["value"]]
    diff_from_before = {
        "kwh": heat_pump["yearly_kwh"] - natural_gas["yearly_kwh"],
        "cost": heat_pump["yearly_cost"] - natural_gas["yearly_cost"],
        "co2": heat_pump["yearly_co2"] - natural_gas["yearly_co2"]
    }

    return {
        "energy_usages": energy_usages,
        "difference": diff_from_before
    }
