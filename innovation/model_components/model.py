from decimal import Decimal

import numpy as np
import pandas as pd

from innovation.models import Order
from minio_utils import get_file_from_minio


class Model:
    constant = Decimal('0.446021')
    c1 = Decimal('0.051499')
    x1_c1 = Decimal('0.399772')
    x4_c1 = Decimal('0.420848')
    x11_c1 = Decimal('0.346955')
    x15_c1 = Decimal('0.40765')
    x16_c1 = Decimal('0.35787')

    c4 = Decimal('0.116825')
    x5_c4 = Decimal('-0.493432')
    x14_c4 = Decimal('0.667676')
    x16_c4 = Decimal('-0.516003')

    def __init__(self, filename):
        self.data_filename = filename

    def get_dataframe(self):
        user_data_file_obj = get_file_from_minio(self.data_filename).read()
        df = pd.read_excel(user_data_file_obj)
        # df.fillna(0, inplace=True)
        return df

    def get_convolution(self, df=None):
        convolution = {}
        if df is None:
            df = self.get_dataframe()

        for i, col in enumerate(list(df.columns)[1:], start=1):
            avg_col = df[col].mean()
            convolution[f'x{i}'] = Decimal(avg_col)

        return convolution

    def get_row(self, start=None, stop=None):
        col_names = ['x1', 'x4', 'x5', 'x7', 'x11', 'x14', 'x15', 'x16']
        df = self.get_dataframe()
        df['Год'] = [int(val) for val in list(df['Год'].values)]
        if start and stop:
            df_rows_interval = df.loc[
                (df['Год'] >= int(start)) & (df['Год'] <= int(stop))
            ]
            df_row = self.get_convolution(df_rows_interval)
            row = {col: Decimal(df_row[col]) for col in col_names}

        elif start and not stop:
            df_row = df.loc[df['Год'] == int(start)]
            df_row.fillna(0, inplace=True)
            df_row = list(df_row.values[0])
            row = {col: Decimal(df_row[int(col[1:])]) for col in col_names}

        elif stop and not start:
            raise Exception("Stop year provided without start year")

        else:
            row = self.get_convolution()
            row = {k: v for k, v in row.items() if k in col_names}

        return row

    def calculate_y(self):
        convolution = self.get_convolution()
        y = self.constant + self.c1 * (
            self.x1_c1 * convolution['x1'] + self.x4_c1 * convolution['x4'] +
            self.x15_c1 * convolution['x15'] + self.x16_c1 * convolution['x16']
        ) + self.c4 * (
            self.x5_c4 * convolution['x5'] + self.x14_c4 * convolution['x14'] +
            self.x16_c4 * convolution['x16']
        )
        return y

    def get_cluster(self, method=None, **kwargs):
        if method == Order.YEAR:
            row = self.get_row(start=kwargs.get('year_start'))
        elif method == Order.INTERVALS:
            row = self.get_row(
                start=kwargs.get('year_start'), stop=kwargs.get('year_stop')
            )
        else:
            row = self.get_row()

        clusters = {
            '1': {
                'x1': Decimal('605.563704'),
                'x4': Decimal('74.1007977'),
                'x5': Decimal('10.9912602'),
                'x7': Decimal('12.0261736'),
                'x11': Decimal('3.88481466'),
                'x14': Decimal('2.34036013'),
                'x15': Decimal('2.73474355'),
                'x16': Decimal('21.0625'),
            },
            '2': {
                'x1': Decimal('2036.70322'),
                'x4': Decimal('128.053402'),
                'x5': Decimal('12.6208238'),
                'x7': Decimal('22.9470241'),
                'x11': Decimal('4.65826331'),
                'x14': Decimal('11.9321632'),
                'x15': Decimal('7.83429687'),
                'x16': Decimal('28.5'),
            },
            '3': {
                'x1': Decimal('5350.08'),
                'x4': Decimal('228.594302'),
                'x5': Decimal('29.814385'),
                'x7': Decimal('34.5612084'),
                'x11': Decimal('11.0855555'),
                'x14': Decimal('8.79057304'),
                'x15': Decimal('11.6689716'),
                'x16': Decimal('94.5'),
            }
        }
        clasters_dists = {'1': 0, '2': 0, '3': 0}
        for cl_name, cl_centroid in clusters.items():
            dist = np.linalg.norm(
                np.array(list(row.values())) -
                np.array(list(clusters[cl_name].values()))
            )
            clasters_dists[cl_name] = dist

        for cl_name, dist in clasters_dists.items():
            if dist == min([val for val in clasters_dists.values()]):
                return cl_name, dist, row

        # counters = {'1': [], '2': [], '3': []}
        # for x, x_val in row.items():
        #     dists = []
        #     for cl, cl_c in clusters.items():
        #         dist = np.linalg.norm(x_val - cl_c[x])
        #         # dist = distance.euclidean([x_val], [cl_c[x]])
        #         dists.append(dist)
        #
        #     clust_num = dists.index(min(dists)) + 1
        #     counters[str(clust_num)].append(x)
        #
        # for k, v in counters.items():
        #     if len(v) == max([len(c) for c in counters.values()]):
        #         return k, v
