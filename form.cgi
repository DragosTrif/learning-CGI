#!/usr/bin/perl -wT

use strict;

use CGI qw/:standard/;

print header,
start_html('Hello'),
start_form,
"Enter your name: ",textfield('name'),
submit,
end_form,
hr;

if (param()) {
	print "Hello ",
	param('name'),
	p;
}
end_html;
