#!/usr/bin/perl -wT

use strict;

use CGI;

my $cgi = CGI->new;

print $cgi->header;
print $cgi->start_html('HELLO WORLD');
print $cgi->h1('Hello World');
print $cgi->end_html;
