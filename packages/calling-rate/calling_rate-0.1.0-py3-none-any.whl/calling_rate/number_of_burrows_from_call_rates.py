from matplotlib import path
from scipy.spatial import ConvexHull
import numpy as np
import pandas as pd


def _get_burrow_coordinates():
    burrow_geci_data_path = "tests/data/coordenadas_madrigueras_geci.csv"
    burrow_geci_data = pd.read_csv(burrow_geci_data_path)
    burrow_jm_data_path = "tests/data/coordenadas_madrigueras_jm.csv"
    burrow_jm_data = pd.read_csv(burrow_jm_data_path)
    merged_data = pd.concat([burrow_geci_data[["X", "Y"]], burrow_jm_data[["X", "Y"]]])
    return merged_data


def _get_number_of_burrows_in_burrow_area():
    return _get_burrow_coordinates().shape[0]


def _get_burrow_area():
    burrow_points = _get_burrow_coordinates()
    return ConvexHull(burrow_points).volume


def get_density_in_burrow_area():
    return _get_number_of_burrows_in_burrow_area() / _get_burrow_area()


def _get_burrow_polygon():
    burrow_points = _get_burrow_coordinates()
    hull = ConvexHull(burrow_points)
    return burrow_points.iloc[hull.vertices, :]


def is_inside_burrow_area():
    return path.Path(_get_burrow_polygon()).contains_points(get_recorder_coordinates())


def get_call_rate_in_burrow_area():
    is_recorder_inside = is_inside_burrow_area()
    recorder_data = pd.read_csv(recorder_data_path)
    return recorder_data.loc[is_recorder_inside, "Tasa_Voc"].mean()


def get_call_rate_in_recorder_area():
    recorder_data = pd.read_csv(recorder_data_path)
    return recorder_data["Tasa_Voc"].mean()


def get_density_in_recorder_area():
    return (
        get_density_in_burrow_area()
        * get_call_rate_in_recorder_area()
        / get_call_rate_in_burrow_area()
    )


recorder_data_path = "tests/data/puntos_grabaciones_estimacion_poblacion.csv"


def get_recorder_coordinates():
    return pd.read_csv(recorder_data_path).loc[:, ["Coordenada_X", "Coordenada_Y"]]


def get_area_for_each_recorder():
    recorder_data = pd.read_csv(recorder_data_path)
    dx = np.median(np.diff(recorder_data["Coordenada_X"].sort_values().unique()))
    dy = np.median(np.diff(recorder_data["Coordenada_Y"].sort_values().unique()))
    dA = dx * dy
    return dA


def get_number_of_recorders():
    number_of_recorders = pd.read_csv(recorder_data_path).shape[0]
    return number_of_recorders


def get_recorder_area():
    return get_number_of_recorders() * get_area_for_each_recorder()


def get_number_of_burrows_in_recorder_area():
    return get_density_in_recorder_area() * get_recorder_area()
