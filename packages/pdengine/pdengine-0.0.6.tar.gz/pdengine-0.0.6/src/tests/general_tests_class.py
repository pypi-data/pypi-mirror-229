import numpy as np
from control.xferfcn import TransferFunction


class general_tester():
    def __init__(self, model):
        self.model = model

    # Generalized type/structure tests for a model's fields
    def model_tests(self):
        model = self.model
        assert type(model.name) == str
        assert type(model.system) == TransferFunction

        assert type(model.inputs) == dict and set(model.inputs.keys()) == set(['MV', 'FF'])
        assert model.ninputs == len(model.inputs['MV']) + len(model.inputs['FF'])
        assert model.ninputs == model.nMVs + model.nFFs

        assert type(model.outputs) == list
        assert model.noutputs == len(model.outputs)
        
        assert type(model.SS_vals) == dict and len(model.SS_vals.keys()) == model.ninputs + model.noutputs
        assert type(model.typ_movs) == dict and len(model.typ_movs.keys()) == model.ninputs

        assert type(model.validity_lims) == dict
        assert type(model.noise_lvls) == dict
        for var in model.outputs + model.inputs['MV'] + model.inputs['FF']: 
            assert var in model.validity_lims.keys()
            assert var in model.noise_lvls.keys()
        
        for var in model.inputs['MV']:
            assert var in model.initial_COs.keys()

    # Generalized generator tests
    def generator_tests(self):
        model = self.model
        test_output = next(model._init_generator(dt=0.02, seed=True))
        
        assert type(test_output) == dict
        assert set(test_output.keys()) == set(model.outputs + model.inputs['MV'] + model.inputs['FF'])
    
        for var in test_output.keys():
            assert type(test_output[var]) == np.float64

    # Comparison of two lists of value dictionaries for purpose of testing (analogous to numpy.allclose())
    def close_enough(self, output_values: list, comparison_values: list):
        if len(output_values) != len(comparison_values): return False

        for i in range(0, len(output_values)):
            for var in output_values[i].keys():
                if not np.allclose(output_values[i][var], comparison_values[i][var], atol=1e-4): return False

        return True