import logging

from yaxp import xpath as xp

import mock

log = logging.getLogger(__name__)


def test_summary(simple, summary, config):
    config['inline_refs'] = "short"
    pages = mock.render([simple, summary], config)
    summary = pages["summary.md"]
    log.debug(summary)

    # first in test glossary
    a = xp.a(href="../simple.md#test_first_defs_0",
             text="first")
    dl = xp.dl(_class="mkdocs-ezglossary-summary", _id="test")
    dl = dl.has(xp.dt().has(a))
    assert len(summary.xpath(str(dl))) == 1

    l1 = xp.a(href="../simple.md#test_first_refs_0")
    dl = xp.dl(_class="mkdocs-ezglossary-summary", _id="test")
    dl = dl.has(xp.dl().has(a))
    assert len(summary.xpath(str(dl))) == 0

    a = xp.a(href="../simple.md#test_third_defs_0",
             text="third")
    dd = xp.dd()
    l1 = xp.ul().li().a(href="../simple.md#test_third_refs_0",
                        text="Hello")
    l2 = xp.ul().li().a(href="../summary.md#test_third_refs_1",
                        text="Summary")
    dd = dd.has(l1)
    dd = dd.has(l2)
    dl = xp.dl(_class="mkdocs-ezglossary-summary", _id="test")
    dl = dl.has(xp.dt().has(a))
    dl = dl.has(dd)
    assert len(summary.xpath(str(dl))) == 1

    a = xp.a(href="../simple.md#demo_first_defs_0",
             text="first")
    dl = xp.dl(_class="mkdocs-ezglossary-summary", _id="demo")
    dl = dl.has(xp.dt().has(a))
    assert len(summary.xpath(str(dl))) == 1

    a = xp.a(href="../simple.md#demo_third_defs_0",
             text="third")
    dl = xp.dl(_class="mkdocs-ezglossary-summary", _id="demo")
    dl = dl.has(xp.dt().has(a))
    assert len(summary.xpath(str(dl))) == 1

    a = xp.a(href="../simple.md#demo_third_refs_0",
             text="third")
    dl = xp.dl(_class="mkdocs-ezglossary-summary", _id="demo")
    dl = dl.has(xp.dd().has(a))
    assert len(summary.xpath(str(dl))) == 0


def test_summary_noref(simple, summary, config):
    config['list_references'] = False
    pages = mock.render([simple, summary], config)
    summary = pages["summary.md"]

    a = xp.a(href="../simple.md#test_first_defs_0",
             text="first")
    dl = xp.dl(_class="mkdocs-ezglossary-summary", _id="test")
    dl = dl.has(xp.dt().has(a))
    assert len(summary.xpath(str(dl))) == 1

    a = xp.a(href="../simple.md#test_third_refs_0",
             text="Hello")
    dl = xp.dl(_class="mkdocs-ezglossary-summary", _id="test")
    dl = dl.has(xp.dt(text="third"))
    dl = dl.has(xp.dd().has(a))
    assert len(summary.xpath(str(dl))) == 0


def test_custom_summary(simple, summary, config):
    config['templates'] = "tests/custom"
    pages = mock.render([simple, summary], config)
    summary = pages["summary.md"]

    dd = xp.dd().ul().li().a(href="../simple.md#test_third_refs_0",
                             text="Hello")
    dl = xp.dl(_class="custom-summary", _id="test")
    dl = dl.has(xp.dt(text="third"))
    dl = dl.has(dd)
    assert len(summary.xpath(str(dl))) == 1


def test_default_summary(simple, summary, config):
    config['use_default'] = True
    pages = mock.render([simple, summary], config)
    summary = pages["summary.md"]
    log.debug(summary)

    a = xp.a(href="../simple.md#__default_defs_0",
             text="default")
    dl = xp.dl(_class="mkdocs-ezglossary-summary", _id="_")
    dl = dl.has(xp.dt().has(a))
    assert len(summary.xpath(str(dl))) == 1


def test_summary_table(simple, tablesummary, config):
    pages = mock.render([simple, tablesummary], config)
    summary = pages["tablesummary.md"]
    log.debug(summary)

    table = xp.div().table()
    table.has(xp.th().has(xp.td(text="Term"))
                .has(xp.td(text="Definition"))
                .has(xp.td(text="References")))
    tr = xp.div().table(_class="mkdocs-ezglossary-summary", _id="demo").tr()
    tr = tr.has(xp.td(text="default"))
    tr = tr.has(xp.ul().li().a(href="../simple.md#__default_defs_0",
                               text="Hello"))
    table.has(tr)
    assert len(summary.xpath(str(table))) == 1
