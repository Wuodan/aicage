# TODO

These are my personal work-in-progress notes about things I don't want to forget. Not all are todos, most are reminders
to look into something.

## Custom folder

Move location of custom additions by user to `~/.aicage-custom` (or maybe `~/.aicage-custom/custom`).
Right now `~/.aicage-custom` contains an ugly mix of user-additions and folders managed by `aicage`.
Those folders managed by aicage should not be in a `custom` folder for clarity, they store stuff for aicage.

And currently I cannot just delete `~/.aicage` as I would lose my custom additions

## images-metadata.yaml

Currently produced by `aicage-image` as a merge of bases from `aicage-image-base` and the agents in `aicage-image`.

This was in current form useful when `aicage` did not have all agents and could not calculate `valid_bases` by itself.

But now it can. And we have to on-the-fly preprocess-update the data in its python mirror class `ImagesMetadata` to add
in custom local agents and custom local bases. Extensions fly outside `ImagesMetadata` and are neatly stored in
`ConfigContext` and read from there when needed (without pre-processing), this is much neater.
