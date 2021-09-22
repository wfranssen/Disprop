import itertools as it

def distanceIsOne(s1,s2):
    """
    Checks if edit distance between s1 and s2 is exactly 1.
    The order of s1 and s2 is not important.
    """
    if s1 == s2: # distance 0 not allowed
        return False
    l1 = len(s1)
    l2 = len(s2)
    if l1 < l2: # Make s1 the longest
        l1, l2 = l2, l1
        s1, s2 = s2, s1
    if l1 == l2:
        # If equal length, check each char, and allow one difference
        dist = 0
        for pos in range(l1):
            if s1[pos] != s2[pos]:
                dist += 1
            if dist == 2:
                return False
        return True
    elif l1-1 == l2:
        # If one element different, loop over 'remove' position
        # And check each char, allowing no changes.
        for delpos in range(l1):
            for elem in range(l2):
                elem2 = elem
                if elem >= delpos:
                    elem2+=1
                if s1[elem2] != s2[elem]:
                    break
            else: # If no problem found, good solution
                return True
        # If no loop ended normally, there was no good solution.
        return False
    else:
        return False

def distanceIsTwo(s1,s2):
    """
    Checks if edit distance between s1 and s2 is exactly 2.
    The order of s1 and s2 is not important.
    """
    l1 = len(s1)
    l2 = len(s2)
    if l1 < l2: # Make s1 the longest
        l1, l2 = l2, l1
        s1, s2 = s2, s1
    if l1 == l2:
        # If equal length, check each char, and allow two difference
        dist = 0
        for pos in range(l1):
            if s1[pos] != s2[pos]:
                dist += 1
            if dist == 3:
                break
        else: #If no issues, it was good
            if dist == 2: #Because this function checks equal 2 only.
                return True
        #Otherwise we continue, checking
        #For 1 remove + 1 insert option
        for delpos, addpos in it.product(range(l1),range(l1)):
            for elem in range(l2):
                elem2 = elem
                if elem >= delpos:
                    elem2+=1
                if elem == addpos: # skip added char
                    continue
                if elem > addpos:
                    elem2+= -1
                if s1[elem2] != s2[elem]:
                    break
            else: # If no problem found, good solution
                return True
        # If no loop ended normally, there was no good solution.
        return False

    elif l1-2 == l2:
        """
        Allow two remove indexes. Check all options.
        """
        for delpos1, delpos2 in it.product(range(l1),range(l1)):
            for elem in range(l2):
                elem2 = elem
                if elem >= delpos1:
                    elem2+=1
                if elem >= delpos2:
                    elem2+=1
                if s1[elem2] != s2[elem]:
                    break
            else: # If no problem found, good solution
                return True
        # If no loop ended normally, there was no good solution.
        return False
    else:
        return False
 
