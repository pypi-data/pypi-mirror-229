# adacut

A tool to "cut" versions out of an Ada source file.

The "cuts" are defined using lines that start with a `--$` comments marker.
Those lines are in the form `--$ {begin, end, line} {question, answer, cut} [{comment, code}]`

# Example

The file `titi_toto.ads`

```ada
--$ begin question
-- Titi?
--$ end question
--$ begin answer
-- Toto
--$ end answer
```

can be turned into two different sources using adacut:

`adacut -m question titi_toto.ads > titi.ads`
```ada
-- Titi?
```

`adacut -m answer titi_toto.ads > toto.ads`
```ada
-- Toto
```

The `-c <CUT>` switch allows to cut the given block.

`cuttable.ads`

```ada
--$ begin cut
    Answer : Integer := 1;
--$ end cut
--$ begin cut
    Answer : Integer := 2;
--$ end cut
```

`adacut -c 1 > cut.ads`
```ada
    Answer : Integer := 1;
```

# Test Adacut

You need pytest to be installed then simply run `$ pytest`

If you want to perform more exhaustive testing, you can use `tox`

`$ tox`
