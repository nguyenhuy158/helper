"""Verbosity handling for CLI commands."""
import logging
import click


class VerbosityCommand(click.Command):
    """Custom click.Command that handles verbosity flags."""

    def parse_args(self, ctx, args):
        # Initialize verbosity from context if it exists
        ctx.ensure_object(dict)
        verbose = ctx.obj.get("verbosity", 0)

        # Process args for verbosity flags
        new_args = []
        i = 0
        while i < len(args):
            arg = args[i]
            if arg == "--verbose":
                verbose += 1
            elif arg.startswith("-"):
                verbose += arg.count("v")
            else:
                new_args.append(arg)
            i += 1

        # Update verbosity in context
        ctx.obj["verbosity"] = verbose

        # Set up logging
        self._setup_logging(verbose)

        # Continue with normal argument parsing
        return super().parse_args(ctx, new_args)

    def _setup_logging(self, verbose):
        """Configure logging based on verbosity level.
        
        Args:
            verbose (int): Verbosity level (0-3)
        """
        logger = logging.getLogger("docker-helper")
        if verbose >= 3:
            logger.setLevel(logging.DEBUG)
        elif verbose == 2:
            logger.setLevel(logging.INFO)
        elif verbose == 1:
            logger.setLevel(logging.WARNING)
        else:
            logger.setLevel(logging.ERROR)


class VerbosityGroup(click.Group):
    """Custom click.Group that handles verbosity flags for command groups."""

    def make_context(self, info_name, args, parent=None, **extra):
        # Pre-process args to find verbosity flags
        verbose = 0
        processed_args = []

        for arg in args:
            if arg == "--verbose":
                verbose += 1
            elif arg.startswith("-"):
                verbose += arg.count("v")
            else:
                processed_args.append(arg)

        # Create context with processed args
        ctx = super().make_context(info_name, processed_args, parent=parent, **extra)

        # Set verbosity in context
        ctx.ensure_object(dict)
        ctx.obj["verbosity"] = verbose

        # Set up logging
        logger = logging.getLogger("docker-helper")
        if verbose >= 3:
            logger.setLevel(logging.DEBUG)
        elif verbose == 2:
            logger.setLevel(logging.INFO)
        elif verbose == 1:
            logger.setLevel(logging.WARNING)
        else:
            logger.setLevel(logging.ERROR)

        return ctx
