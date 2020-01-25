'''
Created on 22-Jun-2019

@author: Uday
'''
#14. Write a program which can map() and filter() to make a list whose elements are cube of even number in a given list


lst = [1,2,3,4,5,6,7,8,9]
x = list(map(lambda x:x*x*x ,list(filter(lambda x:(x%2==0),lst))))
print(x)