# Solving osu!mania streching skin issues

## What I figured out
Everything in game is based on the height of 480px, and sizing some elements is based on a ratio of 1.6.

## Ingame
- Receptors are downscaled by a factor of 1.6, then stretched to match the `ColumnWidth` (value on the <b>skin.ini</b> file).
- Note parts are just scaled to the column's width, maintaining their aspect ratio.

This is why receptors are sometimes stretched, while notes and long notes are not.
And it was a pain to figure out why, and also figure out a way to fix it.

So what i did to fix it, which involved uniform square images for every component, was the following:

## Receptors
1. Downscale image's width to `ReceptorWidth * 1.6`, while maintaining aspect ratio.
2. Add a padding of `Spacing * 1.6`, half to the left and right of image.
3. Add a padding of `HitPosition * 1.6`, above and below image (above is optional).
- The resulting image will be a receptor including proper spacing and width.
- No stretching should occur ingame, however the resolution is severely limited.
- The `ColumnWidth` is `ReceptorWidth + Spacing`.

## Note / Hold parts
1. Add padding of `ImageWidth * Spacing / ColumnWidth` px to the left and right of image.
- The resulting image is the part including proper spacing.
- Width can be anything, thus the resolution is not limited.

## Centered ColumnStart
- `(480 * ScreenRatio - ColumnWidth * Keys) / 2`.
- This will perfectly center the note field.

## And how do i do all of this?
You could use some image editing software, or you can use my python script along with it's customizable skin properties text file to make your own skin.

# Editing your skin
Before anything, make sure to clone this repository into your skin folder, from where you should be working with.
Your skin should look something like this:
```
SkinFolder/
    mania/
        src/
            ...
        README.md
        blank.png
        getffmpeg.py
        osu!receptor.py
        skin.txt
        ...
    skin.ini
    ...
```
Note: the `mania` folder can have any name.

## skin.txt
This is a sequence of commands for creating skin elements automatically, including scaling images and what not.

## The <b>skin.ini</b> header
```
header
... skin.ini config stuff ...
header
```
- Will always add this bit of text at the beginning of the generated <b>skin.ini</b>.
- Make sure to encase the entire header between those two header lines

## Generic mania skin settings
```
base [hide marvelous]
... skin.ini config stuff for mania key layouts...
base
```
- Will always add this bit of text at the beginning of each generated key layout.
- Make sure to encase the entire base between those two base lines
- If `[hide marvelous]` is `1`, it will hide the marvelous judgement when playing.

## Set component types
`set [name] [type] <redirect>`
- `[name]`: Name of the component to set. Can be `note`, `hold-head`, `hold-body`, `hold-tail`, `receptor-up` or `receptor-down`.
- `[type]`: Type of the component to set. Can be:
- - `variable`: Has various forms (eg. arrow directions), will apply the column's layout value as a suffix.
- - `static`: Is always the same regardless of the column's layout value.
- - `redirect`: Will make use of another component's values and images as its own.
- `<redirect> ([type] = redirect)`: The component to redirect to.

## Create key layouts
`keys [keys] [receptor width] [spacing] [hit position] [transparency] [layout]`
- `[keys]`: The number of keys for this key layout.
- `[receptor width]`: The receptor's width.
- `[spacing]`: The spacing between receptors.
- `[hit position]`: The offset relative to the bottom of the screen of where notes are hit.
- `[lane transparency]`: The transparency of each column.

## Src file names
Files in the `src` folder should have specific names, and should not include files that are not needed to create the skin.

Each file should have the name:
- `[name][layout col].png` for `variable` type components, where `[name]` is one of the names from the set command, and `[layout col]` is a character telling where it lands in the `[layout]` for each key layout.
- `[name].png` for `static` type components, where `[name]` is one of the names from the set command.
- `redirect` type components use an existing file as its own.

## Finishing the skin
Finally, to create the <b>skin.ini</b> file that recognises the created files as part of the skin, all you have to do is run `osu!receptor.py` with python 3.9 or higher. But watch out, this will replace the old <b>skin.ini</b> in your skin with a new one based on your skin.txt settings!

## Cleaning up
If you want to cleanup the skin's files for sharing, you can get rid of the following files/folders:
```
src\
    ...
ffmpeg.exe
README.md
getffmpeg.py
receptorstyle.py
skin.txt
```
However, doing this will get rid of every file needed to adjust the skin.
You can always just delete `ffmpeg.exe` when distributing, since this file is automatically downloaded when needed.
Any other files were either generated or added by yourself, of which you can delete at your own discretion.