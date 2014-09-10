Blocks Todo
===========

We have identified the following blocks as the minimum necessary:
  - Log
  - Tweet list
  - Word cloud
  - Charts:
    - rolling
    - pie
    - bar (bar per category)
    - normal x,y (this is a group of charts)

Optionally, we want to implement:
  - Map
  - Form


Actions
=======

Block actions have been divided into three groups. The groups correspond to (pie chart, bar chart, word cloud), (log, tweet list), (rolling char), and (normal x-y charts).

Actions are always emitted as follows:

    emit('event', {
        'action': action_name,
        'argument0': value0,
        'argument1': value1
    })

We note actions by their `action_name`. Optional argument are annotated with (optional).


Category blocks (pie, bar, word cloud)
======================================

The category blocks are all blocks that somehow operate over categories. This includes word clouds, bar charts, pie charts.


set
---
  - `series` (optional): a string indicating the series to operate on, if left out operate on default series
  - `value`: A pair `[ category, value ]` that is inserted as a new category, or replaces the existing category


add
---
  - `series` (optional): a string indicating the series to operate on, if left out operate on default series
  - `value`: A pair `[ category, value ]` that is inserted as a new category, or the value is added to the existing category

del
---
  - `series` (optional): a string indicating the series to operate on, if left out operate on default series
  - `category`: a string indicating the category that is to be removed

reset
-----
  - `series` (optional): a string dinciating the series to operate on, if left out will reset all series
