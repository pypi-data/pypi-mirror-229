#
# Copyright (c) nexB Inc. and others. All rights reserved.
# bitcode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/bitcode for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

CFG_INTBITSET_ENABLE_SANITY_CHECKS = True
from collections.abc import Iterable


class intbitset:
    def __init__(self, rhs=None, preallocate=-1, trailing_bits=0, sanity_checks=CFG_INTBITSET_ENABLE_SANITY_CHECKS,
                 no_allocate=0):
        self.bitset = set()
        if isinstance(rhs, int):
            self.add(rhs)
        elif isinstance(rhs, intbitset):
            self.bitset = rhs.bitset.copy()
        elif isinstance(rhs, Iterable):
            for value in rhs:
                self.add(value)

        self.preallocate = preallocate
        self.trailing_bits = trailing_bits
        self.sanity_checks = sanity_checks
        self.no_allocate = no_allocate

    def add(self, value):
        """
        Add an element to a set.
                This has no effect if the element is already present.
        """
        if value < 0:
            raise ValueError("Value can't be negative")
        self.bitset.add(value)

    def clear(self):
        self.bitset = set()

    def is_infinite(self):
        return False

    def extract_finite_list(self, up_to=""):
        return sorted(self.bitset)

    def copy(self):
        """ Return a shallow copy of a set. """
        new = intbitset()
        new.bitset = self.bitset.copy()
        return new

    def difference(self, *args):
        """ Return a new intbitset with elements from the intbitset that are not in the others. """
        new = intbitset()
        new.bitset = self.bitset.difference(*args)
        return new

    def difference_update(self, *args):
        """ Update the intbitset, removing elements found in others. """
        self.bitset.difference_update(*args)

    def discard(self, value):
        """
        Remove an element from a intbitset if it is a member.
                If the element is not a member, do nothing.
        """
        self.bitset.discard(value)

    def isdisjoint(self, other):
        """ Return True if two intbitsets have a null intersection. """
        return self.bitset.isdisjoint(other.bitset)

    def issuperset(self, other):
        """ Report whether this set contains another set. """
        return self.bitset.issuperset(other.bitset)

    def issubset(self, other):
        """ Report whether another set contains this set. """
        return self.bitset.issubset(other.bitset)

    def remove(self, key):
        """
        Remove an element from a set; it must be a member.
                If the element is not a member, raise a KeyError.
        """
        self.bitset.remove(key)

    def strbits(self):
        """
        Return a string of 0s and 1s representing the content in memory
                of the intbitset.
        """
        new = self.bitset
        if len(new) == 0:
            return ""
        res = ["0"] * (max(new) + 1)
        for _ in new:
            res[_] = "1"
        return ''.join(res)

    def symmetric_difference(self, other):
        """
        Return the symmetric difference of two sets as a new set.
                (i.e. all elements that are in exactly one of the sets.)
        """
        new = intbitset()
        new.bitset = self.bitset.symmetric_difference(other.bitset)
        return new

    def symmetric_difference_update(self, other):
        """ Update an intbitset with the symmetric difference of itself and another. """
        # self.bitset.symmetric_difference_update(other.bitset)
        # print("OwO", self.bitset, other.bitset)
        self.bitset.symmetric_difference_update(other.bitset)

    def tolist(self):
        """
        Legacy method to retrieve a list of all the elements inside an
                intbitset.
        """
        return list(self.bitset)

    def union(self, *args):
        """ Return a new intbitset with elements from the intbitset and all others. """
        new = intbitset()
        new.bitset = self.bitset.union(*args)
        return new

    def union_update(self, *args):
        """ Update the intbitset, adding elements from all others. """
        self.bitset = self.bitset.union(*args)

    def intersection(self, *args):
        """ Return a new intbitset with elements common to the intbitset and all others. """
        new = intbitset()
        new.bitset = self.bitset.intersection(*args)
        return new

    def intersection_update(self, *args):
        """ Update the intbitset, keeping only elements found in it and all others. """
        self.bitset.intersection_update(*args)

    def pop(self):
        sorted_lis = sorted(self.bitset)
        try:
            poped = sorted_lis.pop()
        except IndexError:
            raise KeyError
        self.bitset = set(sorted_lis)
        return poped

    def __and__(self, other):
        """
            Return the intersection of two intbitsets as a new set.
            (i.e. all elements that are in both intbitsets.)
        """
        new = intbitset()
        new.bitset = self.bitset & other.bitset
        return new

    def __or__(self, other):
        new = intbitset()
        new.bitset = self.bitset | other.bitset
        return new

    def __eq__(self, other):
        """ Return self==value. """
        return self.bitset == other.bitset

    def __contains__(self, key):
        """ Return key in self. """
        return key in self.bitset

    def __len__(self):
        """ Return len(self). """
        return len(self.bitset)

    def __iter__(self):
        """ Implement iter(self). """
        return iter(sorted(self.bitset))

    def __str__(self):
        ans = "intbitset(["
        for char in sorted(self.bitset):
            ans += str(char) + ", "
        ans = ans.rstrip(", ")
        ans += "])"
        return ans

    def __getitem__(self, item):
        sorted_list = sorted(list(self.bitset))
        if isinstance(item, slice):
            indices = range(*item.indices(len(sorted_list)))
            return [sorted_list[i] for i in indices]
        n = len(self.bitset)
        if item >= n:
            raise IndexError("Sequence index out of range")
        return sorted_list[item]

    def __iand__(self, other):
        self.bitset = self.bitset & other.bitset

    def __ior__(self, other):
        self.bitset = self.bitset | other.bitset

    def __xor__(self, other):
        new = intbitset()
        new.bitset = self.bitset ^ other.bitset
        return new

    def __ixor__(self, other):
        self.bitset = self.bitset ^ other.bitset

    def __sub__(self, other):
        new = intbitset()
        # if other == None:
        #     raise TypeError("operands must be an intbitset")
        new.bitset = self.bitset - other.bitset
        return new

    def __isub__(self, other):
        self.bitset = self.bitset - other.bitset

    def __ge__(self, other):
        return set.__ge__(self.bitset, other.bitset)

    def __gt__(self, other):
        return set.__gt__(self.bitset, other.bitset)

    def __le__(self, other):
        return set.__le__(self.bitset, other.bitset)

    def __lt__(self, other):
        return set.__lt__(self.bitset, other.bitset)
