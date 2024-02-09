from django.shortcuts import render
from django import forms

from .location import get_lat_long
from .hex import HomeCharacteristics, get_solar_timeseries, get_monthly_energy_balance
from . import conversions


class MyForm(forms.Form):
    zip_code = forms.Field(label='What is your zip code?', initial="10001")
    square_footage = forms.DecimalField(label='What is the square footage of your conditioned home?', initial=2000)
    ceiling_height = forms.DecimalField(label='How high are your ceilings (in feet), on average?', initial=9)

    air_change_rate = forms.DecimalField(label='What is the Air Change Rate per hour?', initial=16)
    wall_insulation_rvalue = forms.DecimalField(label='What is your wall insulation R-Value?', initial=10)

    heat_temperature = forms.DecimalField(label='What is your thermostat to in the winter? (in F)')
    cool_temperature = forms.DecimalField(label='What is your thermostat to in the summer? (F)')
    home_heat_capacity = forms.DecimalField(label='How much energy (in kJ) do you have to put into the building to change the indoor temperature by 1 degree?', initial=10000)
    heating_type = forms.ChoiceField(choices=[('electric_radiator', 'Electric Radiator'), ('high_efficiency_heat_pump', 'High Efficiency Heat Pump')], initial='electric_radiator', label='Heating Type')
    south_facing_window_size = forms.DecimalField(label='How many square feet total are the south-facing windows?', initial=100)
    window_solar_heat_gain_coefficient = forms.DecimalField(label='Window Solar Heat Gain Coefficient', initial=0.5)

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
                'air_change_rate': float(form.cleaned_data['air_change_rate']),
                'wall_insulation_rvalue': float(form.cleaned_data['wall_insulation_rvalue']),
                'home_heat_capacity': float(form.cleaned_data['home_heat_capacity']),
                'heating_type': form.cleaned_data['heating_type'],
                'south_facing_window_size': conversions.squareft_to_squaremeter(form.cleaned_data['south_facing_window_size']),
                'window_solar_heat_gain_coefficient': float(form.cleaned_data['window_solar_heat_gain_coefficient']),
            }
            calculated_data = _do_the_thing(submitted_data)
            print(calculated_data)
    else:
        form = MyForm()

    return render(request, 'base_form.html', {
        'form': form,
        'submitted_data': submitted_data,
        'calculated_data': calculated_data
    })


def _do_the_thing(submitted_data):
    zip_code = submitted_data['zip_code']
    lat, long = get_lat_long(zip_code)

    home = HomeCharacteristics(latitude=float(lat),
                        longitude=float(long),
                        heating_setpoint_c=submitted_data['heat_temperature'],
                        cooling_setpoint_c=submitted_data['cool_temperature'],
                        hvac_capacity_w=submitted_data['home_heat_capacity'],
                        hvac_overall_system_efficiency=1,
                        conditioned_floor_area_sq_m=submitted_data['square_footage'],
                        ceiling_height_m=conversions.feet_to_meters(submitted_data['ceiling_height']),
                        wall_insulation_r_value_imperial=submitted_data['wall_insulation_rvalue'],
                        ach50=submitted_data['air_change_rate'],
                        south_facing_window_size_sq_m=submitted_data['south_facing_window_size'],
                        window_solar_heat_gain_coefficient=submitted_data['window_solar_heat_gain_coefficient']
    )

    solar_timeseries, window_irradiance = get_solar_timeseries(home)

    monthly_energy_balance = get_monthly_energy_balance(home, solar_timeseries, window_irradiance)

    return {
        'zip_code': str(zip_code),
        'latitude': lat,
        'longitude': long,
        'monthly_energy_balance': monthly_energy_balance
    }
