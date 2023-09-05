import math
import pickle
import random
from typing import Optional, List

import joblib
import numpy as np
from pandas import DataFrame
from sklearn import linear_model
from sklearn.metrics import mean_squared_error as mse

from bamt.log import logger_nodes
from .base import BaseNode
from .schema import GaussianParams


class GaussianNode(BaseNode):
    """
    Main class for Gaussian Node
    """

    def __init__(self, name, regressor: Optional[object] = None):
        super(GaussianNode, self).__init__(name)
        if regressor is None:
            regressor = linear_model.LinearRegression()
        self.regressor = regressor
        self.type = "Gaussian" + f" ({type(self.regressor).__name__})"

    def fit_parameters(self, data: DataFrame, **kwargs) -> GaussianParams:
        parents = self.cont_parents
        if type(self).__name__ == "CompositeContinuousNode":
            parents = parents + self.disc_parents
        if parents:
            self.regressor.fit(data[parents].values, data[self.name].values, **kwargs)
            predicted_value = self.regressor.predict(data[parents].values)
            variance = mse(data[self.name].values, predicted_value, squared=False)
            serialization = self.choose_serialization(self.regressor)

            if serialization == "pickle":
                ex_b = pickle.dumps(self.regressor, protocol=4)
                # model_ser = ex_b.decode('latin1').replace('\'', '\"')
                model_ser = ex_b.decode("latin1")
                return {
                    "mean": np.nan,
                    "regressor_obj": model_ser,
                    "regressor": type(self.regressor).__name__,
                    "variance": variance,
                    "serialization": "pickle",
                }
            else:
                logger_nodes.warning(
                    f"{self.name}::Pickle failed. BAMT will use Joblib. | "
                    + str(serialization.args[0])
                )

                path = self.get_path_joblib(
                    node_name=self.name.replace(" ", "_"),
                    specific=f"{self.name.replace(' ', '_')}",
                )
                joblib.dump(self.regressor, path, compress=True, protocol=4)
                return {
                    "mean": np.nan,
                    "regressor_obj": path,
                    "regressor": type(self.regressor).__name__,
                    "variance": variance,
                    "serialization": "joblib",
                }
        else:
            mean_base = np.mean(data[self.name].values)
            variance = np.var(data[self.name].values)
            return {
                "mean": mean_base,
                "regressor_obj": None,
                "regressor": None,
                "variance": variance,
                "serialization": None,
            }

    def get_dist(self, node_info, pvals):
        var = node_info["variance"]
        if pvals:
            for el in pvals:
                if str(el) == "nan":
                    return np.nan
            if node_info["serialization"] == "joblib":
                model = joblib.load(node_info["regressor_obj"])
            else:
                a = node_info["regressor_obj"].encode("latin1")
                model = pickle.loads(a)

            if type(self).__name__ == "CompositeContinuousNode":
                pvals = [int(item) if isinstance(item, str) else item for item in pvals]

            cond_mean = model.predict(np.array(pvals).reshape(1, -1))[0]
            return cond_mean, var
        else:
            return node_info["mean"], math.sqrt(var)

    def choose(self, node_info: GaussianParams, pvals: List[float]) -> float:
        """
        Return value from Logit node
        params:
        node_info: nodes info from distributions
        pvals: parent values
        """

        cond_mean, var = self.get_dist(node_info, pvals)
        return random.gauss(cond_mean, var)

    @staticmethod
    def predict(node_info: GaussianParams, pvals: List[float]) -> float:
        """
        Return prediction from Logit node
        params:
        node_info: nodes info from distributions
        pvals: parent values
        """

        if pvals:
            for el in pvals:
                if str(el) == "nan":
                    return np.nan
            if node_info["serialization"] == "joblib":
                model = joblib.load(node_info["regressor_obj"])
            else:
                a = node_info["regressor_obj"].encode("latin1")
                model = pickle.loads(a)

            pred = model.predict(np.array(pvals).reshape(1, -1))[0]
            return pred
        else:
            return node_info["mean"]
