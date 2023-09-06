from pandas import DataFrame
from pydantic import BaseModel


class DS_Evaluator():

    def __init__(self):
        pass

    def evaluate_model_predictions(self, df_from_model: DataFrame) -> DataFrame:
        """
        Apply evaluation function (_get_confusion_matrix) on every incoming Dataframe row.
        Parameters:
            df_from_model: A dataframe containing both labeled data and model predictions
        Returns:
            Altered dataframe with a new column 'confusion_matrix' that holds a list of 'ConfusionRow' objects
        """
        df_from_model['confusion_matrix'] = df_from_model.apply(lambda row:
                                                                self.get_confusion_matrix(row.pred, row.pred_model),
                                                                axis=1)

        return df_from_model

    def get_confusion_matrix(self, true_label, prediction):
        """
        Model evaluation function, to be implemented per project in evaluator.py file
        """
        raise NotImplementedError

    @staticmethod
    def get_confusion_matrix_binary(true_label, prediction):
        confusion_matrix = {'tp': 0, 'fp': 0, 'fn': 0, 'tn': 0}
        if true_label == 1 and prediction == 1:
            confusion_matrix['tp'] = 1
        elif true_label == 1 and prediction == 0:
            confusion_matrix['fn'] = 1
        elif true_label == 0 and prediction == 0:
            confusion_matrix['tn'] = 1
        else:  # true_label == 0 and prediction == 1
            confusion_matrix['fp'] = 1
        return {'cm': confusion_matrix}


class ConfusionMatrix(BaseModel):

    def __init__(self):
        self.tp: int = 0  # True Positive
        self.tn: int = 0  # True Negative
        self.fp: int = 0  # False Positive
        self.fn: int = 0  # False Negative

        self.precision: float = 0
        self.f1: float = 0
        self.recall: float = 0

    def __add__(self, other):
        _sum = ConfusionMatrix(
            tp=self.tp + other.tp,
            fp=self.fp + other.fp,
            fn=self.fn + other.fn,
            tn=self.tn + other.tn,
        )
        _sum.calc()
        return _sum

    def precision_calc(self):
        sum_ = self.tp + self.fp
        if sum_:
            return self.tp / sum_
        else:
            return 0

    def recall_calc(self):
        sum_ = self.tp + self.fn
        if sum_:
            return self.tp / sum_
        else:
            return 0

    def f1_calc(self):
        precision_ = self.precision
        recall_ = self.recall
        if precision_ + recall_ > 0:
            return 2 * (precision_ * recall_) / (precision_ + recall_)
        return 0

    def calc(self):
        self.precision= round(self.precision_calc(),3)
        self.recall = round(self.recall_calc(), 3)
        self.f1 = round(self.f1_calc(), 3)


class ConfusionRow(ConfusionMatrix):
    """
    This class holds information regarding evaluation result of a single attribute that was sent for evaluation.
    It inherits from the ConfusionMatrix class to enable confusion matrix abilities, and will eventually output
    all relevant values for a single attribute. The evaluator output should be a list of objects from this class type
    """

    def __init__(self, name: str = "generic_cm"):
        super().__init__()
        self.name = name
        self.pred_val: list = []
        self.target_val: list = []

    def set_val_str(self, target: [str, None], pred: [str, None]):
        # pred='' and target=''
        if pred in [None, ''] and target in [None, '']:
            self.tn += 1
        # pred='' and target='sdfsdf'
        elif pred in [None, ''] and target not in [None, '']:
            self.fn += 1
        # ('a'!='b') or (pred='sdfsdf' & target ='')
        elif pred != target:
            self.fp += 1
        elif pred == target:
            self.tp += 1

        else:
            raise ValueError

        self.pred_val.append(pred)
        self.target_val.append(target)
        self.calc()

    def set_val_int(self, target: int, pred: int, zero_is_empty=False):
        if pred == target:
            if (pred != 0) or (zero_is_empty is False):
                self.tp += 1
        elif pred > target:
            self.fp += 1
        elif target > pred:
            self.fn += 1

        if (zero_is_empty is False) or (pred != 0 or target != 0):
            self.pred_val.append(pred)
            self.target_val.append(target)
        self.calc()

    def set_val_list_count(self, target: [int, None], pred: [int, None]):
        if pred is None and target is not None:
            self.fn += 1
        elif pred is not None and target is None:
            self.fp += 1
        elif pred == target:
            self.tp += target
        elif pred > target:
            self.fp += 1
        elif target > pred:
            self.fn += 1

        self.pred_val.append(pred)
        self.target_val.append(target)
        self.calc()

    # compare two list and count how many values UNIQUE from each appears at the other
    def set_val_check_list_of_list(self, col: list, exp: list, pre_comp_func_l=[]):
        # examples:
        # miss col - Exp: [A, B, C] Col: [B,C] tp:2 fn:1
        # miss exp - Exp: [A] Col: [A, B, C] tp:1 fp: 2
        #
        # The Q unique or not unique:
        # unique     - Exp: [A,A,A] col [A,B,B] tp:1 fp:1
        # unique     - Exp: [A,A,A,A] col [A,B,B] tp:1 fp:1
        # or
        # not unique - Exp: [A,A,A] col [A, B] tp:1 fp: 1 fn: 1
        # not unique - Exp: [A,A,A,A] col [A,B] tp:1 fp:1 fn :2
        # tmp_pred = copy.deepcopy(pred)
        # tmp_target = copy.deepcopy(target)
        #
        # for func in pre_comp_func_l:
        #     tmp_pred = func(record_l=tmp_pred)
        #     tmp_target = func(record_l=tmp_target)

        tmp_col = col
        tmp_exp = exp

        exp_idx = 0
        for exp_idx, exp in enumerate(tmp_exp):
            if exp_idx < len(tmp_col):
                if exp == tmp_col[exp_idx]:
                    self.tp += 1
                else:
                    # found values on pred and target that mismatch
                    self.fp += 1
            else:
                # no value at predict
                self.fn += 1

        if exp_idx + 1 < len(tmp_col):
            # adiel: tn used to mark error in this case YAK!
            self.fp += len(tmp_col) - (exp_idx + 1)
        self.calc()

    def set_exp_col_cm(self, match_num, exp_miss, col_miss):
        # row.set_exp_col_cm(match_num=len(order_l['match_exp']), exp_miss=len(order_l['exp_no']), col_miss=len(order_l['col_no']))
        self.tp = match_num
        self.fn = exp_miss
        self.fp = col_miss
        self.calc()

    def get_cols_per_attr(attr):
        return [f'{attr}_pred', f'{attr}_target', f'{attr}_prob', f'{attr}_tp', f'{attr}_fp', f'{attr}_tn',
                f'{attr}_fn']

    def get_server_tester(self):
        self.calc()
        result = {
            self.name + '_fn': self.fn,
            self.name + '_fp': self.fp,
            self.name + '_tn': self.tn,
            self.name + '_tp': self.tp,
            self.name + '_pred': str(self.pred_val),
            self.name + '_prob': -1,
            self.name + '_target': str(self.target_val),
        }
        return result
