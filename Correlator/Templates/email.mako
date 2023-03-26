## Define HTML email content for all severities

<%def name="html_email(severity, description, detail)">
<html>
<head>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link
      href="https://fonts.googleapis.com/css2?family=Readex+Pro&display=swap"
      rel="stylesheet"
    />

	<title>HTML Email</title>
	<style>
    	body {
            font-family: "Readex Pro", sans-serif;
            font-size: 150%;
            margin: 0;
        }
        hr {
            margin-top: 10px;
            margin-bottom: 10px;
        }
        .notice {
            color: green;
        }
        .warning{
            color: yellow;
        }
        .error{
            color: red;
        }
		table.datatable {
			border-style: none;
			border-collapse: collapse;
			padding: 10px;
		}
		table.datatable th {
			padding: 10px;
			background: #f0f0f0;
			color: #313030;
		}
		table.datatable td:first-child {
			text-align: right;
			padding: 10px;
			background: #ffffff;
			color: #313030;
            font-weight: bold;
		}
		table.datatable td {
			text-align: left;
			padding: 10px;
			background: #ffffff;
			color: #313030;
		}
	</style>
</head>
<body>
<p>Hello</p>
<p>This is a automated notification. Please do not reply, as this email address is not monitored.</p>
<p>The notification severity is: <span class="${severity}">${description}</span>.</p>
<hr />
<p><strong>${summary}</strong></p>
${detail}
<hr />
<p>This email was generated by <a href="https://github.com/timmy-bbb/Correlator">Correlator ${version}</a></p>
</body>
</html>
</%def>

## Define text email content for all severities

<%def name="text_email(severity, description, detail)">
Hello

This is an automated notification. Please do not reply, as this email address is not monitored.

The notification severity is: ${description}.

--------------------------------------------------------

${summary}

${detail}

--------------------------------------------------------

This email was generated by Correlator ${version}. https://github.com/timmy-bbb/Correlator
</%def>

## Handle 'notice' severity

<%def name="notice_html()">
${html_email(severity='notice', description='Informational', detail=html_detail)}
</%def>

<%def name="notice_subject()">Notice: ${summary}</%def>

<%def name="notice_text()">
${text_email(severity='notice', description='Informational', detail=text_detail)}
</%def>

## Handle 'warn' severity

<%def name="warn_html()">
${html_email(severity='warn', description='Warning', detail=html_detail)}
</%def>

<%def name="warn_subject()">Warning: ${summary}</%def>

<%def name="warn_text()">
${text_email(severity='warn', description='Warning', detail=text_detail)}
</%def>

## Handle 'error' severity

<%def name="error_html()">
${html_email(severity='error',description='Error', detail=html_detail)}
</%def>

<%def name="error_subject()">Error: ${summary}</%def>

<%def name="error_text()">
${text_email(severity='warn',description='Error', detail=text_detail)}
</%def>
