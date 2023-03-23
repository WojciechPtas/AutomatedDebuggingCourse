# Report

## Function ex_1

If the provided input is non-negative, function will terminate without entering the loop. In other case, with each iteration the value of *i* will increase, which will lead to eventually value of *i* becoming positive, which means that this function **terminates at all inputs**

## Function ex_2

This function will not terminate at all inputs i. e. `i = -27`. Coverages for this particular input are presented below.
```
   5   0% def ex_2(i: int):
   6  49%     while i != 1 and i != 0:
   7  49%         i = i - 2
```
If the input is a non-negative number the loop will terminate after a while, because *i* will be decreased either to 0 or 1. When we provide a negative input, *i* will be only decreased which means that the loop will execute forever.


## Function ex_3

This function will not terminate at all inputs i. e. `i = 10, j = 1`. Coverages for this particular input are presented below.
```
   9   0% def ex_3(i: int, j: int):
  10  33%     while i != j:
  11  33%         i = i - 1
  12  33%         j = j + 1
```
If condition *i < j* holds initially, they will never be equal, as *i* decreases and *j* increases with each iteration. In the other case, the loop will not terminate when their mean is a non-integer (their sum is non-divisible by two).

## Function ex_4

This function will not terminate at all inputs i. e. `i = -4`. Coverages for this particular input are presented below.
```
  14   0% def ex_4(i: int):
  15  33%     while i >= -5 and i <= 5:
  16  33%         if i > 0:
  17   0%             i = i - 1
  18  33%         if i < 0:
  19   0%             i = i + 1
```
If *i* is out of bounds created by the while condition, it won't enter the loop, otherwise, it will never leave, as it will converge to 0, because we increase negative numbers and decrease positive numbers.


## Function ex_5

This function will not terminate at all inputs i. e. `i = -1`. Coverages for this particular input are presented below.
```
  21   0% def ex_5(i: int):
  22   0%     while i < 10:
  23   0%         j = i
  24  49%         while j > 0:
  25  49%             j = j + 1
  26   0%         i = i + 1
```
If *i* is less than then 10, the inner while loop will never terminate. Even if *i* is a negative numvber, it will be increased to one, and than the inner loop will execute forever.

## Function ex_6

This function will terminate for every possible input. Value of *c* does not influcence the termination of the loop. For the outer loop, we decrease the *i* in every iteration which ensures that eventuallt it will become less than zero. For the inner loop, we increase the value of *j* which ensures that eventually it will become greater than *i-1*.