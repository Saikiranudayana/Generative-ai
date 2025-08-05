"""
Array Operations: Combine two arrays and remove zeros from the first array
"""

# Example arrays
array1 = [1, 0, 3, 0, 5, 0, 7, 0, 9, 0]  # Array with zeros
array2 = [2, 4, 6, 8, 10]  # Array with numbers

print("Original Arrays:")
print(f"Array 1 (with zeros): {array1}")
print(f"Array 2 (numbers): {array2}")

# Method 1: Remove zeros from array1, then combine
print("\n" + "="*50)
print("METHOD 1: Remove zeros first, then combine")
print("="*50)

# Remove zeros from array1
array1_no_zeros = [x for x in array1 if x != 0]
print(f"Array 1 without zeros: {array1_no_zeros}")

# Combine arrays
combined_method1 = array1_no_zeros + array2
print(f"Combined result: {combined_method1}")

# Method 2: Using filter() to remove zeros
print("\n" + "="*50)
print("METHOD 2: Using filter() function")
print("="*50)

array1_filtered = list(filter(lambda x: x != 0, array1))
combined_method2 = array1_filtered + array2
print(f"Array 1 filtered: {array1_filtered}")
print(f"Combined result: {combined_method2}")

# Method 3: Using numpy arrays (if you prefer numpy)
print("\n" + "="*50)
print("METHOD 3: Using NumPy arrays")
print("="*50)

try:
    import numpy as np
    
    # Convert to numpy arrays
    np_array1 = np.array(array1)
    np_array2 = np.array(array2)
    
    # Remove zeros from array1
    np_array1_no_zeros = np_array1[np_array1 != 0]
    print(f"Array 1 without zeros (numpy): {np_array1_no_zeros}")
    
    # Combine arrays
    combined_numpy = np.concatenate([np_array1_no_zeros, np_array2])
    print(f"Combined result (numpy): {combined_numpy}")
    
except ImportError:
    print("NumPy not installed. Skipping numpy method.")

# Method 4: One-liner approach
print("\n" + "="*50)
print("METHOD 4: One-liner approach")
print("="*50)

combined_oneliner = [x for x in array1 if x != 0] + array2
print(f"Combined result (one-liner): {combined_oneliner}")

# Method 5: If you want to sort the final result
print("\n" + "="*50)
print("METHOD 5: Combined and sorted")
print("="*50)

combined_sorted = sorted([x for x in array1 if x != 0] + array2)
print(f"Combined and sorted result: {combined_sorted}")

# Function to make it reusable
def combine_arrays_remove_zeros(arr1, arr2):
    """
    Combine two arrays and remove all zeros from the first array
    
    Args:
        arr1: First array (zeros will be removed from this)
        arr2: Second array (will be added as-is)
    
    Returns:
        Combined array with zeros removed from arr1
    """
    return [x for x in arr1 if x != 0] + arr2

# Test the function
print("\n" + "="*50)
print("REUSABLE FUNCTION TEST")
print("="*50)

test_array1 = [10, 0, 20, 0, 30, 0]
test_array2 = [40, 50, 60]

result = combine_arrays_remove_zeros(test_array1, test_array2)
print(f"Test Array 1: {test_array1}")
print(f"Test Array 2: {test_array2}")
print(f"Function Result: {result}")
