"""
A TestRunner for use with the Python unit testing framework. It generates a HTML report to show the result at a glance.

The simplest way to use this is to invoke its main method. E.g.

    import unittest
    import BSTestRunner

    ... define your tests ...

    if __name__ == '__main__':
        BSTestRunner.main()


For more customization options, instantiates a BSTestRunner object.
BSTestRunner is a counterpart to unittest's TextTestRunner. E.g.

    # output to a file
    fp = file('my_report.html', 'wb')
    runner = BSTestRunner.BSTestRunner(
                stream=fp,
                title='My unit test',
                description='This demonstrates the report output by BSTestRunner.'
                )

    # Use an external stylesheet.
    # See the Template_mixin class for more customizable options
    runner.STYLESHEET_TMPL = '<link rel="stylesheet" href="my_stylesheet.css" type="text/css">'

    # run the test
    runner.run(my_test_suite)


------------------------------------------------------------------------
Copyright (c) 2004-2007, Wai Yip Tung
Copyright (c) 2016, Eason Han
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

* Redistributions of source code must retain the above copyright notice,
  this list of conditions and the following disclaimer.
* Redistributions in binary form must reproduce the above copyright
  notice, this list of conditions and the following disclaimer in the
  documentation and/or other materials provided with the distribution.
* Neither the name Wai Yip Tung nor the names of its contributors may be
  used to endorse or promote products derived from this software without
  specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER
OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
import re

"""
Change History

Version 0.8.3
* Modify html style using bootstrap3.

Version 0.8.3
* Prevent crash on class or module-level exceptions (Darren Wurf).

Version 0.8.2
* Show output inline instead of popup window (Viorel Lupu).

Version in 0.8.1
* Validated XHTML (Wolfgang Borgert).
* Added description of test classes and test cases.

Version in 0.8.0
* Define Template_mixin class for customization.
* Workaround a IE 6 bug that it does not treat <script> block as CDATA.

Version in 0.7.1
* Back port to Python 2.3 (Frank Horowitz).
* Fix missing scroll bars in detail log (Podi).
"""
__version__ = "0.8.4"
# TODO: color stderr
# TODO: simplify javascript using ,ore than 1 class in the class attribute?
import datetime
from io import StringIO as StringIO
import sys
import unittest
from xml.sax import saxutils

# ------------------------------------------------------------------------
# The redirectors below are used to capture output during testing. Output
# sent to sys.stdout and sys.stderr are automatically captured. However
# in some cases sys.stdout is already cached before BSTestRunner is
# invoked (e.g. calling logging.basicConfig). In order to capture those
# output, use the redirectors for the cached stream.
#
# e.g.
#   >>> logging.basicConfig(stream=BSTestRunner.stdout_redirector)
#   >>>

def to_unicode(s):
    return s
    # try:
    #     return unicode(s)
    # except UnicodeDecodeError:
    #     # s is non ascii byte string
    #     return s.decode('unicode_escape')

class OutputRedirector(object):
    """ Wrapper to redirect stdout or stderr """
    def __init__(self, fp):
        self.fp = fp

    def write(self, s):
        self.fp.write(s)

    def writelines(self, lines):
        lines = map(to_unicode, lines)
        self.fp.writelines(lines)

    def flush(self):
        self.fp.flush()

stdout_redirector = OutputRedirector(sys.stdout)
stderr_redirector = OutputRedirector(sys.stderr)



# ----------------------------------------------------------------------
# Template

class Template_mixin(object):
    """
    Define a HTML template for report customerization and generation.

    Overall structure of an HTML report

    HTML
    +------------------------+
    |<html>                  |
    |  <head>                |
    |                        |
    |   STYLESHEET           |
    |   +----------------+   |
    |   |                |   |
    |   +----------------+   |
    |                        |
    |  </head>               |
    |                        |
    |  <body>                |
    |                        |
    |   HEADING              |
    |   +----------------+   |
    |   |                |   |
    |   +----------------+   |
    |                        |
    |   REPORT               |
    |   +----------------+   |
    |   |                |   |
    |   +----------------+   |
    |                        |
    |   ENDING               |
    |   +----------------+   |
    |   |                |   |
    |   +----------------+   |
    |                        |
    |  </body>               |
    |</html>                 |
    +------------------------+
    """

    STATUS = {
    0: 'pass',
    1: 'fail',
    2: 'error',
    3: 'skip'
    }

    DEFAULT_TITLE = 'Interface Test Report'
    DEFAULT_DESCRIPTION = ''

    # ------------------------------------------------------------------------
    # HTML Template

    HTML_TMPL = r"""<!DOCTYPE html>
<html lang="zh-cn">
  <head>
    <title>%(title)s</title>
    <meta name="generator" content="%(generator)s"/>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="http://cdn.bootcss.com/bootstrap/3.3.0/css/bootstrap.min.css">
    <script src="https://cdn.bootcss.com/echarts/3.8.5/echarts.common.min.js"></script>
    %(stylesheet)s
  </head>
<body>
    <script language="javascript" type="text/javascript"><!--
    output_list = Array();

    /* level - 0:Summary; 1:Failed; 2:All;3:skiped */
    function showCase(level) {
        trs = document.getElementsByTagName("tr");
        for (var i = 0; i < trs.length; i++) {
            tr = trs[i];
            id = tr.id;
            if (id.substr(0,2) == 'ft') {
                if (level < 1) {
                    tr.className = 'hiddenRow';
                }
                else {
                    tr.className = '';
                }
            }
            if (id.substr(0,2) == 'pt') {
                if (level > 1) {
                    tr.className = '';
                }
                
                else {
                    tr.className = 'hiddenRow';
                }
            }
        }
    }


function showClassDetail(cid, count) {
    var id_list = Array(count);
    var toHide = 1;
    for (var i = 0; i < count; i++) {
        tid0 = 't' + cid.substr(1) + '.' + (i+1);
        tid = 'f' + tid0;
        tr = document.getElementById(tid);
        if (!tr) {
            tid = 'p' + tid0;
            tr = document.getElementById(tid);
        }
        id_list[i] = tid;
        if (tr.className) {
            toHide = 0;
        }
    }
    for (var i = 0; i < count; i++) {
        tid = id_list[i];
        if (toHide) {
            document.getElementById('div_'+tid).style.display = 'none'
            document.getElementById(tid).className = 'hiddenRow';
        }
        else {
            document.getElementById(tid).className = '';
        }
    }
}


function showTestDetail(div_id){
    var details_div = document.getElementById(div_id)
    var displayState = details_div.style.display
    // alert(displayState)
    if (displayState != 'block' ) {
        displayState = 'block'
        details_div.style.display = 'block'
    }
    else {
        details_div.style.display = 'none'
    }
}


function html_escape(s) {
    s = s.replace(/&/g,'&amp;');
    s = s.replace(/</g,'&lt;');
    s = s.replace(/>/g,'&gt;');
    return s;
}

/* obsoleted by detail in <div>
function showOutput(id, name) {
    var w = window.open("", //url
                    name,
                    "resizable,scrollbars,status,width=800,height=450");
    d = w.document;
    d.write("<pre>");
    d.write(html_escape(output_list[id]));
    d.write("\n");
    d.write("<a href='javascript:window.close()'>close</a>\n");
    d.write("</pre>\n");
    d.close();
}
*/
    --></script>

<div class="container">
    %(heading)s
    %(report)s
    %(ending)s
    %(chart_script)s
</div>

    </body>
</html>
"""
    ECHARTS_SCRIPT = """
    <script type="text/javascript">
        // 基于准备好的dom，初始化echarts实例
        var myChart = echarts.init(document.getElementById('chart'));

        // 指定图表的配置项和数据
        var option = {
            title : {
                text: '测试执行情况',
                x:'center'
            },
            tooltip : {
                trigger: 'item',
                formatter: "{a} <br/>{b} : {c} ({d}%%)"
            },
            color: ['#95b75d', 'grey', '#b64645'],
            legend: {
                orient: 'vertical',
                left: 'left',
                data: ['通过','失败','错误']
            },
            series : [
                {
                    name: '测试执行情况',
                    type: 'pie',
                    radius : '60%%',
                    center: ['50%%', '60%%'],
                    data:[
                        {value:%(Pass)s, name:'通过'},
                        {value:%(fail)s, name:'失败'},
                        {value:%(error)s, name:'错误'}
                    ],
                    itemStyle: {
                        emphasis: {
                            shadowBlur: 10,
                            shadowOffsetX: 0,
                            shadowColor: 'rgba(0, 0, 0, 0.5)'
                        }
                    }
                }
            ]
        };

        // 使用刚指定的配置项和数据显示图表。
        myChart.setOption(option);
    </script>
    """
    STYLESHEET_TMPL = """
<style type="text/css" media="screen">

/* -- css div popup ------------------------------------------------------------------------ */
.popup_window-pass {
    display: none;
    /*border: solid #627173 1px; */
    padding: 10px;
    background-color: #1C953F;
    font-family: "Lucida Console", "Courier New", Courier, monospace;
    text-align: left;
    font-size: 10pt;
    width: 80%;
    max-width:798px;
}

.popup_window-fail {
    display: none;
    /*border: solid #627173 1px; */
    padding: 10px;
    background-color: rgb(255, 0, 0);
    font-family: "Lucida Console", "Courier New", Courier, monospace;
    text-align: left;
    font-size: 10pt;
    width: 80%;
    max-width:798px;
}

/* -- report ------------------------------------------------------------------------ */

#show_detail_line .label {
    font-size: 85%;
    cursor: pointer;
}

#show_detail_line {
    margin: 2em auto 1em auto;
}

#total_row  { font-weight: bold; }
.hiddenRow  { display: none; }
.testcase   { margin-left: 2em; }

table td {
    border: 1px solid #ccc
}

.btn-xs {   
    float: right;
    margin-right: 20px;
}
.btn-False {
    width: 42px;
    height: 22px;
    background-color: #1C953F;
    color: #fff;
    border: 0;
    line-height: 22px;
}
.btn-True {
    width: 42px;
    height: 22px;
    background-color: rgb(255, 0, 0);
    color: #fff;
    border: 0;
    line-height: 22px;
}
.btn-fail {
    width: 42px;
    height: 22px;
    background-color: rgb(227, 23, 13);
    color: #fff;
    border: 0;
    line-height: 22px;
}
.btn-pass {
    width: 42px;
    height: 22px;
    background-color: #1C953F;
    color: #fff;
    border: 0;
    line-height: 22px;
}
.btn-error {
    width: 42px;
    height: 22px;
    background-color: rgb(128, 0, 0);
    color: #fff;
    border: 0;
    line-height: 22px;
}

table th:first-child {
    width: 20%;
}
  /* -- ending ---------------------------------------------------------------------- */
    #ending {
    }
</style>
"""



    # ------------------------------------------------------------------------
    # Heading
    #

    HEADING_TMPL = """
    <div class='heading'>
        <h1><font color="#27DBE4">%(title)s</font></h1>
        <h3><font color="#FC0019">%(description)s</font></h3>
        %(parameters)s
         <div id="chart" style="width:50%%;height:400px;float:;"></div>
    </div>
   


""" # variables: (title, parameters, description)

    HEADING_ATTRIBUTE_TMPL = """<p><strong>%(name)s:</strong> %(value)s</p>
""" # variables: (name, value)



    # ------------------------------------------------------------------------
    # Report
    #

    REPORT_TMPL = """
    <div>
<div id='show_detail_line'>
<span class="label label-primary" onclick="showCase(0)">Summary</span>
<span class="label label-danger" onclick="showCase(1)">Failed+Skiped</span>
<span class="label label-default" onclick="showCase(2)">All</span>
</div>
</div>
<table id='result_table' class="table" style="border: 1px solid #ccc">
    <thead>
        <tr id='header_row' style="background-color:#5195F0">
            <th>Desc</td>
            <th>ApiName/Method</td>
            <th>Count</td>
            <th>Pass</td>
            <th>Fail</td>
            <th>Error</td>
            <th>skip</td>
            <th>View</td>
        </tr>
    </thead>
    <tbody>
        %(test_list)s
    </tbody>
    <tfoot>
        <tr id='total_row'>
            <td>Total</td>
            <td>&nbsp;</td>
            <td>%(count)s</td>
            <td bgcolor = "#1d953f" class="text text-success"><font color="Black">%(Pass)s</font></td>
            <td bgcolor = "#D75152" class="text text-danger"><font color="Black">%(fail)s</font></td>
            <td bgcolor = "#D75152" class="text text-warning"><font color="Black">%(error)s</font></td>
            <td bgcolor = "#FFFF00" class="text text-danger><font color="Black">%(skip)s</font></td>
            <td>&nbsp;</td>
            
        </tr>
    </tfoot>
</table>
""" # variables: (test_list, count, Pass, fail, error)

    REPORT_CLASS_TMPL = r"""
<tr class='%(style)s'>
    <td>%(newdesc)s</td>
    <td>%(desc)s</td>
    <td>%(count)s</td>
    <td class="text text-success">%(Pass)s</td>
    <td>%(fail)s</td>
    <td>%(error)s</td>
    <td>%(skip)s</td>
    <td><a class="btn btn-xs btn-%(show)s"href="javascript:showClassDetail('%(cid)s',%(count)s)">Detail</a></td>
</tr>
""" # variables: (style, desc, count, Pass, fail, error, cid)


    REPORT_TEST_WITH_OUTPUT_TMPL = r"""
<tr id='%(tid)s' class='%(Class)s'>
    <td class='%(style)s'><div class='testcase'>%(desc)s</div></td>
    <td colspan='7' align='center'>

    <!--css div popup start-->
    <a class="popup_link btn btn-xs btn-%(status)s" onfocus='this.blur();' href="javascript:showTestDetail('div_%(tid)s')">
        %(status)s</a>

    <div id='div_%(tid)s' class="popup_window-%(status)s">
        <div style='text-align: right;cursor:pointer'>
        <a onfocus='this.blur();' onclick="document.getElementById('div_%(tid)s').style.display = 'none'">
           <font color="White">[x]</font></a>
        </div>
        <pre>
        %(script)s
        </pre>
    </div>
    <!--css div popup end-->

    </td>
</tr>
""" # variables: (tid, Class, style, desc, status)


    REPORT_TEST_NO_OUTPUT_TMPL = r"""
<tr id='%(tid)s' class='%(Class)s'>
    <td class='%(style)s'><div class='testcase'>%(desc)s</div></td>
    <td colspan='7' align='center'>%(status)s</td>
</tr>
""" # variables: (tid, Class, style, desc, status)


    REPORT_TEST_OUTPUT_TMPL = r"""
%(id)s: %(output)s
""" # variables: (id, output)



    # ------------------------------------------------------------------------
    # ENDING
    #

    ENDING_TMPL = """<div id='ending'>&nbsp;</div>"""

# -------------------- The end of the Template class -------------------


TestResult = unittest.TestResult

class _TestResult(TestResult):
    # note: _TestResult is a pure representation of results.
    # It lacks the output and reporting ability compares to unittest._TextTestResult.
    def __init__(self, verbosity=1):
        TestResult.__init__(self)
        self.outputBuffer = StringIO()
        self.stdout0 = None
        self.stderr0 = None
        self.success_count = 0
        self.failure_count = 0
        self.error_count = 0
        self.skipped_count = 0
        self.verbosity = verbosity

        # result is a list of result in 4 tuple
        # (
        #   result code (0: success; 1: fail; 2: error),
        #   TestCase object,
        #   Test output (byte string),
        #   stack trace,
        # )
        self.result = []


    def startTest(self, test):
        TestResult.startTest(self, test)
        # just one buffer for both stdout and stderr  更改
        self.outputBuffer = StringIO()
        stdout_redirector.fp = self.outputBuffer
        stderr_redirector.fp = self.outputBuffer
        self.stdout0 = sys.stdout
        self.stderr0 = sys.stderr
        sys.stdout = stdout_redirector
        sys.stderr = stderr_redirector


    def complete_output(self):
        """
        Disconnect output redirection and return buffer.
        Safe to call multiple times.
        """
        if self.stdout0:
            sys.stdout = self.stdout0
            sys.stderr = self.stderr0
            self.stdout0 = None
            self.stderr0 = None
        return self.outputBuffer.getvalue()


    def stopTest(self, test):
        # Usually one of addSuccess, addError or addFailure would have been called.
        # But there are some path in unittest that would bypass this.
        # We must disconnect stdout in stopTest(), which is guaranteed to be called.
        self.complete_output()


    def addSuccess(self, test):
        self.success_count += 1
        TestResult.addSuccess(self, test)
        output = self.complete_output()
        self.result.append((0, test, output, ''))
        if self.verbosity > 1:
            sys.stderr.write('ok ')
            sys.stderr.write(str(test))
            sys.stderr.write('\n')
        else:
            sys.stderr.write('.')

    def addError(self, test, err):
        self.error_count += 1
        TestResult.addError(self, test, err)
        _, _exc_str = self.errors[-1]
        output = self.complete_output()
        self.result.append((2, test, output, _exc_str))
        if self.verbosity > 1:
            sys.stderr.write('E  ')
            sys.stderr.write(str(test))
            sys.stderr.write('\n')
        else:
            sys.stderr.write('E')

    def addFailure(self, test, err):
        self.failure_count += 1
        TestResult.addFailure(self, test, err)
        _, _exc_str = self.failures[-1]
        output = self.complete_output()
        self.result.append((1, test, output, _exc_str[-(len(_exc_str)-(_exc_str.index("Ass"))):]))
        if self.verbosity > 1:
            sys.stderr.write('F  ')
            sys.stderr.write(str(test))
            sys.stderr.write('\n')
        else:
            sys.stderr.write('F')

    def addSkip(self, test, reason):
        """Called when a test is skipped."""
        self.skipped_count += 1
        TestResult.addSkip(self, test, reason)
        _, _exc_str = self.skipped[-1]
        output = self.complete_output()
        self.result.append((3, test, output, _exc_str))
        if self.verbosity > 1:
            sys.stderr.write('S')
            sys.stderr.write(str(test))
            sys.stderr.write('\n')
        else:
            sys.stderr.write('S')
        self.skipped.append((test, reason))

class BSTestRunner(Template_mixin):
    """
    """
    def __init__(self, stream=sys.stdout, verbosity=1, title=None, description=None):
        self.stream = stream
        self.verbosity = verbosity
        if title is None:
            self.title = self.DEFAULT_TITLE
        else:
            self.title = title
        if description is None:
            self.description = self.DEFAULT_DESCRIPTION
        else:
            self.description = description

        self.startTime = datetime.datetime.now()

    def run(self, test):
        "Run the given test case or test suite."
        result = _TestResult(self.verbosity)
        try:
            test(result)
        except TypeError:
            pass
        self.stopTime = datetime.datetime.now()
        self.generateReport(test, result)
        return result


    def sortResult(self, result_list):
        # unittest does not seems to run in any particular order.
        # Here at least we want to group them together by class.
        rmap = {}
        classes = []
        for n,t,o,e in result_list:
            cls = t.__class__
            if not cls in rmap:
                rmap[cls] = []
                classes.append(cls)
            rmap[cls].append((n,t,o,e))
        r = [(cls, rmap[cls]) for cls in classes]
        return r


    def getReportAttributes(self, result):
        """
        Return report attributes as a list of (name, value).
        Override this to add custom attributes.
        """
        startTime = str(self.startTime)[:19]
        duration = str(self.stopTime - self.startTime)
        status = []
        if result.success_count: status.append('<span class="text text-success">Pass <strong>%s</strong></span>'    % result.success_count)
        if result.failure_count: status.append('<span class="text text-danger">Failure <strong>%s</strong></span>' % result.failure_count)
        if result.error_count: status.append('<span class="text text-warning">Error <strong>%s</strong></span>' % result.error_count)
        if result.skipped_count: status.append('<span class="text text-warning">skip <strong>%s</strong></span>' % result.skipped_count)
        if status:
            status = ' '.join(status)
        else:
            status = 'none'
        return [
            ('开始时间', startTime),
            ('总共耗时', duration),
            ('测试结果', status),
        ]


    def generateReport(self, test, result):
        report_attrs = self.getReportAttributes(result)
        generator = 'BSTestRunner %s' % __version__
        stylesheet = self._generate_stylesheet()
        heading = self._generate_heading(report_attrs)
        report = self._generate_report(result)
        ending = self._generate_ending()
        chart = self._generate_chart(result)
        output = self.HTML_TMPL % dict(
            title=saxutils.escape(self.title),
            generator=generator,
            stylesheet=stylesheet,
            heading=heading,
            report=report,
            ending=ending,
            chart_script=chart
        )
        self.stream.write(output.encode('utf8'))


    def _generate_stylesheet(self):
        return self.STYLESHEET_TMPL


    def _generate_heading(self, report_attrs):
        a_lines = []
        for name, value in report_attrs:
            line = self.HEADING_ATTRIBUTE_TMPL % dict(
                    name = saxutils.escape(name),####更改
                    # value = saxutils.escape(value),

                    value = value,
                )
            a_lines.append(line)
        heading = self.HEADING_TMPL % dict(
            title = saxutils.escape(self.title),
            parameters = ''.join(a_lines),
            description = saxutils.escape(self.description),
        )
        return heading


    def _generate_report(self, result):
        rows = []
        sortedResult = self.sortResult(result.result)
        for cid, (cls, cls_results) in enumerate(sortedResult):
            # subtotal for a class
            np = nf = ne = nk = 0
            for n, t, o, e in cls_results:
                if n == 0:
                    np += 1
                elif n == 1:
                    nf += 1
                elif n == 2:
                    ne += 1
                else:
                    nk += 1
            # format class description
            if cls.__module__ == "__main__":
                name = cls.__name__
            else:
                name = "%s" % (cls.__name__)
            if "，" in cls.__doc__:
                doc = cls.__doc__ and cls.__doc__.split("，")[0] or ""
                newdoc = cls.__doc__.split("，")[1] or ""
            else:
                doc = cls.__doc__ and cls.__doc__.split(",")[0] or ""
                newdoc = cls.__doc__.split(",")[1] or ""
            if '新字段' in str(cls_results):
                desc = doc + '--有新字段'
            else:
                desc = doc

            row = self.REPORT_CLASS_TMPL % dict(
                style=ne > 0 and 'text text-warning' or nf > 0 and 'text text-danger' or np>0 and 'text text-success',
                newdesc=newdoc,
                desc=desc,
                count=np+nf+ne+nk,
                Pass=np,
                fail=nf,
                error=ne,
                skip=nk,
                cid='c%s' % (cid+1),
                show=nf > 0 or ne > 0 or nk > 0,
            )
            rows.append(row)

            for tid, (n, t, o, e) in enumerate(cls_results):
                self._generate_report_test(rows, cid, tid, n, t, o, e)

        report = self.REPORT_TMPL % dict(
            test_list=''.join(rows),
            count=str(result.success_count+result.failure_count+result.error_count+result.skipped_count),
            Pass=str(result.success_count),
            fail=str(result.failure_count),
            error=str(result.error_count),
            skip=str(result.skipped_count)
        )
        return report


    def _generate_chart(self, result):
        chart = self.ECHARTS_SCRIPT % dict(
            Pass=str(result.success_count),
            fail=str(result.failure_count),
            error=str(result.error_count),
        )
        return chart
    def _generate_report_test(self, rows, cid, tid, n, t, o, e):
        # e.g. 'pt1.1', 'ft1.1', etc
        o1 = re.search('\s[\u4e00-\u9fa5].+\n',o).group()
        has_output = bool(o or e)
        tid = (n == 0 and 'p' or 'f' or 's') + 't%s.%s' % (cid+1,tid+1)
        name = t.id().split('.')[-1]
        doc = t.shortDescription() or ""
        desc = doc and ('%s: %s' % (o1, doc)) or o1
        tmpl = has_output and self.REPORT_TEST_WITH_OUTPUT_TMPL or self.REPORT_TEST_NO_OUTPUT_TMPL

        # o and e should be byte string because they are collected from stdout and stderr?
        if isinstance(o,str):
            # TODO: some problem with 'string_escape': it escape \n and mess up formating
            # uo = unicode(o.encode('string_escape'))
            uo = o
        else:
            uo = o
        if isinstance(e,str):
            # TODO: some problem with 'string_escape': it escape \n and mess up formating
            # ue = unicode(e.encode('string_escape'))
            ue = e
        else:
            ue = e

        script = self.REPORT_TEST_OUTPUT_TMPL % dict(
            id = tid,
            output = saxutils.escape(uo+ue),
        )

        row = tmpl % dict(
            tid = tid,
            Class = (n == 0 and 'hiddenRow' or 'none'),
            # Class = (n == 0 and 'hiddenRow' or 'text text-success'),
            # style = n == 2 and 'errorCase' or (n == 1 and 'failCase' or 'none'),
            style=n == 2 and 'text text-warning' or (n == 3 and 'text text-warning') or (n == 1 and 'text text-danger' or 'text text-success'),
            desc=desc,
            script=script,
            status=self.STATUS[n],
        )
        rows.append(row)
        if not has_output:
            return

    def _generate_ending(self):
        return self.ENDING_TMPL


##############################################################################
# Facilities for running tests from the command line
##############################################################################

# Note: Reuse unittest.TestProgram to launch test. In the future we may
# build our own launcher to support more specific command line
# parameters like test title, CSS, etc.
class TestProgram(unittest.TestProgram):
    """
    A variation of the unittest.TestProgram. Please refer to the base
    class for command line parameters.
    """
    def runTests(self):
        # Pick BSTestRunner as the default test runner.
        # base class's testRunner parameter is not useful because it means
        # we have to instantiate BSTestRunner before we know self.verbosity.
        if self.testRunner is None:
            self.testRunner = BSTestRunner(verbosity=self.verbosity)
        unittest.TestProgram.runTests(self)

main = TestProgram

##############################################################################
# Executing this module from the command line
##############################################################################

if __name__ == "__main__":
    main(module=None)
