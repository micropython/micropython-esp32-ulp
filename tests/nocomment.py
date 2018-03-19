from esp32_ulp.nocomment import remove_comments

ORIG = """\
/*
 * HEADER
 */

# single, full line comment

label:  // another rest-of-line comment

        nop     /* partial line */

        .string "try confusing /* with a comment start"
        .string "should be there 1"  /* another comment */
        .string 'try confusing */ with a comment end'

        .string "more confusing \\" /* should be there 2"
        /* comment */
        .string 'more confusing \\' */'

/***** FOOTER *****/
"""

EXPECTED = """\






label:

	nop

	.string "try confusing /* with a comment start"
	.string "should be there 1"
	.string 'try confusing */ with a comment end'

	.string "more confusing \\" /* should be there 2"

	.string 'more confusing \\' */'


"""


def test_remove_comments():
    lines_orig = ORIG.splitlines()
    len_orig = len(lines_orig)
    lines_expected = EXPECTED.splitlines()
    len_expected = len(lines_expected)
    lines_got = remove_comments(ORIG)
    len_got = len(lines_got)
    assert len_orig == len_expected == len_got, \
           "line count differs %d %d %d" % (len_orig, len_expected, len_got)
    assert lines_expected == lines_got, "texts differ"


test_remove_comments()
