
from __future__ import annotations

import dataclasses as dc
import typing as t
import re

@dc.dataclass
class Matcher:
    """ Allows for recursive pattern matching.
    
        Instances of this class can be used as decorators around functions - this will set the decorated function as that instance's :attr:`on_match` callback. """


    match_pattern_str: dc.InitVar[str] = r"[\w\W]*"
    r""" The string pattern that will be used to match text for this :class:`Matcher` to :meth:`process`. """

    on_match: t.Callable[..., str] = lambda: ""
    r""" Returns a processed string. The arguments to this callback function must match the number of groups in this :class:`Matcher`'s :attr:`match_pattern`. """

    inner_matchers: list[Matcher] = dc.field(default_factory=list)
    r""" Each inner :class:`Matcher` :meth:`process`\\ es the entirety of the :attr:`match_pattern`'s match (:meth:`re.Pattern.group`). """
    
    group_matchers: list[Matcher] = dc.field(default_factory=list)
    r""" Each group :class:`Matcher` :meth:`process`\\ es a single group in the :attr:`match_pattern` and returns the processed text to be given to the :attr:`on_match` callback as an argument. """

    match_pattern: re.Pattern[str] = dc.field(init=False)
    r""" The compiled version of :attr:`match_pattern_str`. """

    def __post_init__(self, take_pat: str):
        self.match_pattern = re.compile(take_pat)
    
    def __call__(self, callback: t.Callable[..., str]):
        self.on_match = callback
        return self
    
    def process(self, text: str) -> str:
        """ Returns processed text based on an input string.
        
            The input string is matched against the :attr:`match_pattern` using :meth:`~re.Pattern.finditer`, and each resulting :class:`re.Match`'s :meth:`~re.Match.groups` is :meth:`process`\\ ed by its coresponding :attr:`group_matcher` to correct the :meth:`~re.Match.groups` for the :attr:`on_match` callback.
            
            The processed text is collected, then appended to by calling each :attr:`inner_matcher`'s :meth:`process` method on the entirety of the :class:`re.Match`'s match :meth:`~re.Match.group`. """

        processed = ""
        for re_match in self.match_pattern.finditer(text):
            groups = [matcher.process(re_group) for matcher, re_group in zip(self.group_matchers, re_match.groups())]
            processed += self.on_match(*groups)
            full_match = re_match.group()
            for inner_matcher in self.inner_matchers:
                processed += inner_matcher.process(full_match)
        return processed
    
    def group(self):
        """ Returns a :class:`Matcher` that has been added to the list of :attr:`group_matchers`.
        
            This should be called once for each group in the :attr:`match_pattern`. """

        self.group_matchers.append(Matcher())
        return self.group_matchers[-1]
    
    def matcher(self, match_pat_str: str=r"[\w\W]*"):
        """ Returns a new :class:`Matcher` that has been added to the list of :attr:`inner_matchers`. """

        self.inner_matchers.append(Matcher(match_pat_str))
        return self.inner_matchers[-1]
    
    def quick_steps(self, steps: dict[str, str | t.Callable[..., str]]):
        """ Adds a collection of simple substitution :class:`Matcher`\\ s to the list of :attr:`inner_matchers`.
        
            Each pair in ``steps`` should be a regex pattern string mapped to either a replacement value or a lambda :attr:`on_match` callback. """

        for regex, replacer in steps.items():
            if isinstance(replacer, str):
                replacer = lambda: replacer
            replacer = t.cast(t.Callable[..., str], replacer) # appease pylance
            self.inner_matchers.append(Matcher(regex)(replacer))