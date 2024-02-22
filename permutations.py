from __future__ import annotations
from itertools import product
from random import choice
from re import sub

# A permutation class to denote elements of the permutation group S_n
class Perm:

    # takes in the description of the permutation as a disjoint cycle decomposition and optionally, maximum = n (as in S_n)
    def __init__(self, description: str, maximum: int = None) -> None:
        self.description: list[list[int]] = [[int(j) for j in (i * 2)] for i in (description.strip("()").split(")("))]
        self.max: int = max([max(i) for i in self.description]) if maximum is None else maximum
        self.string: str = self.apply(self.max, self.description)
    
    # the result of actually applying the schematic to the set {1 ... n}, written out as disjoint cycles 
    def apply(self, maximum: int, cycles: list[list[int]]):
        result = []

        # for each cycle in the result, len-1 is the number of items. this repeats while there are still items to go
        while sum([len(i) - 1 for i in result]) < maximum:

            # find the first element in {1 ... n} which is not yet logged in the cycles, and add it to a new element
            element = min([i for i in range(1, maximum + 1) if not any (i in r for r in result)])
            result.append([element])

            # then find its orbit (keep applying until we get back to the original element)
            while result[-1].count(element) < 2:
                new = result[-1][-1]
                for cycle in cycles:
                    if new in cycle:
                        new = cycle[cycle.index(new) + 1]
                result[-1].append(new)

        # format this as disjoint cycles and return the string
        return "(" + ")(".join(["".join(map(str, r[:-1])) for r in result]) + ")"
    
    # returns the cycle's disjoint cycle decomposition as a string
    def __repr__(self) -> str:
        return self.string

    def __str__(self) -> str:
        return sub("\(\d\)", "", self.__repr__()) or "e"
    
    # element multiplication within S_n is just permutation composition
    def __mul__(self, other: Perm) -> Perm:
        return Perm(self.apply(max(self.max, other.max), other.description[::-1] + self.description[::-1]))
    
    # elements raised to an integer power n are:
    def __pow__(self, power: int) -> Perm:

        # ((a)^-1)^-n if n is negative
        if power < 0:
            return (self ** (-power)).inverse()
        
        # the identity if n is 0
        elif power == 0:
            return Perm("", self.max)
        
        # the element itself if n is 1
        elif power == 1:
            return self
        
        # the element multiplied by itself repeatedly if n > 1
        return self.__pow__(power - 1) * self
        
    # luckily, every element of S_n has finite order, so we can find its inverse through repeat multiplication
    @property
    def inverse(self) -> Perm:
        x = self

        # while the result of multiplying x and the original element is not the identity, set x to the new element
        while (new := (x * self)) != Perm("", self.max):
            x = new

        return x
    
    # let's find the order in pretty much the same way as we find the inverse
    @property
    def order(self) -> int:
        x, n = self, 1

        # while the result of multiplying x and the original element is not the identity, set x to the new element
        while (new := (x * self)) != Perm("", self.max):
            x, n = new, n + 1

        return n + 1
            
    # this is an injective function from the union of all S_n to the naturals
    def __hash__(self) -> int:
        return int("".join((c if c.isnumeric() else "0" for c in self.string)))
    
    # use the hash to compare two permutations
    def __eq__(self, __value: Perm) -> bool:
        return isinstance(__value, Perm) and self.__hash__() == __value.__hash__()

    # we can also use them to compare permutations for some semblance of sorting
    def __lt__(self, other):
        return self.__hash__() > other.__hash__()
            

# for some set of specified elements, keep going until we find the group they generate
def generate_group(*elements: list[Perm]) -> list[Perm]:

    # while we're still adding stuff to the group
    group, size = list(elements), 0
    while size != len(group):
        size, new = len(group), []

        # multiply every pair of elements and add their product to the group
        for (sigma, tau) in product(group, group):
            if (prod := sigma * tau) not in group and prod not in new:
                new.append(prod)
        
        # add on the new elements to the group
        group = group + new

    return sorted(group)


# the sgn function: this works by counting even-length cycles (as these are odd)
def sgn(sigma: Perm):
    sigma = str(sigma).strip("()").split(")(")
    return (-1) ** sum((len(s) + 1 for s in sigma))


# ========================================================================================================================= #


# run some tests
if __name__ == "__main__":

    # these two elements should generate the symmetric group S_4
    S_4 = generate_group(
        Perm("(1234)"),
        Perm("(123)(4)")
        )
    print(f"Generated group S₄ with {len(S_4)} elements:\n {{{', '.join(map(str, S_4))}}}\n")

    # elements with sgn(sigma) = 1 are the even elements: the ones in A_4
    A_4 = [sigma for sigma in S_4 if sgn(sigma) == 1]
    print(f"Isolated group A₄ with {len(A_4)} elements:\n {{{', '.join(map(str, A_4))}}}\n")

    # chooses random element and does some analysis on it
    sigma = choice(S_4)
    print(f"Analysing element {sigma}:\n Order = {sigma.order}\n Inverse = {sigma.inverse}\n Sign = {sgn(sigma)}")
    print(f" Generated group = {{{', '.join(map(str, generate_group(sigma)))}}}")


    # chooses another random element and does some analysis on it
    tau = choice(S_4)
    print(f" Example multiplication: {sigma} * {tau} = {sigma * tau}")


"""

SAMPLE OUTPUT
=============

Generated group S₄ with 24 elements:
 {e, (14), (13), (12), (24), (23), (34), (143), (142), (14)(23), (134), (132), (13)(24), (124), (123), (12)(34), (243), (234), (1432), (1423), (1342), (1324), (1243), (1234)}

Isolated group A₄ with 12 elements:
 {e, (143), (142), (14)(23), (134), (132), (13)(24), (124), (123), (12)(34), (243), (234)}

Analysing element (1324):
 Order = 4
 Inverse = (1423)
 Sign = -1
 Generated group = {e, (12)(34), (1423), (1324)}
 Example multiplication: (1324) * (14) = (243)

"""