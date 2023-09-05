# numequate/base.py
    
def fibonacci(n):
    if n < 0:
        raise ValueError("Fibonacci is undefined for negative integers.")
    
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        return b

def gcd(a, b):
    if a < 0 or b < 0:
        raise ValueError("GCD is undefined for negative integers.")
    
    while b:
        a, b = b, a % b
    
    return a

def power(base, exponent):
    return base ** exponent

def clamp(value, min_value, max_value):
    return max(min(value, max_value), min_value)

def lerp(start, end, alpha):
    return start + (end - start) * alpha

def map_range(value, in_min, in_max, out_min, out_max):
    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b != 0:
        return a / b
    else:
        raise ValueError("Cannot divide by zero")