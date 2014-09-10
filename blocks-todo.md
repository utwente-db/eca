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

Block actions have been divided into three groups. The groups correspond to (pie chart, bar chart, word cloud), (log, tweet list), (rolling chart), and (normal x-y charts).

Actions are always emitted as follows:

    emit('event', {
        'action': action_name,
        'argument0': value0,
        'argument1': value1
    })

We note actions by their `action_name`. Optional argument are annotated with (optional). It is possible to emit to a block without giving a `'action'` field. If you do, the default action is used: usually this will generate a warning on the development console of the browser.


Category blocks (pie, bar, word cloud)
--------------------------------------

The category blocks are all blocks that somehow operate over categories. This includes word clouds, bar charts, pie charts.


### set
  - `series` (optional): a string indicating the series to operate on, if left out operate on default series
  - `value`: A pair `[ category, value ]` that is inserted as a new category, or replaces the existing category

Adds the given category to the block and sets its value at the given value. If the category already exists its current value is overwritten by the given value.

### add
  - `series` (optional): a string indicating the series to operate on, if left out operate on default series
  - `value`: A pair `[ category, value ]` that is inserted as a new category, or the value is added to the existing category

Updates the block by adding the given value to the given categories current value. If the category does not exist, it is created at a value of `0` before the update is executed.

### del
  - `series` (optional): a string indicating the series to operate on, if left out operate on default series
  - `category`: a string indicating the category that is to be removed

Removes a category from the block. This is different from setting a category to `0`: visual elements related to the category will be completely removed.

### reset
  - `series` (optional): a string dinciating the series to operate on, if left out will reset all series

Resets the block to its original state.


Rolling Chart
-------------

The rolling chart is a special case of chart. It supports series, but must be updated in a single action.

### add
  - `values`: a dictionary of the form `{ 'series0': value0, 'series1': value1, ... }` to update

Each series of the block is updated with the given value. Any series that is left out will not be updated for this interval, and will instead be shown as a break in the graph.

### reset
Resets this block to its initial values.
