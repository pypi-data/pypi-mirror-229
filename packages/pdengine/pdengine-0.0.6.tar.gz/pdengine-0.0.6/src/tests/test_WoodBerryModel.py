from pdengine import WoodBerryModel
from tests import general_tests_class as tc
from control import tf, pade

def test_woodberry_init():
    model = WoodBerryModel()
    tester = tc.general_tester(model)
    tester.model_tests()

    assert model.name == "Wood-Berry Distillation"

def test_init_generate_wd():
    model = WoodBerryModel()
    tester = tc.general_tester(model)
    tester.model_tests()

    model_vals = [next(model._init_generator(dt=0.02, seed=True)) for i in range (0, 5)]
    assert tester.close_enough(model_vals, wb_values())
    tester.generator_tests()

# Brittle tests below
def test_create_system_wb():
    model = WoodBerryModel()
    assert model._equals(comp_wb_model())

# Supporting functions below - used in tests but not tests themselves
# Initialize comparison model for WoodBerryModel
def comp_wb_model():
    g_tf = tf([12.8], [16.7,1])
    (num_pade, den_pade) = pade(1,1)
    g_delay = tf(num_pade, den_pade)
    g11 = g_tf*g_delay

    g_tf = tf([-18.9], [21.0,1])
    (num_pade, den_pade) = pade(3,1)
    g_delay = tf(num_pade, den_pade)
    g12 = g_tf*g_delay

    g_tf = tf([6.6], [10.9,1])
    (num_pade, den_pade) = pade(7,1)
    g_delay = tf(num_pade, den_pade)
    g21 = g_tf*g_delay

    g_tf = tf([-19.4], [14.4,1])
    (num_pade, den_pade) = pade(3,1)
    g_delay = tf(num_pade, den_pade)
    g22 = g_tf*g_delay

    g_tf = tf([3.8], [14.9,1])
    (num_pade, den_pade) = pade(8,1)
    g_delay = tf(num_pade, den_pade)
    g1f = g_tf*g_delay

    g_tf = tf([4.9], [13.2,1])
    (num_pade, den_pade) = pade(3,1)
    g_delay = tf(num_pade, den_pade)
    g2f = g_tf*g_delay

    row_1_num = [x[0][0] for x in (g11.num, g12.num, g1f.num)]
    row_2_num = [x[0][0] for x in (g21.num, g22.num, g2f.num)]

    row_1_den = [x[0][0] for x in (g11.den, g12.den, g1f.den)]
    row_2_den = [x[0][0] for x in (g21.den, g22.den, g2f.den)]

    sys = tf(
                [row_1_num,row_2_num],
                [row_1_den,row_2_den])

    return sys

# Returns seeded values of WoodBerryModel
def wb_values():
    vals = [{'x_D': 96.24791, 'x_B': 0.50197, 'R': 1.95009, 'S': 1.70991, 'F': 2.45},
        {'x_D': 96.24791, 'x_B': 0.50197, 'R': 1.95009, 'S': 1.70991, 'F': 2.45},
        {'x_D': 96.24791, 'x_B': 0.50197, 'R': 1.95009, 'S': 1.70991, 'F': 2.45},
        {'x_D': 96.24791, 'x_B': 0.50197, 'R': 1.95009, 'S': 1.70991, 'F': 2.45},
        {'x_D': 96.24791, 'x_B': 0.50197, 'R': 1.95009, 'S': 1.70991, 'F': 2.45}]
    return vals