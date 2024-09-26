"""Display results from running the execexam tool."""

from typing import Any, Dict, List, Optional, Iterable

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.layout import Layout
from rich import print

from . import enumerations


def make_colon_separated_string(arguments: Dict[str, Any]):
    """Make a colon separated string from a dictionary."""
    return "\n" + "".join(
        [f"- {key}: {value}\n" for key, value in arguments.items()]
    )


def get_display_return_code(return_code: int, fancy: bool) -> str:
    """Determine the return code from running the specified checks(s)."""
    message = "\n"
    # no errors were found in the executable examination
    if return_code == 0:
        message += "[green]\u2714 All checks passed."
    # there was an error in the executable examination
    else:
        message += "[red]\u2718 One or more checks failed."
    if fancy:
        message += "\n"
    return message


def display_advice(return_code: int) -> str:
    """Determine the return code from running the specified checks(s)."""
    message = "\n"
    # no errors were found in the executable examination
    # and no advice is needed, so display helpful message
    if return_code == 0:
        message += "[green]\u2714 Advise requested, but none is needed!"
    # there was an error in the executable examination;
    # note that this is not going to be normally displayed
    else:
        message += "[red]\u2718 Advise requested, and will be provided!"
    # add an extra newline to ensure suitable spacing;
    # note that this is always done and thus there is
    # no need to know whether or not fancy output needed
    message += "\n"
    return message


def display_content(  # noqa: PLR0913
    console: Console,
    display_report_type: enumerations.ReportType,
    report_types: Optional[List[enumerations.ReportType]],
    content: str,
    label: str,
    richtext: bool,
    syntax: bool,
    syntax_theme: str = "ansi_dark",
    syntax_language: str = "python",
    newline: bool = False,
) -> None:
    """Display a diagnostic message using rich or plain text."""
    if report_types is not None and (
        display_report_type in report_types
        or enumerations.ReportType.all in report_types
    ):
        # rich text was chosen and thus the message
        # should appear in a panel with a title
        if richtext:
            # add an extra newline in the output
            # to separate this block for a prior one;
            # only needed when using rich text
            if newline:
                console.print()
            # use rich to print highlighted
            # source code in a formatted box
            if syntax:
                source_code_syntax = Syntax(
                    "\n" + content,
                    syntax_language,
                    theme=syntax_theme,
                )
                console.print(
                    Panel(
                        source_code_syntax,
                        expand=False,
                        title=label,
                    )
                )
            # use rich to print sylized text since
            # the content is not source code
            # that should be syntax highlighted
            else:
                console.print(
                    Panel(
                        content,
                        expand=False,
                        title=label,
                        highlight=True,
                    )
                )
        # plain text was chosen but the content is
        # source code and thus syntax highlighting
        # is needed, even without the panel box
        elif not richtext and syntax:
            source_code_syntax = Syntax(
                "\n" + content,
                syntax_language,
                theme=syntax_theme,
            )
            console.print(f"{label}")
            console.print(source_code_syntax)
        # plain text was chosen and the content is
        # not source code and thus no syntax highlighting
        # is needed and there is no panel box either
        else:
            console.print(f"{label}\n{content}")


def create_layout()  -> Layout:
    """Create a layout to organize data displayed in the terminal using the rich package."""
    # creates a Layout object
    layout = Layout()

    # splits the layout into 5 rows
    layout.split_column(
        Layout(name="Test Trace"),
        Layout(name="Parameters/Failing Test"),
        Layout(name="Test Failure(s)"),
        Layout(name="Advice Status/Overall Status"),
        Layout(name="Debugging Information")
    )

    # splits the second row into 2 columns
    layout["Parameters/Failing Test"].split_row(
        Layout(name="Parameters"),
        Layout(name="Failing Test")
    )

    # splits the fourth row into 2 columns
    layout["Advice Status/Overall Status"].split_row(
        Layout(name="Advice Status"),
        Layout(name="Overall Status")
    )

    # returns the layout created
    return layout

def update_layout(  # noqa: PLR0913
    content_func: Iterable,
    layout: Layout,
    console: Console,
    display_report_type: enumerations.ReportType,
    report_types: Optional[List[enumerations.ReportType]],
    content: str,
    label: str,
    richtext: bool,
    syntax: bool,
    syntax_theme: str = "ansi_dark",
    syntax_language: str = "python",
    newline: bool = False,
)  -> None:
    """Update the layout to include content that needs displayed."""
    # updates parameter information block in the layout if specified
    if label.equals("Parameter Information"):
        layout["Parameters"].update(
            content_func(console,
                         display_report_type,
                         report_types,
                         content,
                         label,
                         richtext,
                         syntax,
                         syntax_theme,
                         syntax_language,
                         newline)
        )

    # updates to inform there is no parameter information if not specified
    else:
        layout["Parameters"].update("No parameter information to be displayed.")

    # updates test trace block in the layout if specified
    if label.equals("Test Trace"):
        layout["Test Trace"].update(
            content_func(console,
                         display_report_type,
                         report_types,
                         content,
                         label,
                         richtext,
                         syntax,
                         syntax_theme,
                         syntax_language,
                         newline)
        )

    # updates to inform there is no test tracing information if not specified
    else:
        layout["Test Trace"].update("No test tracing to be displayed.")

    # updates test failure block in the layout if specified
    if label.equals("Test Failure(s)"):
        layout["Test Failure(s)"].update(
            content_func(console,
                         display_report_type,
                         report_types,
                         content,
                         label,
                         richtext,
                         syntax,
                         syntax_theme,
                         syntax_language,
                         newline)
        )

    # updates to inform there is no test failure information if not specified
    else:
        layout["Test Failure(s)"].update("No test failures to be displayed.")

    # updates failing test block in the layout if specified
    if label.equals("Failing Test"):
        layout["Failing Test"].update(
            content_func(console,
                         display_report_type,
                         report_types,
                         content,
                         label,
                         richtext,
                         syntax,
                         syntax_theme,
                         syntax_language,
                         newline)
        )

    # updates to inform there is no failing test information if not specified
    else:
        layout["Failing Test"].update("No failing tests to be displayed")

    # updates advice status block in the layout if specified
    if label.equals("Advice Status"):
        layout["Advice Status"].update(
            content_func(console,
                         display_report_type,
                         report_types,
                         content,
                         label,
                         richtext,
                         syntax,
                         syntax_theme,
                         syntax_language,
                         newline)
        )

    # updates to inform there is no advice status information if not specified
    else:
        layout["Advice Status"].update("No advice status information to be displayed.")

    # updates debugging information block in the layout if specified
    if label.equals("Debugging Information"):
        layout["Debugging Information"].update(
            content_func(console,
                         display_report_type,
                         report_types,
                         content,
                         label,
                         richtext,
                         syntax,
                         syntax_theme,
                         syntax_language,
                         newline)
        )

    # updates to inform there is no debugging information if not specified
    else:
        layout["Debugging Information"].update("No debugging information to be displayed.")

    # updates overall status block in the layout if specified
    if label.equals("Overall Status"):
        layout["Overall Status"].update(
            content_func(console,
                         display_report_type,
                         report_types,
                         content,
                         label,
                         richtext,
                         syntax,
                         syntax_theme,
                         syntax_language,
                         newline)
        )

    # updates to inform there is no overall status information if not specified
    else:
        layout["Overall Status"].update("No overall status information to be displayed.")

    # prints the updated layout to the terminal
    print(layout)
