import java.util.Arrays;
import java.util.Vector;

class P55ABDiscreteCoils extends PMCVariable {

    public P55ABDiscreteCoils() {
        super("AB", "55 AB discrete coils", new Vector(), "", new int[]{1}, true, false, null);
    }

    PMCDiscreteCoil M1101 = new PMCDiscreteCoil("M1101", "55.AB.00-MLF-1101", false, 3.61975,-3.6423,5);
    PMCDiscreteCoil M1102 = new PMCDiscreteCoil("M1102", "55.AB.00-MLF-1102", false, 3.76235,-4.17737,25);
    PMCDiscreteCoil M1103 = new PMCDiscreteCoil("M1103", "55.AB.00-MLF-1103", false, 4.27171,-4.78053,55);
    PMCDiscreteCoil M1104 = new PMCDiscreteCoil("M1104", "55.AB.00-MLF-1104", false, 5.03252,-5.05293,86);
    PMCDiscreteCoil M1105 = new PMCDiscreteCoil("M1105", "55.AB.00-MLF-1105", false, 5.83621,-4.95454,107);
    PMCDiscreteCoil M1106 = new PMCDiscreteCoil("M1106", "55.AB.00-MLF-1106", false, 6.61183,-4.56123,127);
    PMCDiscreteCoil M1107 = new PMCDiscreteCoil("M1107", "55.AB.00-MLF-1107", false, 7.14317,4.07973,-129);
    PMCDiscreteCoil M1108 = new PMCDiscreteCoil("M1108", "55.AB.00-MLF-1108", false, 6.25987,4.70847,-125);
    PMCDiscreteCoil M1109 = new PMCDiscreteCoil("M1109", "55.AB.00-MLF-1109", false, 5.45643,5.10182,-101);
    PMCDiscreteCoil M1110 = new PMCDiscreteCoil("M1110", "55.AB.00-MLF-1110", false, 4.4007,4.92666,-60);
    PMCDiscreteCoil M1111 = new PMCDiscreteCoil("M1111", "55.AB.00-MLF-1111", false, 3.69873,4.08005,-19);
    PMCDiscreteCoil M1112 = new PMCDiscreteCoil("M1112", "55.AB.00-MLF-1112", false, 3.60691,2.64769,0);
    PMCDiscreteCoil M2101 = new PMCDiscreteCoil("M2101", "55.AB.00-MLF-2101", false, 3.61975,-3.6423,5);
    PMCDiscreteCoil M2102 = new PMCDiscreteCoil("M2102", "55.AB.00-MLF-2102", false, 3.76235,-4.17737,25);
    PMCDiscreteCoil M2103 = new PMCDiscreteCoil("M2103", "55.AB.00-MLF-2103", false, 4.27171,-4.78053,55);
    PMCDiscreteCoil M2104 = new PMCDiscreteCoil("M2104", "55.AB.00-MLF-2104", false, 5.03252,-5.05293,86);
    PMCDiscreteCoil M2105 = new PMCDiscreteCoil("M2105", "55.AB.00-MLF-2105", false, 5.83621,-4.95454,107);
    PMCDiscreteCoil M2106 = new PMCDiscreteCoil("M2106", "55.AB.00-MLF-2106", false, 6.61182,-4.56123,127);
    PMCDiscreteCoil M2107 = new PMCDiscreteCoil("M2107", "55.AB.00-MLF-2107", false, 7.14316,4.07973,-129);
    PMCDiscreteCoil M2108 = new PMCDiscreteCoil("M2108", "55.AB.00-MLF-2108", false, 6.25988,4.70847,-125);
    PMCDiscreteCoil M2109 = new PMCDiscreteCoil("M2109", "55.AB.00-MLF-2109", false, 5.45642,5.10182,-101);
    PMCDiscreteCoil M2110 = new PMCDiscreteCoil("M2110", "55.AB.00-MLF-2110", false, 4.40069,4.92666,-60);
    PMCDiscreteCoil M2111 = new PMCDiscreteCoil("M2111", "55.AB.00-MLF-2111", false, 3.69873,4.08005,-19);
    PMCDiscreteCoil M2112 = new PMCDiscreteCoil("M2112", "55.AB.00-MLF-2112", false, 3.60691,2.64769,0);
    PMCDiscreteCoil M4101 = new PMCDiscreteCoil("M4101", "55.AB.00-MLF-4101", false, 3.61975,-3.6423,5);
    PMCDiscreteCoil M4102 = new PMCDiscreteCoil("M4102", "55.AB.00-MLF-4102", false, 3.76235,-4.17737,25);
    PMCDiscreteCoil M4103 = new PMCDiscreteCoil("M4103", "55.AB.00-MLF-4103", false, 4.2717,-4.78053,55);
    PMCDiscreteCoil M4104 = new PMCDiscreteCoil("M4104", "55.AB.00-MLF-4104", false, 5.03252,-5.05293,86);
    PMCDiscreteCoil M4105 = new PMCDiscreteCoil("M4105", "55.AB.00-MLF-4105", false, 5.83621,-4.95454,107);
    PMCDiscreteCoil M4106 = new PMCDiscreteCoil("M4106", "55.AB.00-MLF-4106", false, 6.61182,-4.56123,127);
    PMCDiscreteCoil M4107 = new PMCDiscreteCoil("M4107", "55.AB.00-MLF-4107", false, 7.14316,4.07973,-129);
    PMCDiscreteCoil M4108 = new PMCDiscreteCoil("M4108", "55.AB.00-MLF-4108", false, 6.25987,4.70847,-125);
    PMCDiscreteCoil M4109 = new PMCDiscreteCoil("M4109", "55.AB.00-MLF-4109", false, 5.45643,5.10182,-101);
    PMCDiscreteCoil M4110 = new PMCDiscreteCoil("M4110", "55.AB.00-MLF-4110", false, 4.4007,4.92666,-60);
    PMCDiscreteCoil M4111 = new PMCDiscreteCoil("M4111", "55.AB.00-MLF-4111", false, 3.69873,4.08005,-19);
    PMCDiscreteCoil M4112 = new PMCDiscreteCoil("M4112", "55.AB.00-MLF-4112", false, 3.60691,2.64769,0);
    PMCDiscreteCoil M5101 = new PMCDiscreteCoil("M5101", "55.AB.00-MLF-5101", false, 3.61975,-3.6423,5);
    PMCDiscreteCoil M5102 = new PMCDiscreteCoil("M5102", "55.AB.00-MLF-5102", false, 3.76235,-4.17737,25);
    PMCDiscreteCoil M5103 = new PMCDiscreteCoil("M5103", "55.AB.00-MLF-5103", false, 4.27171,-4.78053,55);
    PMCDiscreteCoil M5104 = new PMCDiscreteCoil("M5104", "55.AB.00-MLF-5104", false, 5.03253,-5.05293,86);
    PMCDiscreteCoil M5105 = new PMCDiscreteCoil("M5105", "55.AB.00-MLF-5105", false, 5.83621,-4.95454,107);
    PMCDiscreteCoil M5106 = new PMCDiscreteCoil("M5106", "55.AB.00-MLF-5106", false, 6.61182,-4.56123,127);
    PMCDiscreteCoil M5107 = new PMCDiscreteCoil("M5107", "55.AB.00-MLF-5107", false, 7.14316,4.07973,-129);
    PMCDiscreteCoil M5108 = new PMCDiscreteCoil("M5108", "55.AB.00-MLF-5108", false, 6.25987,4.70847,-125);
    PMCDiscreteCoil M5109 = new PMCDiscreteCoil("M5109", "55.AB.00-MLF-5109", false, 5.45643,5.10182,-101);
    PMCDiscreteCoil M5110 = new PMCDiscreteCoil("M5110", "55.AB.00-MLF-5110", false, 4.40069,4.92666,-60);
    PMCDiscreteCoil M5111 = new PMCDiscreteCoil("M5111", "55.AB.00-MLF-5111", false, 3.69873,4.08005,-19);
    PMCDiscreteCoil M5112 = new PMCDiscreteCoil("M5112", "55.AB.00-MLF-5112", false, 3.60691,2.64769,0);
    PMCDiscreteCoil M7101 = new PMCDiscreteCoil("M7101", "55.AB.00-MLF-7101", false, 3.61975,-3.6423,5);
    PMCDiscreteCoil M7102 = new PMCDiscreteCoil("M7102", "55.AB.00-MLF-7102", false, 3.76235,-4.17737,25);
    PMCDiscreteCoil M7103 = new PMCDiscreteCoil("M7103", "55.AB.00-MLF-7103", false, 4.2717,-4.78053,55);
    PMCDiscreteCoil M7104 = new PMCDiscreteCoil("M7104", "55.AB.00-MLF-7104", false, 5.03252,-5.05293,86);
    PMCDiscreteCoil M7105 = new PMCDiscreteCoil("M7105", "55.AB.00-MLF-7105", false, 5.83621,-4.95454,107);
    PMCDiscreteCoil M7106 = new PMCDiscreteCoil("M7106", "55.AB.00-MLF-7106", false, 6.61182,-4.56123,127);
    PMCDiscreteCoil M7107 = new PMCDiscreteCoil("M7107", "55.AB.00-MLF-7107", false, 7.14317,4.07973,-129);
    PMCDiscreteCoil M7108 = new PMCDiscreteCoil("M7108", "55.AB.00-MLF-7108", false, 6.25987,4.70847,-125);
    PMCDiscreteCoil M7109 = new PMCDiscreteCoil("M7109", "55.AB.00-MLF-7109", false, 5.45643,5.10182,-101);
    PMCDiscreteCoil M7110 = new PMCDiscreteCoil("M7110", "55.AB.00-MLF-7110", false, 4.4007,4.92666,-60);
    PMCDiscreteCoil M7111 = new PMCDiscreteCoil("M7111", "55.AB.00-MLF-7111", false, 3.69873,4.08005,-19);
    PMCDiscreteCoil M7112 = new PMCDiscreteCoil("M7112", "55.AB.00-MLF-7112", false, 3.6069,2.64769,0);
    PMCDiscreteCoil M8101 = new PMCDiscreteCoil("M8101", "55.AB.00-MLF-8101", false, 3.61975,-3.6423,5);
    PMCDiscreteCoil M8102 = new PMCDiscreteCoil("M8102", "55.AB.00-MLF-8102", false, 3.76235,-4.17737,25);
    PMCDiscreteCoil M8103 = new PMCDiscreteCoil("M8103", "55.AB.00-MLF-8103", false, 4.2717,-4.78053,55);
    PMCDiscreteCoil M8104 = new PMCDiscreteCoil("M8104", "55.AB.00-MLF-8104", false, 5.03252,-5.05293,86);
    PMCDiscreteCoil M8105 = new PMCDiscreteCoil("M8105", "55.AB.00-MLF-8105", false, 5.83621,-4.95454,107);
    PMCDiscreteCoil M8106 = new PMCDiscreteCoil("M8106", "55.AB.00-MLF-8106", false, 6.61182,-4.56123,127);
    PMCDiscreteCoil M8107 = new PMCDiscreteCoil("M8107", "55.AB.00-MLF-8107", false, 7.14317,4.07973,-129);
    PMCDiscreteCoil M8108 = new PMCDiscreteCoil("M8108", "55.AB.00-MLF-8108", false, 6.25987,4.70847,-125);
    PMCDiscreteCoil M8109 = new PMCDiscreteCoil("M8109", "55.AB.00-MLF-8109", false, 5.45643,5.10182,-101);
    PMCDiscreteCoil M8110 = new PMCDiscreteCoil("M8110", "55.AB.00-MLF-8110", false, 4.4007,4.92666,-60);
    PMCDiscreteCoil M8111 = new PMCDiscreteCoil("M8111", "55.AB.00-MLF-8111", false, 3.69873,4.08005,-19);
    PMCDiscreteCoil M8112 = new PMCDiscreteCoil("M8112", "55.AB.00-MLF-8112", false, 3.60691,2.64769,0);
}
