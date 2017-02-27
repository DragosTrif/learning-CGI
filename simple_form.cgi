#!/usr/bin/perl -wT

use strict;

use CGI qw/:standard/;

print header;
print "<html><head><title>Are you old enough to vote?</title></head>\n";
print "<body>\n";
print "<h1>Are you old enough to vote?</h1>\n";
print "<p>\n";
print "<form action='voter_age.cgi' method='post'>\n";
print "Age: <input type='text' name='age'>\n";
print "<input type='submit'>\n";
print "</form>\n";
print "</p></body></html>\n"
