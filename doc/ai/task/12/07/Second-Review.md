# Review TODOS

## Unit test structure heavily violated

I am picky on this, the trask instruction documents reference `doc/python-test-structure-guidelines.md`
and in this session I already had to remind you about guidelines in
`doc/python-test-structure-guidelines.md`.

But you don't get it or chose to ignore those guidelines.

Just one example, there are surely more: `src/aicage/registry/image_selection` has a bunch of files.  
But on the test-side you crammed all unit tests for this package into one file:

- `tests/aicage/registry/image_selection/test_selection.py`

This is totally non-acceptable. If you further continue this pattern I will have you cough up a test
just to validate test-structure.

## `prompts` package

- src/aicage/runtime/prompts/tty.py
- src/aicage/runtime/prompts/yes_no.py

The above modules are still public. Looking where they are used outside their package shows places
where user is prompted outside the `prompts` package.

## `src/aicage/registry/image_selection/extensions.py` to large

The file is too large, create a package for it.

## Reverse test for visibility: Detect where visibility is unnecessarily public

I really like your latest test for visibility as it frees me from babysit-reviews.  
The other thing which is even harder for me to detect during reviews is where methods or modules are
public without need.

Can you suggest a test-strategy to detect this or is this going too far?
