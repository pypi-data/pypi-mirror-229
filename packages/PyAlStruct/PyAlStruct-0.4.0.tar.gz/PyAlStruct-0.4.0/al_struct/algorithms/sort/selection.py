class SelectionSort:
    def sort(self, arr):
        """
        Perform selection sort on the input list 'arr' in-place.

        :param arr: The input list to be sorted.
        """
        n = len(arr)

        for i in range(n - 1):
            min_index = i

            # Find the index of the minimum element in the unsorted part of the list
            for j in range(i + 1, n):
                if arr[j] < arr[min_index]:
                    min_index = j

            # Swap the minimum element with the first element of the unsorted part
            arr[i], arr[min_index] = arr[min_index], arr[i]


# Example usage:
if __name__ == "__main__":
    bubble_sort = SelectionSort()
    my_list = [64, 34, 25, 12, 22, 11, 90]

    print("Original List:", my_list)
    bubble_sort.sort(my_list)
    print("Sorted List:", my_list)
