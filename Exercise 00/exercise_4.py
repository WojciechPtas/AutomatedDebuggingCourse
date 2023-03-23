
def average(l: list) -> float:
    """
    Calculates the average of a number list.
    """
    #s = 0
    #for i in range(len(l)):
    #    s += l[i]
    #return s / len(l)
    return sum(l)/len(l)


def middle(x: int, y: int, z: int) -> int:
    """
    Finds the middle of three arguments x, y, and z that is neither the maximum nor the minimum.
    """
    if (x <= y and y <= z) or (z <= y and y <= x):
        return y
    elif (y <= x and x <= z) or (z <= x and x <= y):
        return x
    else:
        return z
    

def reverse_list(l: list) -> list:
    """
    Returns l in reversed order, e.g., reverse_list([1, 2, 3]) == [3, 2, 1]
    """
    #pass
    newList = l[::-1]
    
    return newList

def sort_list(l: list) -> list:
    """
    Returns l in ascending order, e.g., sort_list([3, 1, 2]) == [1, 2, 3]
    """
    l.sort()
    return l
    #pass

def each_other(l: list) -> list:
    """
    Returns every second element of l starting from the first, e.g., reverse_list([1, 2, 3, 4, 5]) == [1, 3, 5]
    """
    newList =l[::2]
    return newList
    #pass

def all_even(l: list) -> list:
    """
    Returns all even elements of l in order, e.g., reverse_list([4, 3, 2]) == [4, 2]
    """
    return [nums for nums in l if nums%2==0]
    #pass

    
######## Tests ########

def test_average():
    assert average([1, 2, 3]) == 2
    assert average([2, 2, 2]) == 2
    assert average([0, 2, 4]) == 2
    

def test_middle():
    assert middle(1, 2, 3) == 2
    assert middle(3, 2, 1) == 2
    assert middle(2, 1, 3) == 2
    assert middle(2, 3, 1) == 2
    assert middle(1, 3, 2) == 2
    assert middle(3, 1, 2) == 2
    

def test_lists():
    assert reverse_list([2, 3, 1, 4]) == [4, 1, 3, 2]
    assert reverse_list([4, 3, 2, 1, 5]) == [5, 1, 2, 3, 4]
    assert sort_list([2, 3, 1, 4]) == [1, 2, 3, 4]
    assert sort_list([4, 3, 2, 1, 5]) == [1, 2, 3, 4, 5]
    assert each_other([2, 3, 1, 4]) == [2, 1]
    assert each_other([4, 3, 2, 1, 5]) == [4, 2, 5]
    assert all_even([2, 3, 1, 4]) == [2, 4]
    assert all_even([4, 3, 2, 1, 5]) == [4, 2]
    
    
if __name__ == '__main__':
      
    try:
        test_average()
    except AssertionError:
        print('0.4.a seems NOT OK')
    else:
        print('0.4.a seems OK')
    try:
        test_middle()
    except AssertionError:
        print('0.4.b seems NOT OK')
    else:
        print('0.4.b seems OK')
    try:
        test_lists()
    except AssertionError:
        print('0.4.c seems NOT OK')
    else:
        print('0.4.c seems OK')
    

