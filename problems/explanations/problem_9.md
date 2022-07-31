The code has a bug! The problem is that we only want to find the **proper** divisors of a number, but the code
counts the number itself as one of its proper divisors!
Correcting is straightforward since we only need to change the last function.
#### Corrected Code:
```
17    def __proper_divisors(number):
18        divisors = list()
19    for i in range(1, (number/2)+1): # using number/2+1 as the upper band so that we will never consider it a divisor  
20        if number % i == 0:
21            divisors.append(i)
22    return divisors
```
