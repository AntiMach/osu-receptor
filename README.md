# Solving osu!mania streching skin issues
Skip [here](#skip) to learn how to actually use this.

## What I figured out
Everything in game is based on the height of 480px, and sizing some elements is based on a ratio of 1.6.

## Ingame
- Receptors are downscaled by a factor of 1.6, then stretched to match the `ColumnWidth` (value on the `skin.ini` file).
- Note parts are just scaled to the column's width, maintaining their aspect ratio.

This is why receptors are sometimes stretched, while notes and long notes are not.
And it was a pain to figure out why, and also figure out a way to fix it.

So what I did to fix it, which involved uniform square images for every component, was the following:

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

## And how can I do all of this?
You could use some image editing software, or you can use my python script along with it's customizable skin properties text file to make your own skin.

# <a id="skip"></a> Editing your skin
Before anything, make sure to clone this repository as your skin folder, from where you should be working with.
The repository itself works as a skin, but its files can be easily placed inside any other osu skin.
Your skin should have these files and folders:
```
SkinFolder/
    osu_receptor/
        ...
    src-[skinname]/
        skin.txt
        ...
    blank.png
    osu_receptor.bat
    ...
```
These files and folders are important, the rest is added by the script or by yourself.
`[skinname]` is the name of you osu!receptor noteskin.

## The skin.ini
The good old `skin.ini` can be created here for non `[Mania]` section settings. Any of those will be replaced by the generated key layouts from the program.

## The skin.txt
This is a sequence of commands for creating skin elements automatically, including scaling images and defining some skin properties.

## Notefield settings
```
settings [hide marvelous] [center] [screen ratio] {
    ...
    extra config lines
    ...
}
```
- `[hidden marvelous : yes/no]`: If the marvelous judgement should be hidden.
- `[center : yes/no]`: If the note field should be centered or not.
- `[screen ratio : expr]`: An expression representing the screen ratio you're playing at. Usual value is `16:9`.
- `<extra config lines : text>`: Optional. Any extra config lines you consider necessary to add to every generated key layout.

## Set component types
`component [name] [type] [redirect]`
- `[name : option]`: Name of the component to set. Can be `note`, `hold-head`, `hold-body`, `hold-tail`, `receptor-up` or `receptor-down`.
- `[type : option]`: Type of the component to set. Can be:
- - `variable`: Has various forms (eg. arrow directions), will apply the column's layout value as a suffix.
- - `static`: Is always the same regardless of the column's layout value.
- - `redirect`: Will make use of another component's values and images as its own.
- `[redirect : option] ([type] = redirect)`: The component to redirect to.

## Create key layouts
`keys [keys] [receptor width] [spacing] [hit position] [transparency] [layout]`
- `[keys : 1-9]`: The number of keys for this key layout.
- `[receptor width : 0-100]`: The receptor's width.
- `[spacing : 0-100]`: The spacing between receptors.
- `[hit position : 0-240]`: The offset relative to the bottom of the screen of where notes are hit.
- `[transparency : 0-255]` : The transparency of each column.
- NOTE: the values for the `receptor width` and `spacing` options should add up to a value between `0` and `100`

## Src-skin file names
Files in the `src-[skinname]` folder should have specific names, and should only include the needed images and `skin.txt` files.

Each image should be named:
- `[name][layout col].png` for `variable` type components, where `[name]` is one of the names from the set command, and `[layout col]` is a character telling where it lands in the `[layout]` for each key layout.
- `[name].png` for `static` type components, where `[name]` is one of the names from the set command.
- `redirect` type components use an existing file as its own.

## Finishing the skin
Finally, to edit the `skin.ini` file that recognises the created files as part of the skin, all you have to do is run `osu_receptor.bat` with python 3.9 or higher installed. But watch out, this will edit the current `skin.ini` in your skin and may delete previous `[Mania]` settings. Anything that isn't a `[Mania]` section should stay the same, but if you're scared of loosing any settings, <b>please make a backup of your `skin.ini`</b>.

## Cleaning up
If you want to cleanup the skin's files for sharing, you can get rid of the following files/folders:
```
osu_receptor\
    ...
src-[skinname]\
    ...
osu_receptor.bat
```
However, doing this will get rid of every file needed to adjust the skin.
Any other files were either generated or added by yourself, of which you can delete at your own discretion.

## <a id="downloads"></a> Using a pre-made skin
If you just want to use a mania skin, you can download them here:
- [Circle Skin](https://github.com/AntiMach/osu-receptor/releases/tag/circles)
- [Arrow Skin (pl0x&chordxx style)](https://github.com/AntiMach/osu-receptor/releases/tag/arrows)

These are just my preferences, you may change anything if you feel like changing
Install it and enjoy!