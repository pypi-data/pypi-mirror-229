class BubbleSort:
    def sort(self, arr):
        """
        Perform bubble sort on the input list 'arr' in-place.

        :param arr: The input list to be sorted.
        """
        n = len(arr)

        for i in range(n - 1):
            # Flag to check if any swaps were made in this pass
            swapped = False

            # Last i elements are already in place, so we don't need to check them
            for j in range(0, n - i - 1):
                if arr[j] > arr[j + 1]:
                    # Swap arr[j] and arr[j+1]
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
                    swapped = True

            # If no two elements were swapped in this pass, the list is already sorted
            if not swapped:
                break


# Example usage:
if __name__ == "__main__":
    bubble_sort = BubbleSort()
    my_list = [64, 34, 25, 12, 22, 11, 90]

    print("Original List:", my_list)
    bubble_sort.sort(my_list)
    print("Sorted List:", my_list)
