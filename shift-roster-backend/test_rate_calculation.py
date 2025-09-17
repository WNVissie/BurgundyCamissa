#!/usr/bin/env python3
"""
Quick test to verify rate calculation logic
"""

def calculate_hourly_rate(rate_value, rate_type):
    """Convert any rate type to hourly rate"""
    if rate_type == 'weekly':
        return rate_value / 40  # 40 hours per week
    elif rate_type == 'daily':
        return rate_value / 8   # 8 hours per day
    elif rate_type == 'monthly':
        return rate_value / 160  # 160 hours per month (4 weeks * 40 hours)
    elif rate_type == 'hourly':
        return rate_value
    else:
        return 0

def calculate_cost(hours_worked, rate_value, rate_type):
    """Calculate total cost for hours worked"""
    hourly_rate = calculate_hourly_rate(rate_value, rate_type)
    return hours_worked * hourly_rate

# Test scenarios
print("Rate Calculation Test:")
print("=" * 40)

# Test 1: Weekly rate R5000 for 52 hours
rate_value = 5000
rate_type = 'weekly'
hours_worked = 52

hourly_rate = calculate_hourly_rate(rate_value, rate_type)
total_cost = calculate_cost(hours_worked, rate_value, rate_type)

print(f"Weekly rate: R{rate_value}")
print(f"Hourly rate: R{hourly_rate:.2f} (R{rate_value} ÷ 40 hours)")
print(f"Hours worked: {hours_worked}")
print(f"Total cost: R{total_cost:.2f}")
print(f"Expected: R{52 * (5000/40):.2f}")
print()

# Test 2: Daily rate R625 for 26 hours
rate_value = 625
rate_type = 'daily'
hours_worked = 26

hourly_rate = calculate_hourly_rate(rate_value, rate_type)
total_cost = calculate_cost(hours_worked, rate_value, rate_type)

print(f"Daily rate: R{rate_value}")
print(f"Hourly rate: R{hourly_rate:.2f} (R{rate_value} ÷ 8 hours)")
print(f"Hours worked: {hours_worked}")
print(f"Total cost: R{total_cost:.2f}")
print(f"Expected: R{26 * (625/8):.2f}")
print()

# Test 3: Hourly rate R125 for 26 hours
rate_value = 125
rate_type = 'hourly'
hours_worked = 26

hourly_rate = calculate_hourly_rate(rate_value, rate_type)
total_cost = calculate_cost(hours_worked, rate_value, rate_type)

print(f"Hourly rate: R{rate_value}")
print(f"Hours worked: {hours_worked}")
print(f"Total cost: R{total_cost:.2f}")
print(f"Expected: R{26 * 125:.2f}")
