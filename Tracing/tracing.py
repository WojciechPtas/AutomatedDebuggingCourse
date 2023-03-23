from debuggingbook.Intro_Debugging import remove_html_markup
from debuggingbook.Tracer import EventTracer

with EventTracer(condition='line == 223 or len(out) >= 6'):
 remove_html_markup('<b>foo</b>bar')