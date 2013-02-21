import os, subprocess

from subprocess import Popen

@given(u'"skadi" is in PATH')
def impl(ctx):
    bindir = os.path.join(ctx.env['SKADI_ROOT'], 'bin')
    ctx.env['PATH'] = ('%s:' % bindir) + ctx.env['PATH']
    assert bindir in ctx.env['PATH']

@when(u'I issue the following command from the project root')
def impl(ctx):
    process = Popen(
        ctx.text,
        stdout=subprocess.PIPE, env=ctx.env, shell=True
    )
    ctx.stdout, ctx.status = process.communicate()
    assert ctx.stdout is not None

@then(u'the output should contain the following sections')
def impl(ctx):
    lines = ctx.stdout.splitlines()
    for row in ctx.table:
        assert row['Section'] in lines