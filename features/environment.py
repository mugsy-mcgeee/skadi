import os

def before_all(ctx):
	ctx.env = os.environ.copy()
	root = os.path.join(os.path.dirname(__file__), '..')
	ctx.env['SKADI_ROOT'] = root
