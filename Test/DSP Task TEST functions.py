#!/usr/bin/env python
# coding: utf-8
# %%

# %%

def ReadSignalFile(file_name):
    expected_indices = []
    expected_samples = []

    # All official Task 1 files are kept beside this test file.
    file_path = Path(__file__).resolve().parent / Path(file_name).name

    with open(file_path, "r", encoding="utf-8") as f:
        # Official Task files have three header lines.
        f.readline()
        f.readline()
        f.readline()

        line = f.readline()

        while line:
            L = line.strip()

            if len(L.split()) == 2:
                parts = L.split()

                V1 = int(parts[0])
                V2 = float(parts[1])

                expected_indices.append(V1)
                expected_samples.append(V2)

                line = f.readline()
            else:
                break

    return expected_indices, expected_samples




def AddSignalSamplesAreEqual(userFirstSignal, userSecondSignal, Your_indices, Your_samples):
    if (userFirstSignal == 'Signal1.txt' and userSecondSignal == 'Signal2.txt'):
        file_name = "add.txt"  # write here the path of the add output file
    expected_indices, expected_samples = ReadSignalFile(file_name)
    if (len(expected_samples) != len(Your_samples)) or (len(expected_indices) != len(Your_indices)):
        print("Addition Test case failed, your signal have different length from the expected one")
        return
    for i in range(len(Your_indices)):
        if (Your_indices[i] != expected_indices[i]):
            print("Addition Test case failed, your signal have different indicies from the expected one")
            return
    for i in range(len(expected_samples)):
        if abs(Your_samples[i] - expected_samples[i]) < 0.01:
            continue
        else:
            print("Addition Test case failed, your signal have different values from the expected one")
            return
    print("Addition Test case passed successfully")



def SubSignalSamplesAreEqual(userFirstSignal, userSecondSignal, Your_indices, Your_samples):
    if (userFirstSignal == 'Signal1.txt' and userSecondSignal == 'Signal2.txt'):
        file_name = "subtract.txt"  # write here the path of the subtract output file

    expected_indices, expected_samples = ReadSignalFile(file_name)

    if (len(expected_samples) != len(Your_samples)) or (len(expected_indices) != len(Your_indices)):
        print("Subtraction Test case failed, your signal have different length from the expected one")
        return
    for i in range(len(Your_indices)):
        if (Your_indices[i] != expected_indices[i]):
            print("Subtraction Test case failed, your signal have different indicies from the expected one")
            return
    for i in range(len(expected_samples)):
        if abs(Your_samples[i] - expected_samples[i]) < 0.01:
            continue
        else:
            print("Subtraction Test case failed, your signal have different values from the expected one")
            return
    print("Subtraction Test case passed successfully")



def MultiplySignalByConst(User_Const, Your_indices, Your_samples):
    if (User_Const == 5):
        file_name = "mul5.txt"  # write here the path of the mul5 output file

    expected_indices, expected_samples = ReadSignalFile(file_name)
    if (len(expected_samples) != len(Your_samples)) or (len(expected_indices) != len(Your_indices)):
        print("Multiply by " + str(
            User_Const) + " Test case failed, your signal have different length from the expected one")
        return
    for i in range(len(Your_indices)):
        if (Your_indices[i] != expected_indices[i]):
            print("Multiply by " + str(
                User_Const) + " Test case failed, your signal have different indicies from the expected one")
            return
    for i in range(len(expected_samples)):
        if abs(Your_samples[i] - expected_samples[i]) < 0.01:
            continue
        else:
            print("Multiply by " + str(
                User_Const) + " Test case failed, your signal have different values from the expected one")
            return
    print("Multiply by " + str(User_Const) + " Test case passed successfully")



def ShiftSignalByConst(Shift_value, Your_indices, Your_samples):
    if (Shift_value == 3):  # x(n+k)
        file_name = "advance3.txt"  # write here the path of delay3 output file
    elif (Shift_value == -3):  # x(n-k)
        file_name = "delay3.txt"  # write here the path of advance3 output file

    expected_indices, expected_samples = ReadSignalFile(file_name)
    if (len(expected_samples) != len(Your_samples)) or (len(expected_indices) != len(Your_indices)):
        print("Shift by " + str(
            Shift_value) + " Test case failed, your signal have different length from the expected one")
        return
    for i in range(len(Your_indices)):
        if (Your_indices[i] != expected_indices[i]):
            print("Shift by " + str(
                Shift_value) + " Test case failed, your signal have different indicies from the expected one")
            return
    for i in range(len(expected_samples)):
        if abs(Your_samples[i] - expected_samples[i]) < 0.01:
            continue
        else:
            print("Shift by " + str(
                Shift_value) + " Test case failed, your signal have different values from the expected one")
            return
    print("Shift by " + str(Shift_value) + " Test case passed successfully")




def Folding(Your_indices, Your_samples):
    file_name = "folding.txt"  # write here the path of the folding output file
    expected_indices, expected_samples = ReadSignalFile(file_name)
    if (len(expected_samples) != len(Your_samples)) or (len(expected_indices) != len(Your_indices)):
        print("Folding Test case failed, your signal have different length from the expected one")
        return
    for i in range(len(Your_indices)):
        if (Your_indices[i] != expected_indices[i]):
            print("Folding Test case failed, your signal have different indicies from the expected one")
            return
    for i in range(len(expected_samples)):
        if abs(Your_samples[i] - expected_samples[i]) < 0.01:
            continue
        else:
            print("Folding Test case failed, your signal have different values from the expected one")
            return
    print("Folding Test case passed successfully")



from pathlib import Path
from datetime import datetime
import sys

TEST_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = TEST_DIR.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dsp.discrete_signal import DiscreteSignal
from dsp.operations import add, subtract, multiply, delay, advance, fold


def _load_task_signal(file_name):
    """Read a Task-provided signal file from the Test folder."""
    path = TEST_DIR / file_name
    indices, samples = ReadSignalFile(str(path))
    return DiscreteSignal(indices, samples, name=Path(file_name).stem)


def _write_operation_result(file, title, result):
    """Write one operation result as index/value pairs."""
    file.write(f"--- {title} ---\n")
    file.write(f"N = {len(result.indices)}\n")

    for index, value in zip(result.indices, result.values):
        file.write(f"{int(index)} {float(value):g}\n")

    file.write("\n")


def run_all_tests():
    signal1 = _load_task_signal("Signal1.txt")
    signal2 = _load_task_signal("Signal2.txt")

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_file = TEST_DIR / f"operation_outputs_{timestamp}.txt"

    print("\n DSP TASK 1 TESTS\n")

    with open(output_file, "w", encoding="utf-8") as out:
        out.write("OPERATIONS OUTPUTS \n\n")

        result = add([signal1, signal2])
        _write_operation_result(out, "Addition: Signal1 + Signal2", result)
        AddSignalSamplesAreEqual(
            "Signal1.txt",
            "Signal2.txt",
            result.indices,
            result.values,
        )

        result = subtract(signal1, signal2)
        _write_operation_result(out, "Subtraction: Signal1 - Signal2", result)
        SubSignalSamplesAreEqual(
            "Signal1.txt",
            "Signal2.txt",
            result.indices,
            result.values,
        )

        result = multiply(signal1, 5)
        _write_operation_result(out, "Multiplication: 5 * Signal1", result)
        MultiplySignalByConst(
            5,
            result.indices,
            result.values,
        )

        # 4) Advance by 3
        result = advance(signal1, 3)
        _write_operation_result(out, "Advance by 3", result)
        ShiftSignalByConst(
            3,
            result.indices,
            result.values,
        )

        # 5) Delay by 3
        result = delay(signal1, 3)
        _write_operation_result(out, "Delay by 3", result)
        ShiftSignalByConst(
            -3,
            result.indices,
            result.values,
        )

        # 6) Folding
        result = fold(signal1)
        _write_operation_result(out, "Folding: x(-n)", result)
        Folding(
            result.indices,
            result.values,
        )

    print(f"Operation results were saved to: {output_file}")



if __name__ == "__main__":
    run_all_tests()
