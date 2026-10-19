from pathlib import Path
import importlib.util
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from dsp.discrete_signal import DiscreteSignal
from dsp.quantization import quantize

TESTS_DIR = ROOT / "tests"
CASES_DIR = TESTS_DIR / "testcases" / "Task 3"
def load_test_function(filename, function_name):
    path = CASES_DIR / filename
    spec = importlib.util.spec_from_file_location(function_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load test helper: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, function_name)


def read_signal(path):
    # The first three lines are test metadata; the remaining lines are: index value.
    lines = path.read_text(encoding="utf-8").splitlines()[3:]
    indices = []
    values = []
    for line in lines:
        parts = line.split()
        if len(parts) >= 2:
            indices.append(int(parts[0]))
            values.append(float(parts[1]))
    if not values:
        raise ValueError(f"No samples found in {path}")
    return DiscreteSignal(indices, values, name=path.stem)



def main():
    test1 = load_test_function("QuanTest1.py", "QuantizationTest1")
    test2 = load_test_function("QuanTest2.py", "QuantizationTest2")

    ##print("=" * 60)
    ##print("RUNNING INSTRUCTOR QUANTIZATION TEST CASES")
    ##print("=" * 60)

    # Test 1: 3 bits = 8 levels
    signal1 = read_signal(CASES_DIR / "Quan1_input.txt")
    result1 = quantize(signal1, bits=3)

    print("\nTEST 1 - 3 bits / 8 levels")
    print("-" * 60)
    print("Actual output from our code:")
    print("Interval indices:", result1.interval_indices)
    print("Encoded:", result1.encoded)
    print("Quantized values:", result1.quantized.values.tolist())
    ##print("\nExpected output file: Quan1_Out.txt")

    test1(
        str(CASES_DIR / "Quan1_Out.txt"),
        result1.encoded,
        result1.quantized.values.tolist(),
    )

    print("TEST 1: PASSED")

    # Test 2: 4 levels = 2 bits
    signal2 = read_signal(CASES_DIR / "Quan2_input.txt")
    result2 = quantize(signal2, levels=4)

    print("\nTEST 2 - 4 levels / 2 bits")
    print("-" * 60)
    print("Actual output from our code:")
    print("Interval indices:", result2.interval_indices)
    print("Encoded:", result2.encoded)
    print("Quantized values:", result2.quantized.values.tolist())
    print("Quantization error:", result2.error.values.tolist())
    #print("\nExpected output file: Quan2_Out.txt")

    test2(
        str(CASES_DIR / "Quan2_Out.txt"),
        result2.interval_indices,
        result2.encoded,
        result2.quantized.values.tolist(),
        result2.error.values.tolist(),
    )

    print("TEST 2: PASSED")
    #print("\nAll instructor test cases passed successfully!")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"\nCould not run instructor test cases: {exc}")
        print("Check that this file is in the project root and that the file names/folders match.")
        sys.exit(1)
