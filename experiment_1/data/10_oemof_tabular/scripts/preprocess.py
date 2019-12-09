import os

import pandas as pd


# Set paths
abspath = os.path.abspath(os.path.dirname(__file__))

data_raw_path = os.path.join(abspath, '../..', '00_raw', 'Data', 'In', 'v0.01')

data_preprocessed_path = os.path.join(abspath, '..', 'data')

scalars = pd.read_csv(os.path.join(data_raw_path, 'Scalars.csv'), header=0)

bus_list = [
    'AT-el-bus',
    'BE-el-bus',
    'CH-el-bus',
    'CZ-el-bus',
    'DE-el-bus',
    'DK-el-bus',
    'FR-el-bus',
    'IT-el-bus',
    'LU-el-bus',
    'NL-el-bus',
    'PL-el-bus',
]

link_list = [
    'AT-CH',
    'AT-CZ',
    'AT-IT',
    'BE-FR',
    'BE-LU',
    'BE-NL',
    'CH-FR',
    'CH-IT',
    'CZ-PL',
    'DE-AT',
    'DE-BE',
    'DE-CH',
    'DE-CZ',
    'DE-DK',
    'DE-FR',
    'DE-LU',
    'DE-NL',
    'DE-PL',
    'DK-NL',
    'FR-IT',
    'FR-LU',
]

datetimeindex = pd.DatetimeIndex(start='2019-01-01', freq='H', periods=8760)


def create_bus_file():
    bus = pd.DataFrame(columns=['name', 'type', 'balanced'])

    bus['name'] = bus_list

    bus['type'] = 'bus'

    bus['balanced'] = 'true'

    bus.to_csv(os.path.join(data_preprocessed_path, 'elements', 'bus.csv'), index=False)


def create_shortage_file():
    shortage = pd.DataFrame(
        columns=[
            'name',
            'type',
            'carrier',
            'tech',
            'capacity',
            'bus',
            'marginal_cost',
            'profile',
            'output_parameters',
        ]
    )
    shortage['name'] = ['-'.join(bus.split('-')[:2] + ['shortage']) for bus in bus_list]

    shortage['bus'] = bus_list

    shortage['type'] = 'dispatchable'

    shortage['carrier'] = 'shortage'

    shortage['tech'] = 'shortage'

    shortage['profile'] = 1

    shortage['output_parameters'] = '{}'

    shortage['marginal_cost'] = 5000

    shortage.to_csv(
        os.path.join(data_preprocessed_path, 'elements', 'shortage.csv'), index=False,
    )


def create_curtailment_file():
    curtailment = pd.DataFrame(
        columns=[
            'name',
            'type',
            'carrier',
            'tech',
            'capacity',
            'bus',
            'marginal_cost',
            'profile',
            'output_parameters',
        ]
    )
    curtailment['name'] = ['-'.join(bus.split('-')[:2] + ['curtailment']) for bus in bus_list]

    curtailment['bus'] = bus_list

    curtailment['type'] = 'excess'

    curtailment['carrier'] = 'curtailment'

    curtailment['tech'] = 'curtailment'

    curtailment['profile'] = 1

    curtailment['output_parameters'] = '{}'

    curtailment['marginal_cost'] = 0

    curtailment.to_csv(
        os.path.join(data_preprocessed_path, 'elements', 'curtailment.csv'), index=False,
    )


def create_load_file():
    load = pd.DataFrame(columns=['name', 'amount', 'profile', 'type', 'bus'])

    load['name'] = ['-'.join(bus.split('-')[:2] + ['load']) for bus in bus_list]

    scalars_load = scalars.loc[scalars['Parameter'] == 'Energy_FinalEnergy_Electricity']

    load['amount'] = scalars_load['Value'].values

    load['profile'] = ['{}-el-load-profile'.format(bus.split('-')[0]) for bus in bus_list]

    load['type'] = 'load'

    load['bus'] = bus_list

    load.to_csv(os.path.join(data_preprocessed_path, 'elements', 'load.csv'), index=False)


def combine_profiles(raw_profile_path, column_name):
    profile_file_list = os.listdir(raw_profile_path)

    profile_list = []
    for file in profile_file_list:
        region = file.split('_')[1]

        print("Load profile for region {}".format(region))

        raw_load_profile = pd.read_csv(os.path.join(raw_profile_path, file), index_col=0)

        load_profile = raw_load_profile.iloc[:, 0]

        load_profile.name = region + '-' + column_name

        profile_list.append(load_profile)

    profile_df = pd.concat(profile_list, axis=1)

    profile_df = profile_df.set_index(datetimeindex, drop=True)

    profile_df.index.name = 'timeindex'
    profile_df = profile_df.iloc[:5]
    return profile_df


def create_load_profiles():
    raw_load_profile_path = os.path.join(data_raw_path, 'Energy', 'FinalEnergy', 'Electricity')

    load_profile_df = combine_profiles(raw_load_profile_path, 'el-load-profile')

    load_profile_df.to_csv(os.path.join(data_preprocessed_path, 'sequences', 'load_profile.csv'))


def create_volatile_file():
    volatile = pd.DataFrame(
        columns=[
            'name',
            'type',
            'carrier',
            'tech',
            'capacity',
            'capacity_cost',
            'bus',
            'marginal_cost',
            'profile',
            'output_parameters',
        ]
    )

    # wind onshore
    wind_onshore = volatile.copy()

    scalars_wind_onshore = scalars.loc[
        scalars['Parameter'] == 'EnergyConversion_Capacity_Electricity_Wind_Onshore'
    ]

    wind_onshore['name'] = ['-'.join(bus.split('-')[:2] + ['wind-onshore']) for bus in bus_list]

    wind_onshore['carrier'] = 'wind'

    wind_onshore['tech'] = 'onshore'

    wind_onshore['capacity'] = scalars_wind_onshore['Value'].values

    wind_onshore['bus'] = bus_list

    wind_onshore['profile'] = [
        '-'.join(bus.split('-')[:2] + ['wind-onshore-profile']) for bus in bus_list
    ]

    # wind offshore
    wind_offshore = volatile.copy()

    scalars_wind_offshore = scalars.loc[
        scalars['Parameter'] == 'EnergyConversion_Capacity_Electricity_Wind_Offshore'
    ]

    wind_offshore['name'] = ['-'.join(bus.split('-')[:2] + ['wind-offshore']) for bus in bus_list]

    wind_offshore['carrier'] = 'wind'

    wind_offshore['tech'] = 'offshore'

    wind_offshore['capacity'] = scalars_wind_offshore['Value'].values

    wind_offshore['bus'] = bus_list

    wind_offshore['profile'] = [
        '-'.join(bus.split('-')[:2] + ['wind-offshore-profile']) for bus in bus_list
    ]

    # solarpv
    # name,carrier,tech,capacity,capacity_cost,bus,marginal_cost,profile,output_parameters
    solarpv = volatile.copy()

    scalars_solarpv = scalars.loc[
        scalars['Parameter'] == 'EnergyConversion_Capacity_Electricity_Solar_PV'
    ]

    solarpv['name'] = ['-'.join(bus.split('-')[:2] + ['solarpv']) for bus in bus_list]

    solarpv['carrier'] = 'solar'

    solarpv['tech'] = 'pv'

    solarpv['capacity'] = scalars_solarpv['Value'].values

    solarpv['bus'] = bus_list

    solarpv['profile'] = ['-'.join(bus.split('-')[:2] + ['solar-pv-profile']) for bus in bus_list]

    volatile = pd.concat([wind_onshore, wind_offshore, solarpv], axis=0)

    volatile['type'] = 'volatile'

    volatile['marginal_cost'] = 0

    volatile['output_parameters'] = '{}'

    volatile.to_csv(
        os.path.join(data_preprocessed_path, 'elements', 'volatile.csv'), index=False,
    )


def create_volatile_profiles():
    raw_wind_onshore_profile_paths = os.path.join(
        data_raw_path, 'Energy', 'SecondaryEnergy', 'Wind', 'Onshore'
    )

    wind_onshore_profile_df = combine_profiles(
        raw_wind_onshore_profile_paths, 'el-wind-onshore-profile'
    )

    raw_wind_offshore_profile_paths = os.path.join(
        data_raw_path, 'Energy', 'SecondaryEnergy', 'Wind', 'Offshore'
    )

    wind_offshore_profile_df = combine_profiles(
        raw_wind_offshore_profile_paths, 'el-wind-offshore-profile'
    )

    raw_solar_pv_profile_paths = os.path.join(
        data_raw_path, 'Energy', 'SecondaryEnergy', 'Solar', 'PV'
    )

    solar_pv_profile_df = combine_profiles(raw_solar_pv_profile_paths, 'el-solar-pv-profile')

    volatile_df = pd.concat(
        [wind_onshore_profile_df, wind_offshore_profile_df, solar_pv_profile_df], axis=1, sort=True
    )

    volatile_df.to_csv(os.path.join(data_preprocessed_path, 'sequences', 'volatile_profile.csv'))


def create_link_file():
    link = pd.DataFrame(
        columns=['name', 'type', 'capacity', 'capacity_cost', 'loss', 'from_bus', 'to_bus']
    )
    transmission_loss_per_100km = scalars.loc[
        scalars['Parameter'] == 'Transmission_Losses_Electricity_Grid'
    ]

    transmission_length = scalars.loc[
        scalars['Parameter'] == 'Transmission_Length_Electricity_Grid'
    ]

    transmission_capacity = scalars.loc[
        scalars['Parameter'] == 'Transmission_Length_Electricity_Grid'
    ]

    link['name'] = link_list

    link['type'] = 'link'

    link['capacity'] = transmission_capacity['Value'].values

    link['loss'] = (
        transmission_length['Value'].values * 0.01 * transmission_loss_per_100km['Value'].values
    )

    link['from_bus'] = [link.split('-')[0] + '-el-bus' for link in link_list]

    link['to_bus'] = [link.split('-')[1] + '-el-bus' for link in link_list]

    link.to_csv(
        os.path.join(data_preprocessed_path, 'elements', 'link.csv'), index=False,
    )


if __name__ == '__main__':
    create_bus_file()
    create_shortage_file()
    create_curtailment_file()
    create_load_file()
    create_load_profiles()
    create_volatile_file()
    create_volatile_profiles()
    create_link_file()
