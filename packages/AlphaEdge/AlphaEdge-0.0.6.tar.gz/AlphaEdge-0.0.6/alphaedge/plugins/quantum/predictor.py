import os, json, pdb, itertools
import pandas as pd
from ultron.strategy.deformer import FusionLoad
from ultron.kdutils.file import load_pickle
from jdw.mfc.entropy.deformer.fusionx import Futures
from alphaedge.plugins.quantum.base import Base


class Predictor(Base):

    def __init__(self, directory, policy_id, is_groups=1):
        super(Predictor, self).__init__(directory=directory,
                                        policy_id=policy_id,
                                        is_groups=is_groups)

    def predict(self, model_desc, total_data, returns_data):
        alpha_res = []
        desc_dir = os.path.join(self.category_directory, "desc")
        model_dir = os.path.join(self.category_directory, "model")
        model_desc = model_desc if isinstance(model_desc,
                                              list) else [model_desc]
        model_list = []
        for m in model_desc:
            filename = os.path.join(desc_dir, "{0}.h5".format(m))
            desc = load_pickle(filename)
            model = FusionLoad(desc)
            model_list.append(model)

        columns = [model.formulas.dependency for model in model_list]
        columns = list(set(itertools.chain.from_iterable(columns)))
        total_data = self.normal(total_data=total_data, columns=columns)

        for model in model_list:
            eng = Futures(batch=model.batch,
                          freq=model.freq,
                          horizon=model.horizon,
                          id=model.id,
                          is_full=True,
                          directory=model_dir)
            factors = eng.create_data(total_data=total_data,
                                      returns=returns_data)
            alpha_res.append(factors)
        return pd.concat(alpha_res, axis=1)

    def groups_predict(self, policy_desc, total_data):
        res = []
        for k, model_desc in policy_desc.items():
            prepar_data = self.create_predict_data(horizon=int(k),
                                                   offset=0,
                                                   total_data=total_data)
            returns_data = prepar_data[['trade_date', 'code', 'nxt1_ret']]
            predict_data = self.predict(model_desc=model_desc,
                                        total_data=prepar_data,
                                        returns_data=returns_data)
            res.append(predict_data)
        return pd.concat(res, axis=1)

    def main_predict(self, model_desc, total_data):
        desc_dir = os.path.join(self.category_directory, "desc")
        filename = os.path.join(desc_dir, "{0}.h5".format(model_desc))
        desc = load_pickle(filename)
        horizon = desc['horizon']
        prepar_data = self.create_predict_data(horizon=int(horizon),
                                               offset=0,
                                               total_data=total_data)
        returns_data = prepar_data[['trade_date', 'code', 'nxt1_ret']]
        predict_data = self.predict(model_desc=model_desc,
                                    total_data=prepar_data,
                                    returns_data=returns_data)
        return predict_data

    def calculate(self, total_data):
        policy_file = os.path.join(self.directory, "policy.json")
        with open(policy_file, 'r') as json_file:
            policy_data = json.load(json_file)

        if self.is_groups:
            return self.groups_predict(policy_desc=policy_data['groups'],
                                       total_data=total_data)
        else:
            return self.main_predict(model_desc=policy_data['main'],
                                     total_data=total_data)
        '''
        model_desc = policy_data['groups'][str(
            horizon)] if self.is_groups else policy_data['main']
        return self.predict(model_desc=model_desc,
                            total_data=total_data,
                            returns_data=returns_data)
        '''
