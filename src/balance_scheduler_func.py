import math
import collections
from typing import List, Optional


Card = collections.namedtuple('Card', ['id', 'day', 'ivl'])
Vacation = collections.namedtuple('Vacation', ['start', 'end', 'factor'])

# Raw balancing function which assumes 0 to be today
# schedule and vacation origins must also be today

def balance(
    cards: List[Card],
    today: int=0,
    revs_done_today: int=0,
    num_days: int=365,
    move_factor: float=0.1,
    schedule_factors: Optional[List[float]]=None,
    vacations: Optional[List[Vacation]]=None,
) -> List:

    # "day" variables are always normalized with 0 being today

    if schedule_factors is None:
        schedule_factors = [1.0]
    if vacations is None:
        vacations = []

    num_schedule_days = len(schedule_factors)


    # Sorting

    # A movability value is assigned to each card
    #   higher interval -> higher movability
    #   due later -> higher movability

    day_counts = [0] * num_days
    cards_sort = []

    for card in cards:
        day = card.day - today
        if day < num_days:
            movability = pow(card.ivl, 0.8) + day
            cards_sort.append((movability, card))
            if day >= 0:
                day_counts[day] += 1

    day_counts[0] += revs_done_today
    cards_sort.sort(key=lambda x: x[0], reverse=True)


    # Balancing

    day_factors = []

    for day in range(num_days):
        day_factor = schedule_factors[(day + today) % num_schedule_days]
        day_factors.append(day_factor)

    for start, end, fac in vacations:
        for day_shifted in range(start, end + 1):
            day = day_shifted - today
            if 0 <= day < num_days:
                day_factors[day] *= fac

    cards_to_balance = []

    # Cards with a higher movability value are moved first
    # This slowly creates a balance so that cards with a
    # lower movability have a lower chance of being moved a lot

    for _, card in cards_sort:
        day = card.day - today

        # Only move cards within the range of days
        if day >= num_days:
            continue

        # The move range of overdue cards is decreased by the overdue amount
        # Prevents cards being moved back over and over
        overdue = max(0, day - today)
        adj_ivl = max(0, card.ivl - overdue)

        mov = math.floor(adj_ivl * move_factor)

        # Find the day with the least amount of cards in the possible range
        start = max(0, day - mov)
        end = min(num_days - 1, day + mov)

        # Increase the range until there are at least mov+1 possible factored days in the span
        # NOTE: This can be optimized by reusing sums
        num_possible = 0
        while True:
            if start == 0 and end == num_days - 1:
                break

            num_possible = 0
            for i in range(start, end + 1):
                num_possible += day_factors[i]

            if num_possible >= mov + 1:
                break

            start = max(0, start - 1)
            end = min(num_days - 1, end + 1)

        # If there are no possible balanced day, the card keeps the unbalanced day
        #   This should only happen if there are no possible days in the balance span
        if num_possible < 1:
            target_day = day

        else:
            target_day = None
            target_rating = None

            for i in range(start, end + 1):
                day_factor = day_factors[i]

                if day_factor <= 0:
                    continue

                # Slightly prefer placing around the optimal day
                rating_factor = 2 - math.cos((i - day) / max(1, day - start, end - day))

                rating = day_counts[i] * rating_factor * 1/day_factor

                if target_rating is None or rating <= target_rating:
                    target_day = i
                    target_rating = rating

        # Add the card to the best day
        cards_to_balance.append((card, target_day + today))

        day_counts[target_day] += 1
        if day >= 0:
            day_counts[day] -= 1

    return cards_to_balance
