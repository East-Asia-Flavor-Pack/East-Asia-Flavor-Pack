     example_progress_bar5 = {
        name = "PROGRESS_BAR_NAME1"
        desc = "PROGRESS_BAR_TEXT3" #This will be printed on the left side of the progress bar
       second_desc = "PROGRESS_BAR_TEXT3" #This will be printed on the right side of the progress bar

        is_inverted = yes #Will treat negative progress as positive meaning that the object is to keep this progress down

        start_value = 50
        min_value = 0 #Can also be a script value or math block, evaluated in the journal entry's scope whenever the bar is clamped or shown
        max_value = 100 #Can also be a script value or math block, evaluated in the journal entry's scope whenever the bar is clamped or shown

       # Use one of these ready-made looks:
        default = yes
        default_green = yes
        default_bad = yes

       These progress bar weekly/monthly/yearly progress updates executes before the weekly/monthly/yearly JE pulses
        weekly_progress = {
            add = {
                desc = "PROGRESS_BAR_ADD_WEEKLY_DESC2"
                value = 30
            }
        }
        monthly_progress = {
            progress_condition = {
                limit = {
                    influence > 100
                }
                add = {
                    desc = "PROGRESS_BAR_ADD_MONTHLY_DESC1"
                    value = 3
                }
                else = {
                    limit = {
                        influence > 50
                    }
                    add = {
                        desc = "PROGRESS_BAR_ADD_MONTHLY_DESC2"
                        value = 1
                    }
                }
            }
        }
        yearly_progress = {
        }
     }

     progress_condition works like if - its body counts towards the bar only while its limit holds, and
     an else inside it takes over when the limit fails, chained as deep as you need.

     The difference is the journal entry panel. It builds the Advance and Retreat lists straight from
     these progress values, and it lists a progress_condition whose limit currently fails as well -
     ticked when it holds, an empty box when it does not - so the player can see what is left to do.
     A plain if is invisible to that list, so write factors the player should know about as
     progress_condition and keep if for arithmetic they should not see.

     A factor only appears in the list if it carries a desc. Factors that come from a named script value
     are counted but not listed, since the condition lives outside the bar.

     Do not put format = inside a progress_condition. The list styles a failing branch by overriding the
     bar's format key, and a format written on the factor itself wins over that, so the entry would lose
     its empty box and read as if the condition held.

     The look of the bar is defined here as well. Set any of the keys below and the bar uses them
     instead of one of the ready-made looks above:

     example_progress_bar6 = {
        name = "PROGRESS_BAR_NAME1"
        desc = "PROGRESS_BAR_TEXT3"
        second_desc = "PROGRESS_BAR_TEXT4"

        progress_texture = "gfx/interface/progressbar/progressbar_bad.dds" #the filled part of the bar
        background_texture = "gfx/interface/progressbar/progressbar_gold.dds" #the part the fill has not reached yet
        glow_texture = "gfx/interface/progressbar/progressbar_bad_glow.dds" #the glow at the leading edge of the fill
        glow_line_texture = "gfx/interface/progressbar/progressbar_bad_glow_line.dds" #the line inside that glow
        color = { 1 1 1 1 } #tints the whole bar, glow included - use it with the neutral progressbar_white art
        marker = yes #shows the sliding marker on top of the bar, for bars read as "how far between two poles"
        left_icon = "gfx/interface/progressbar/tokugawa_marker.dds" #icon before the bar, journal entry panel only
        right_icon = "gfx/interface/progressbar/qing_dynasty_marker.dds" #icon after the bar, journal entry panel only

        start_value = 0
        min_value = -40
        max_value = 40
     }

     Every key is optional. Textures left out fall back to the default blue bar and its glow, and a
     bar with no icons gets the full panel width. The bar textures come in matching sets named
     progressbar_<colour>.dds, progressbar_<colour>_glow.dds and progressbar_<colour>_glow_line.dds -
     pick all three from the same set unless you want them to differ on purpose.

     color tints whatever the bar actually draws, in one pass: the fill, its glow and the background
     side all take the same tint. Two things follow from that. A bar whose two sides need different
     colours gets them from progress_texture and background_texture and leaves color alone. And a
     bar with no background_texture has nothing to tint on the unfilled side - it stays the empty
     bar art - so set background_texture as well if you want the whole bar coloured.
