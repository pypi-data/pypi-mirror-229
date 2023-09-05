from pdengine import ValveModel
from tests import general_tests_class as tc
from control import tf, pade

def test_valve_init():
    model = ValveModel()
    tester = tc.general_tester(model)
    tester.model_tests()

    assert model.name == "Simple Control Valve"

def test_init_generate_valve():
    model = ValveModel()
    tester = tc.general_tester(model)

    model_vals = [next(model._init_generator(dt=0.02, seed=True)) for i in range (0, 5)]
    assert tester.close_enough(model_vals, valve_values())
    tester.generator_tests()

# Brittle tests below
def test_create_system_valve():
    model = ValveModel()
    assert model._equals(comp_valve_model())

def test_get_percentspan():
    model = ValveModel()

    assert 0.5 == model.get_percentspan("CO", 0.5)

# Supporting functions below - used in tests but not tests themselves
# Initialize comparison model for ValveModel
def comp_valve_model():
    g_tf = tf([-10], [7,1])
    (num_pade, den_pade) = pade(5,1)
    g_delay = tf(num_pade, den_pade)
    g11 = g_tf*g_delay
    test_sys = tf(g11)
    return test_sys

# Returns seeded values of ValveModel
def valve_values():
    vals = [{'F': 4.99916, 'CO': 0.50000},
        {'F': 4.99916, 'CO': 0.50000},
        {'F': 4.99916, 'CO': 0.50000},
        {'F': 4.99916, 'CO': 0.50000},
        {'F': 4.99916, 'CO': 0.50000},]
    return vals