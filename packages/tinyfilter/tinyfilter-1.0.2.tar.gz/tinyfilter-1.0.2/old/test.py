from ascii_magic import AsciiArt

my_art = AsciiArt.from_image('art.png')
my_art.to_terminal(columns=80, monochrome=True)

