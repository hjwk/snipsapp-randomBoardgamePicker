def extractSlot(slots, slot):
    if slots[slot]:
        return int(slots[slot].first().value)

    return None