'''
Created on 22-Jun-2019

@author: Uday
'''
#11. Two different numbers are called amicable numbers if the sum of the proper divisors of
# each is equal to the other number. For example 220 and 284 are amicable numbers.
# Sum of proper divisors of 220 = 1+2+4+5+10+11+20+22+44+55+110 = 284
# Sum of proper divisors of 284 = 1+2+4+71+142 = 220
# Write a function to print pairs of amicable numbers in a range


from Python_excercise_9 import sumPdivisors
def amic(n):
    z = []
    for i in range(n+1):
        a = sumPdivisors(i)
        b = sumPdivisors(a)
        if a == b:
            continue
        if i == b:
            if str(b)+'-'+str(a) not in z:
                z.append(str(a)+'-'+str(b))
    return z
print(amic(1000))
        
        


    