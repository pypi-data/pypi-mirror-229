import geopandas


def get_recording_coordinates(shp_path, geojson_path="tmp.geojson"):
    shp_files_to_geojson(shp_path)
    recording_coordinates_df = geojson_to_id_table(geojson_path)
    return recording_coordinates_df


def get_recording_data(shp_path, geojson_path="tmp.geojson"):
    shp_files_to_geojson(shp_path)
    recording_data_df = geojson_to_records_by_season_table(geojson_path)
    return recording_data_df


def geojson_to_id_table(geojson_path: str):
    geopandas_df = geopandas.read_file(geojson_path)
    geopandas_coordinates = geopandas_df.get_coordinates()
    geopandas_df[["X", "Y"]] = geopandas_coordinates
    return geopandas_df.loc[:, ["id", "X", "Y"]]


def geojson_to_records_by_season_table(geojson_path):
    geopandas_df = geopandas.read_file(geojson_path)
    return geopandas_df.loc[:, ["Temporada", "id", "Estatus", "Pres-Ause", "Cant Voc", "Tasa Voc"]]


def shp_files_to_geojson(raw_data: str, output_path: str = "tmp.geojson"):
    geopandas_df = geopandas.read_file(raw_data)
    geopandas_df.to_file(output_path, driver="GeoJSON")
