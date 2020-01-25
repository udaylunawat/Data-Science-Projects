'''
Created on 22-Jun-2019

@author: Uday
'''
#2 .Write a program to print twin primes less than 1000. 
#If two consecutive odd numbers are both prime then they are known as twin primes


l = []
for i in range(1,1000,2):
    for j in range(i-1,1,-1):
        flag = 0
        if i%j == 0:
            flag = 1
            break
        elif j == 2 and flag == 0:
            l.append(i)
print("Twin primes under 1000")
for i in range(1,len(l)):
    if l[i]-l[i-1]==2:
        print(l[i-1],l[i])
#     if abs(item - l[count+1]) == 2:
#         print(item,l[count+1])
