from decimal import Decimal
from math import exp

import numpy as np
import pandas as pd

from minio_utils import get_file_from_minio


class Model:
    X1 = 'Патенты'
    X4 = 'Все активы'
    X5 = 'Гудвилл'
    X6 = 'R&D'
    X7 = 'Материальные активы'
    X11 = 'Кол-во поглощений'
    X13 = 'Доля сотрудников НИОКР'
    X14 = 'ЗП'
    X15 = 'Амортизация'
    X16 = 'Возраст'
    VARS_MAP = {
        X1: 'X1',
        X4: 'X4',
        X5: 'X5',
        X6: 'X6',
        X7: 'X7',
        X11: 'X11',
        X13: 'X13',
        X14: 'X14',
        X15: 'X15',
        X16: 'X16',
    }
    CHOICES = [
        (X1, 'Патенты'),
        (X4, 'Все активы'),
        (X5, 'Гудвилл'),
        (X6, 'R&D'),
        (X7, 'Материальные активы'),
        (X11, 'Кол-во поглощений'),
        (X13, 'Доля сотрудников НИОКР'),
        (X14, 'ЗП'),
        (X15, 'Амортизация'),
        (X16, 'Возраст'),
    ]
    logit_const = Decimal('-14.7771')
    logit_const_x1 = Decimal('0.00565429')
    logit_const_x11 = Decimal('2.00633')
    constant = Decimal('0.446021')
    c1 = Decimal('0.051499')
    x1_c1 = Decimal('0.399772')
    x4_c1 = Decimal('0.420848')
    x5_c1 = Decimal('0.279014')
    x7_c1 = Decimal('0.307363')
    x11_c1 = Decimal('0.346955')
    x14_c1 = Decimal('0.275896')
    x15_c1 = Decimal('0.40765')
    x16_c1 = Decimal('0.35787')

    c4 = Decimal('0.116825')
    x1_c4 = Decimal('0.0428447')
    x4_c4 = Decimal('0.0100262')
    x5_c4 = Decimal('-0.493432')
    x7_c4 = Decimal('0.133243')
    x11_c4 = Decimal('0.0394845')
    x14_c4 = Decimal('0.667676')
    x15_c4 = Decimal('0.1524')
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
            convolution[f'X{i}'] = Decimal(avg_col)

        return convolution

    def get_row(self, start=None, stop=None):
        col_names = [
            self.X1, self.X4, self.X5, self.X7,
            self.X11, self.X14, self.X15, self.X16
        ]
        vars_names = [self.VARS_MAP[el] for el in col_names]
        df = self.get_dataframe()
        df['Год'] = [int(val) for val in list(df['Год'].values)]
        if start and stop:
            df_rows_interval = df.loc[
                (df['Год'] >= int(start)) & (df['Год'] <= int(stop))
            ]
            df_row = self.get_convolution(df_rows_interval)
            row = {
                col: Decimal(df_row[self.VARS_MAP[col]]) for col in col_names
            }

        elif start and not stop:
            df_row = df.loc[df['Год'] == int(start)]
            df_row.fillna(0, inplace=True)
            df_row = list(df_row.values[0])
            row = {
                col: Decimal(
                    df_row[int(self.VARS_MAP[col][1:])]
                ) for col in col_names
            }

        elif stop and not start:
            raise Exception("Stop year provided without start year")

        else:
            row = self.get_convolution()
            row = {
                k: v for k, v in row.items() if k in vars_names
            }

        return row

    def calculate_y(self):
        convolution = self.get_convolution()
        y = self.constant + self.c1 * (
            self.x1_c1 * convolution['X1'] + self.x4_c1 * convolution['X4'] +
            self.x5_c1 * convolution['X5'] + self.x7_c1 * convolution['X7'] +
            self.x11_c1 * convolution['X11'] +
            self.x14_c1 * convolution['X14'] +
            self.x15_c1 * convolution['X15'] + self.x16_c1 * convolution['X16']
        ) + self.c4 * (
            self.x1_c4 * convolution['X1'] + self.x4_c4 * convolution['X4'] +
            self.x5_c4 * convolution['X5'] + self.x7_c4 * convolution['X7'] +
            self.x11_c4 * convolution['X11'] +
            self.x14_c4 * convolution['X14'] +
            self.x15_c4 * convolution['X15'] + self.x16_c4 * convolution['X16']
        )
        return y

    def get_recommendation(self, cluster_num):
        if cluster_num == "1":
            recommendation = """
            Для улучшения иновационного развития предприятия,
            необходимо обратить внимание на количество поглощений,
            а именно рассмотреть возможность увеличения данного показателя.
            """
        elif cluster_num == "2":
            recommendation = """
            Для улучшения иновационного развития предприятия,
            необходимо обратить внимание на количество патентов, а именно
            рассмотреть возможность увеличения данного показателя.
            """
        else:
            recommendation = """
            У вашей компании очень высокий уровень инновационной
            привлекательности, для его поддержания и улучшения стоит обратить
            внимание на количество поглощений других компаний, а именно
            рассмотреть возможность увеличения данного показателя.
            """

        return recommendation

    def get_p_value(self, df=None):
        if df is None:
            df = self.get_dataframe()

        convolution = self.get_convolution(df)
        eta = self.logit_const + self.logit_const_x1 * convolution['X1'] + \
            self.logit_const_x11 * convolution['X11']

        p_value = Decimal(exp(eta)) / Decimal(1 + exp(eta))

        return p_value

    def get_cluster(self, method, **kwargs):
        from innovation.models import Order

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
                'X1': Decimal('605.563704'),
                'X4': Decimal('74.1007977'),
                'X5': Decimal('10.9912602'),
                'X7': Decimal('12.0261736'),
                'X11': Decimal('3.88481466'),
                'X14': Decimal('2.34036013'),
                'X15': Decimal('2.73474355'),
                'X16': Decimal('21.0625'),
            },
            '2': {
                'X1': Decimal('2036.70322'),
                'X4': Decimal('128.053402'),
                'X5': Decimal('12.6208238'),
                'X7': Decimal('22.9470241'),
                'X11': Decimal('4.65826331'),
                'X14': Decimal('11.9321632'),
                'X15': Decimal('7.83429687'),
                'X16': Decimal('28.5'),
            },
            '3': {
                'X1': Decimal('5350.08'),
                'X4': Decimal('228.594302'),
                'X5': Decimal('29.814385'),
                'X7': Decimal('34.5612084'),
                'X11': Decimal('11.0855555'),
                'X14': Decimal('8.79057304'),
                'X15': Decimal('11.6689716'),
                'X16': Decimal('94.5'),
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
