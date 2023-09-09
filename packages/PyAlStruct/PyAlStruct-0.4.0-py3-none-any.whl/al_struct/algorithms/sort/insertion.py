class InsertionSort:
    def sort(self, arr):
        """
        Perform insertion sort on the input list 'arr' in-place.

        :param arr: The input list to be sorted.
        """
        for i in range(1, len(arr)):
            key = arr[i]
            j = i - 1

            # Move elements of arr[0..i-1], that are greater than key, one position ahead
            while j >= 0 and key < arr[j]:
                arr[j + 1] = arr[j]
                j -= 1

            arr[j + 1] = key


# Example usage:
if __name__ == "__main__":
    insertion_sort = InsertionSort()
    my_list = [64, 34, 25, 12, 22, 11, 90]

    print("Original List:", my_list)
    insertion_sort.sort(my_list)
    print("Sorted List:", my_list)
